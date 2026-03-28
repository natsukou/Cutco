"""QA stage — 启动 Claude Code Agent 执行质检。"""
from __future__ import annotations

import logging

from . import agent_runtime, config, store

logger = logging.getLogger(__name__)


def run(project_id: str) -> dict:
    """启动 QA agent 来质检 demo 视频。"""
    state = store.load_state(project_id)
    project_path = store.project_dir(project_id)

    logger.info("QA agent starting for project %s", project_id)

    # 启动 Claude Code Agent
    result = agent_runtime.run_qa_agent(project_dir=project_path)

    # Agent 完成后，检查产物并更新 state
    artifact_mapping = {
        "engineering_report": "qa/engineering-report.json",
        "audio_report": "qa/audio-report.json",
        "srt_report": "qa/srt-report.json",
        "visual_report": "qa/visual-report.json",
        "qa_report": "qa/qa-report.md",
    }

    for key, relative_path in artifact_mapping.items():
        full_path = project_path / relative_path
        if full_path.exists():
            state["files"][key] = str(full_path)

    if result.success:
        # 从 qa-report.md 提取 verdict
        verdict = _extract_verdict(project_path)
        state["verdict"] = verdict
        state["status"] = "qa_completed"
        state["runtime"]["claude"] = "agent"
        state["history"].append({
            "at": store.now_iso(),
            "status": "qa_completed",
            "note": f"QA agent completed. Verdict: {verdict}",
        })
        logger.info("QA agent completed for project %s, verdict: %s", project_id, verdict)
    else:
        state["runtime"]["claude"] = "error"
        state["history"].append({
            "at": store.now_iso(),
            "status": state["status"],
            "note": f"QA agent failed: {result.error[:200]}",
        })
        store.write_text(project_id, "logs/qa-agent-error.log", result.error)
        if result.output:
            store.write_text(project_id, "logs/qa-agent-output.log", result.output)
        logger.error("QA agent failed for project %s: %s", project_id, result.error[:200])

    store.save_state(project_id, state)
    return state


def _extract_verdict(project_path) -> str:
    """从 qa-report.md 尝试提取 verdict。"""
    report_path = project_path / "qa" / "qa-report.md"
    if not report_path.exists():
        return "UNKNOWN"

    content = report_path.read_text(encoding="utf-8", errors="ignore").upper()

    # 按优先级匹配
    if "FAIL" in content and "CONDITIONAL" not in content.split("FAIL")[0][-20:]:
        return "FAIL"
    if "CONDITIONAL PASS" in content or "CONDITIONAL" in content:
        return "CONDITIONAL PASS"
    if "PASS" in content:
        return "PASS"
    return "UNKNOWN"
