from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from . import config


STAGE_DIRS = ("intake", "criteria", "production", "qa", "logs")
STATE_FILE = "state.json"
INTAKE_KEYS = (
    "task_type",
    "target_platform",
    "delivery_languages",
    "audience",
    "style_goals",
    "avoid_list",
    "demo_goal",
    "acceptance_focus",
    "references",
    "deadline",
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    simplified = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value.strip().lower())
    simplified = re.sub(r"-{2,}", "-", simplified).strip("-")
    return simplified or "project"


def ensure_project_structure(project_dir: Path) -> None:
    for folder in STAGE_DIRS:
        (project_dir / folder).mkdir(parents=True, exist_ok=True)


def project_dir(project_id: str) -> Path:
    return config.PROJECTS_DIR / project_id


def state_path(project_id: str) -> Path:
    return project_dir(project_id) / STATE_FILE


def normalize_intake(payload: dict[str, Any] | None) -> dict[str, str]:
    payload = payload or {}
    normalized: dict[str, str] = {}
    for key in INTAKE_KEYS:
        normalized[key] = str(payload.get(key, "") or "").strip()
    return normalized


def intake_to_markdown(title: str, intake: dict[str, str], request_text: str) -> str:
    lines = [
        f"# {title}",
        "",
        "## 结构化需求",
        f"- 任务类型：{intake.get('task_type') or '未填写'}",
        f"- 目标平台：{intake.get('target_platform') or '未填写'}",
        f"- 交付语言：{intake.get('delivery_languages') or '未填写'}",
        f"- 目标受众：{intake.get('audience') or '未填写'}",
        f"- 风格目标：{intake.get('style_goals') or '未填写'}",
        f"- 明确禁忌：{intake.get('avoid_list') or '未填写'}",
        f"- 本轮 demo 要证明什么：{intake.get('demo_goal') or '未填写'}",
        f"- 验收重点：{intake.get('acceptance_focus') or '未填写'}",
        f"- 参考链接或参考视频：{intake.get('references') or '未填写'}",
        f"- 时间要求：{intake.get('deadline') or '未填写'}",
        "",
        "## 原始补充描述",
        request_text.strip() or "未填写",
        "",
    ]
    return "\n".join(lines)


def create_project(title: str, request_text: str, intake: dict[str, Any] | None = None) -> dict[str, Any]:
    config.ensure_base_dirs()
    project_id = f"{datetime.now():%Y%m%d-%H%M%S}-{slugify(title)[:36]}"
    directory = project_dir(project_id)
    ensure_project_structure(directory)
    intake_data = normalize_intake(intake)
    request_markdown = intake_to_markdown(title, intake_data, request_text)

    state = {
        "id": project_id,
        "title": title,
        "request_text": request_text.strip(),
        "intake": intake_data,
        "status": "intake",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "task_type": intake_data.get("task_type") or "full",
        "platform": intake_data.get("target_platform") or "unknown",
        "verdict": None,
        "files": {},
        "notes": [],
        "history": [{"at": now_iso(), "status": "intake", "note": "Project created"}],
        "runtime": {"claude": "pending", "gemini": "pending"},
    }

    (directory / "intake" / "user_request.md").write_text(request_markdown, encoding="utf-8")
    (directory / "intake" / "structured-brief.json").write_text(
        json.dumps(intake_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    save_state(project_id, state)
    return state


def load_state(project_id: str) -> dict[str, Any]:
    return hydrate_state(json.loads(state_path(project_id).read_text(encoding="utf-8")))


def save_state(project_id: str, state: dict[str, Any]) -> dict[str, Any]:
    state = hydrate_state(state)
    state["updated_at"] = now_iso()
    state_path(project_id).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def append_note(project_id: str, note: str) -> dict[str, Any]:
    state = load_state(project_id)
    state["notes"].append({"at": now_iso(), "text": note})
    return save_state(project_id, state)


def list_projects() -> list[dict[str, Any]]:
    config.ensure_base_dirs()
    projects: list[dict[str, Any]] = []
    for candidate in sorted(config.PROJECTS_DIR.iterdir(), reverse=True):
        if not candidate.is_dir():
            continue
        state_file = candidate / STATE_FILE
        if state_file.exists():
            projects.append(hydrate_state(json.loads(state_file.read_text(encoding="utf-8"))))
    return projects


def hydrate_state(state: dict[str, Any]) -> dict[str, Any]:
    state.setdefault("intake", normalize_intake(None))
    state.setdefault("files", {})
    state.setdefault("notes", [])
    state.setdefault("history", [])
    state.setdefault("runtime", {})
    state["runtime"].setdefault("claude", "pending")
    state["runtime"].setdefault("gemini", "pending")
    state.setdefault("task_type", "full")
    state.setdefault("platform", "unknown")
    state.setdefault("verdict", None)
    return state


def save_upload(project_id: str, file_storage, stage: str, key: str) -> Path | None:
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None
    destination = project_dir(project_id) / stage / Path(file_storage.filename).name
    file_storage.save(destination)
    state = load_state(project_id)
    state["files"][key] = str(destination)
    save_state(project_id, state)
    return destination


def copy_external_file(project_id: str, source: Path, stage: str, key: str) -> Path:
    destination = project_dir(project_id) / stage / source.name
    shutil.copy2(source, destination)
    state = load_state(project_id)
    state["files"][key] = str(destination)
    save_state(project_id, state)
    return destination


def write_text(project_id: str, relative_path: str, content: str) -> Path:
    destination = project_dir(project_id) / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination


def write_json(project_id: str, relative_path: str, payload: dict[str, Any]) -> Path:
    destination = project_dir(project_id) / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination


def list_artifacts(project_id: str) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    root = project_dir(project_id)
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or file_path.name == STATE_FILE:
            continue
        relative = file_path.relative_to(root).as_posix()
        artifacts.append({"relative_path": relative, "name": file_path.name, "size": file_path.stat().st_size})
    return artifacts


def list_knowledge_files() -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(config.KNOWLEDGE_DIR.glob("*.md"), reverse=True):
        files.append({"name": path.name, "path": str(path), "size": path.stat().st_size})
    return files


def append_project_pattern(filename: str, heading: str, lines: list[str]) -> Path:
    path = config.KNOWLEDGE_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else f"# {filename}\n\n"
    addition = [f"## {heading}", *[f"- {line}" for line in lines], ""]
    path.write_text(existing + "\n".join(addition), encoding="utf-8")
    return path


def confirm_criteria(project_id: str) -> dict[str, Any]:
    state = load_state(project_id)
    state["status"] = "approved_for_demo"
    state["history"].append({"at": now_iso(), "status": "approved_for_demo", "note": "Criteria confirmed by user"})
    return save_state(project_id, state)


def _preview(path_str: str | None, limit: int = 2400) -> str:
    if not path_str:
        return ""
    p = Path(path_str)
    if not p.exists() or p.suffix.lower() not in {".md", ".json", ".srt", ".txt"}:
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")[:limit]


STATUS_FLOW = ["intake", "criteria_ready", "approved_for_demo", "demo_uploaded", "qa_done"]


def build_pipeline_view(project_id: str) -> dict[str, dict[str, Any]]:
    """Build a structured pipeline view for template rendering."""
    state = load_state(project_id)
    status = state.get("status", "intake")
    files = state.get("files", {})

    # Determine which stages are reached
    reached = set()
    for s in STATUS_FLOW:
        reached.add(s)
        if s == status:
            break

    # --- Criteria node ---
    criteria_has_content = bool(files.get("project_brief") or files.get("acceptance_criteria"))
    if status in ("intake",) and not criteria_has_content:
        c_status, c_label = "pending", "待运行"
    elif criteria_has_content:
        c_status, c_label = "done", "已生成"
    else:
        c_status, c_label = "pending", "待运行"

    brief_text = _preview(files.get("project_brief"))
    acceptance_text = _preview(files.get("acceptance_criteria"))

    criteria_summary = "AI 分析需求并生成验收标准" if c_status == "pending" else "验收标准已生成，请确认"

    # --- Production node ---
    if "approved_for_demo" in reached or "demo_uploaded" in reached:
        if "demo_uploaded" in reached:
            p_status, p_label = "done", "已上传"
            p_summary = "Demo 素材已上传"
        else:
            p_status, p_label = "running", "待上传"
            p_summary = "标准已确认，请上传 Demo 文件"
    else:
        p_status, p_label = "pending", "等待前序"
        p_summary = "需先确认验收标准"

    # --- QA node ---
    if "qa_done" in reached:
        qa_status, qa_label = "done", "已完成"
        qa_summary = f"质检结论：{state.get('verdict', 'N/A')}"
    elif "demo_uploaded" in reached:
        qa_status, qa_label = "pending", "可运行"
        qa_summary = "Demo 已上传，可运行质检"
    else:
        qa_status, qa_label = "pending", "等待前序"
        qa_summary = "需先上传 Demo"

    qa_report = _preview(files.get("qa_report"))

    return {
        "criteria": {
            "status": c_status,
            "label": c_label,
            "summary": criteria_summary,
            "brief": brief_text,
            "acceptance": acceptance_text,
        },
        "production": {
            "status": p_status,
            "label": p_label,
            "summary": p_summary,
        },
        "qa": {
            "status": qa_status,
            "label": qa_label,
            "summary": qa_summary,
            "report": qa_report,
        },
    }
