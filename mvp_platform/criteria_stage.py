"""Criteria stage — 启动 Claude Code Agent 生成验收标准。"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from . import agent_runtime, config, store

logger = logging.getLogger(__name__)


def run(project_id: str) -> dict:
    """启动 criteria agent 来分析需求和视频，生成验收标准。"""
    state = store.load_state(project_id)
    project_path = store.project_dir(project_id)

    logger.info("Criteria agent starting for project %s", project_id)

    # 启动 Claude Code Agent
    result = agent_runtime.run_criteria_agent(project_dir=project_path)

    # Agent 完成后，检查产物并更新 state
    artifact_mapping = {
        "project_brief": "criteria/project-brief.md",
        "acceptance_criteria": "criteria/acceptance-criteria.md",
        "pending_items": "criteria/pending-items.md",
        "demo_plan": "criteria/demo-plan.json",
        "source_probe": "criteria/source_probe.json",
    }

    for key, relative_path in artifact_mapping.items():
        full_path = project_path / relative_path
        if full_path.exists():
            state["files"][key] = str(full_path)

    if result.success:
        state["status"] = "awaiting_confirmation"
        state["runtime"]["claude"] = "agent"
        state["history"].append({
            "at": store.now_iso(),
            "status": "awaiting_confirmation",
            "note": "Criteria agent completed successfully",
        })
        logger.info("Criteria agent completed for project %s", project_id)
    else:
        state["runtime"]["claude"] = "error"
        state["history"].append({
            "at": store.now_iso(),
            "status": state["status"],
            "note": f"Criteria agent failed: {result.error[:200]}",
        })
        # 将错误信息写入日志文件以便排查
        store.write_text(project_id, "logs/criteria-agent-error.log", result.error)
        if result.output:
            store.write_text(project_id, "logs/criteria-agent-output.log", result.output)
        logger.error("Criteria agent failed for project %s: %s", project_id, result.error[:200])

    store.save_state(project_id, state)
    return state


def write_confirmed_pattern(project_id: str) -> None:
    """用户确认验收标准后，将关键参数沉淀到经验库。"""
    state = store.load_state(project_id)
    task_type = state.get("task_type", "full")
    platform = state.get("platform", "unknown")
    from datetime import datetime

    filename = f"{task_type}-{platform}-{datetime.now():%Y-%m}.md"
    heading = f"项目 {state.get('title', project_id)} 验收标准确认（{datetime.now():%Y-%m-%d}）"

    lines = [f"项目 ID: {project_id}"]

    # 从验收标准文件提取关键信息
    ac_path = state.get("files", {}).get("acceptance_criteria")
    if ac_path and Path(ac_path).exists():
        content = Path(ac_path).read_text(encoding="utf-8", errors="ignore")
        # 取前 500 字符作为摘要
        lines.append(f"验收标准摘要: {content[:500]}")

    store.append_project_pattern(filename, heading, lines)
