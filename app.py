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


@app.post("/projects/<project_id>/vectcut-process")
def vectcut_process(project_id: str):
    """使用 VectCut API 处理视频。"""
    from mvp_platform import external_skills

    process_type = request.form.get("process_type", "split")
    video_url = request.form.get("video_url", "").strip()

    if not video_url:
        return redirect(url_for("index", project=project_id))

    state = store.load_state(project_id)
    result_data = {"process_type": process_type, "video_url": video_url, "at": store.now_iso()}

    try:
        if process_type == "split":
            start_time = float(request.form.get("start_time", 0))
            end_time = float(request.form.get("end_time", 10))
            result = external_skills.split_video(video_url, start_time, end_time)
            result_data["result"] = result
            result_data["note"] = f"视频裁剪完成: {start_time}s - {end_time}s"

        elif process_type == "subtitles":
            # 创建草稿并添加视频，然后生成字幕
            draft_result = external_skills.create_draft(f"{state['title']}_字幕版", 1080, 1920)
            draft_id = draft_result.get("draft_id", "")
            if draft_id:
                external_skills.add_video(draft_id, video_url)
                subtitles = external_skills.create_subtitles_from_video(draft_id, video_url)
                result_data["result"] = {"draft_id": draft_id, "draft_url": draft_result.get("draft_url", ""), "subtitles_count": len(subtitles)}
                result_data["note"] = f"字幕生成完成，共 {len(subtitles)} 条字幕"
            else:
                result_data["error"] = "创建草稿失败"

        elif process_type == "voiceover":
            text = request.form.get("voiceover_text", "").strip()
            voice_id = request.form.get("voice_id", "")
            if text:
                draft_result = external_skills.create_draft(f"{state['title']}_配音版", 1080, 1920)
                draft_id = draft_result.get("draft_id", "")
                if draft_id:
                    vo_result = external_skills.create_voiceover_video(draft_id, text, video_url=video_url, voice_id=voice_id)
                    result_data["result"] = {"draft_id": draft_id, "draft_url": draft_result.get("draft_url", ""), **vo_result}
                    result_data["note"] = f"AI 配音完成，音频时长: {vo_result.get('duration', 0):.1f}s"
                else:
                    result_data["error"] = "创建草稿失败"
            else:
                result_data["error"] = "未提供配音文本"

        elif process_type == "extract_audio":
            result = external_skills.extract_audio(video_url)
            result_data["result"] = result
            result_data["note"] = "音频提取完成"

        # 保存处理记录
        state.setdefault("vectcut_history", []).append(result_data)
        state["history"].append({"at": store.now_iso(), "status": "vectcut_processed", "note": result_data.get("note", "VectCut 处理完成")})
        store.save_state(project_id, state)

        # 保存结果到 production 目录
        store.write_json(project_id, f"production/vectcut_{process_type}_{store.now_iso().replace(':', '-')}.json", result_data)

    except Exception as e:
        result_data["error"] = str(e)
        state.setdefault("vectcut_history", []).append(result_data)
        state["history"].append({"at": store.now_iso(), "status": "vectcut_error", "note": f"处理失败: {e}"})
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
