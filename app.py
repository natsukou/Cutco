from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, redirect, render_template, request, send_file, url_for

from mvp_platform import config, criteria_stage, qa_stage, store


app = Flask(__name__)
config.ensure_base_dirs()


# ---- Jinja Filters ----

STATUS_CLASS_MAP = {
    "intake": "running",
    "criteria_ready": "running",
    "approved_for_demo": "running",
    "demo_uploaded": "running",
    "qa_done": "done",
}


@app.template_filter("status_class")
def status_class_filter(status: str) -> str:
    return STATUS_CLASS_MAP.get(status, "")


# ---- Helpers ----

def group_artifacts(artifacts: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {"intake": [], "criteria": [], "production": [], "qa": [], "other": []}
    for artifact in artifacts:
        stage = artifact["relative_path"].split("/", 1)[0]
        grouped.setdefault(stage, []).append(artifact)
    return grouped


# ---- Routes ----

@app.get("/")
def index():
    project_id = request.args.get("project")
    projects = store.list_projects()
    selected = None
    if project_id:
        selected = store.load_state(project_id)
    elif projects:
        selected = projects[0]
        project_id = selected["id"]

    artifacts = store.list_artifacts(project_id) if project_id else []
    grouped_artifacts = group_artifacts(artifacts)
    knowledge_files = store.list_knowledge_files()

    pipeline = {}
    if selected:
        pipeline = store.build_pipeline_view(project_id)

    return render_template(
        "index.html",
        app_name=config.APP_NAME,
        projects=projects,
        selected=selected,
        artifacts=artifacts,
        grouped_artifacts=grouped_artifacts,
        knowledge_files=knowledge_files,
        pipeline=pipeline,
    )


@app.post("/projects")
def create_project():
    title = (request.form.get("title") or "").strip() or "未命名项目"
    request_text = (request.form.get("request_text") or "").strip()
    # Parse guide-chip-enriched text into intake fields
    intake = _extract_intake_from_text(request_text)
    state = store.create_project(title, request_text, intake=intake)
    source_video = request.files.get("source_video")
    if source_video and source_video.filename:
        store.save_upload(state["id"], source_video, "intake", "source_video")
    return redirect(url_for("index", project=state["id"]))


def _extract_intake_from_text(text: str) -> dict:
    """Best-effort extraction of structured fields from guide-chip-enriched text."""
    mapping = {
        "📺 目标平台：": "target_platform",
        "🌍 交付语言：": "delivery_languages",
        "🎯 验收标准：": "acceptance_focus",
        "🎨 风格目标：": "style_goals",
        "⛔ 明确禁忌：": "avoid_list",
        "👥 目标受众：": "audience",
        "🧪 本轮 demo 要证明：": "demo_goal",
        "⏰ 时间要求：": "deadline",
        "🔗 参考链接：": "references",
    }
    result: dict[str, str] = {}
    for prefix, key in mapping.items():
        if prefix in text:
            # Take content from prefix to next line or next prefix
            start = text.index(prefix) + len(prefix)
            rest = text[start:]
            # Find next prefix or end
            end = len(rest)
            for other_prefix in mapping:
                if other_prefix in rest:
                    idx = rest.index(other_prefix)
                    end = min(end, idx)
            result[key] = rest[:end].strip().split("\n")[0].strip()
    return result


@app.post("/projects/<project_id>/run-criteria")
def run_criteria(project_id: str):
    criteria_stage.run(project_id)
    return redirect(url_for("index", project=project_id))


@app.post("/projects/<project_id>/confirm-criteria")
def confirm_criteria(project_id: str):
    store.confirm_criteria(project_id)
    criteria_stage.write_confirmed_pattern(project_id)
    return redirect(url_for("index", project=project_id))


@app.post("/projects/<project_id>/upload-production")
def upload_production(project_id: str):
    demo_video = request.files.get("demo_video")
    demo_srt = request.files.get("demo_srt")
    notes = (request.form.get("production_notes") or "").strip()
    if demo_video and demo_video.filename:
        store.save_upload(project_id, demo_video, "production", "demo_video")
    if demo_srt and demo_srt.filename:
        store.save_upload(project_id, demo_srt, "production", "demo_srt")
    if notes:
        store.write_text(project_id, "production/notes.md", notes + "\n")
    state = store.load_state(project_id)
    state["status"] = "demo_uploaded"
    state["history"].append({"at": store.now_iso(), "status": "demo_uploaded", "note": "Demo assets uploaded"})
    store.save_state(project_id, state)
    return redirect(url_for("index", project=project_id))


@app.post("/projects/<project_id>/ffmpeg-process")
def ffmpeg_process(project_id: str):
    """使用 FFmpeg 本地处理视频。"""
    from mvp_platform import external_skills

    process_type = request.form.get("process_type", "trim")
    # 获取上传的视频文件
    video_file = request.files.get("video_file")

    if not video_file or not video_file.filename:
        return redirect(url_for("index", project=project_id))

    # 保存上传的视频到项目目录
    project_path = store.project_dir(project_id)
    input_path = project_path / "production" / video_file.filename
    input_path.parent.mkdir(parents=True, exist_ok=True)
    video_file.save(input_path)

    state = store.load_state(project_id)
    result_data = {"process_type": process_type, "input_file": video_file.filename, "at": store.now_iso()}

    try:
        if process_type == "trim":
            start_time = request.form.get("start_time", "0")
            end_time = request.form.get("end_time", "10")
            output_path = input_path.parent / f"trimmed_{input_path.stem}.mp4"
            result = external_skills.trim_video(input_path, start_time, end_time, output_path)
            result_data["result"] = result
            if result["success"]:
                result_data["note"] = f"视频裁剪完成: {start_time} - {end_time}"
                result_data["output_file"] = output_path.name
            else:
                result_data["error"] = result.get("error", "裁剪失败")

        elif process_type == "subtitles":
            model = request.form.get("whisper_model", "base")
            output_path = input_path.parent / f"subtitled_{input_path.stem}.mp4"
            result = external_skills.create_subtitled_video(input_path, output_path, model=model)
            result_data["result"] = result
            if result["success"]:
                result_data["note"] = "字幕生成并合成完成"
                result_data["output_file"] = output_path.name
                result_data["subtitle_file"] = result.get("subtitle_path", "")
            else:
                result_data["error"] = result.get("error", "字幕生成失败")

        elif process_type == "voiceover":
            text = request.form.get("voiceover_text", "").strip()
            voice = request.form.get("voice", "zh-CN-XiaoxiaoNeural")
            if text:
                output_path = input_path.parent / f"voiceover_{input_path.stem}.mp4"
                result = external_skills.create_voiceover_video(input_path, text, output_path, voice=voice)
                result_data["result"] = result
                if result["success"]:
                    result_data["note"] = "AI 配音合成完成"
                    result_data["output_file"] = output_path.name
                else:
                    result_data["error"] = result.get("error", "配音失败")
            else:
                result_data["error"] = "未提供配音文本"

        elif process_type == "extract_audio":
            output_path = input_path.parent / f"{input_path.stem}_audio.mp3"
            result = external_skills.extract_audio(input_path, output_path, format="mp3")
            result_data["result"] = result
            if result["success"]:
                result_data["note"] = "音频提取完成"
                result_data["output_file"] = output_path.name
            else:
                result_data["error"] = result.get("error", "提取失败")

        # 保存处理记录
        state.setdefault("ffmpeg_history", []).append(result_data)
        state["history"].append({"at": store.now_iso(), "status": "ffmpeg_processed", "note": result_data.get("note", "FFmpeg 处理完成")})
        store.save_state(project_id, state)

        # 保存结果到 production 目录
        store.write_json(project_id, f"production/ffmpeg_{process_type}_{store.now_iso().replace(':', '-')}.json", result_data)

    except Exception as e:
        result_data["error"] = str(e)
        state.setdefault("ffmpeg_history", []).append(result_data)
        state["history"].append({"at": store.now_iso(), "status": "ffmpeg_error", "note": f"处理失败: {e}"})
        store.save_state(project_id, state)

    return redirect(url_for("index", project=project_id))


@app.post("/projects/<project_id>/run-qa")
def run_qa(project_id: str):
    try:
        qa_stage.run(project_id)
    except Exception:
        pass
    return redirect(url_for("index", project=project_id))


@app.get("/projects/<project_id>/artifacts/<path:relative_path>")
def artifact(project_id: str, relative_path: str):
    root = store.project_dir(project_id).resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents and target != root:
        raise FileNotFoundError(relative_path)
    return send_file(target, as_attachment=False)


@app.get("/knowledge/<path:filename>")
def knowledge(filename: str):
    target = (config.KNOWLEDGE_DIR / filename).resolve()
    root = config.KNOWLEDGE_DIR.resolve()
    if root not in target.parents and target != root:
        raise FileNotFoundError(filename)
    return send_file(target, as_attachment=False)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5055, debug=True)
