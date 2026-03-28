from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from . import config


@dataclass
class AgentRunResult:
    provider: str
    success: bool
    output: str = ""
    error: str = ""
    command: list[str] | None = None


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```json"):
        stripped = stripped[len("```json") :]
    elif stripped.startswith("```"):
        stripped = stripped[len("```") :]
    if stripped.endswith("```"):
        stripped = stripped[:-3]
    return stripped.strip()


def _resolve_claude_command() -> list[str]:
    resolved = shutil.which(config.CLAUDE_COMMAND)
    if resolved:
        lower = resolved.lower()
        if lower.endswith(".ps1"):
            return ["powershell", "-ExecutionPolicy", "Bypass", "-File", resolved]
        return [resolved]
    return [config.CLAUDE_COMMAND]


def _build_skill_context(skill_dir: Path) -> str:
    """读取 SKILL.md 和 references 目录下的所有 .md 文件，拼成完整的 skill context。"""
    parts: list[str] = []

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        parts.append(f"=== SKILL.md ===\n{skill_md.read_text(encoding='utf-8')}")

    ref_dirs = [skill_dir / "reference", skill_dir / "references"]
    for ref_dir in ref_dirs:
        if ref_dir.is_dir():
            for md_file in sorted(ref_dir.glob("*.md")):
                parts.append(f"=== {md_file.name} ===\n{md_file.read_text(encoding='utf-8')}")

    return "\n\n".join(parts)


def _run_claude_agent(prompt: str, cwd: Path) -> AgentRunResult:
    """启动 Claude Code agent session，允许长时间运行和工具调用。"""
    prefix = _resolve_claude_command()
    command = prefix + [
        "--print",
        "--output-format", "text",
        "--allowedTools", "Bash(command:*),Read,Write,Edit",
        prompt,
    ]
    if config.CLAUDE_MODEL:
        insert_at = len(prefix)
        command[insert_at:insert_at] = ["--model", config.CLAUDE_MODEL]

    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=config.AGENT_TIMEOUT,
        )
    except FileNotFoundError:
        return AgentRunResult(
            provider="claude",
            success=False,
            error=f"Claude command not found: {config.CLAUDE_COMMAND}. 请确认已安装 Claude Code CLI。",
            command=command,
        )
    except subprocess.TimeoutExpired:
        return AgentRunResult(
            provider="claude",
            success=False,
            error=f"Claude agent 超时（{config.AGENT_TIMEOUT}s）。可通过 MVP_AGENT_TIMEOUT 环境变量调大。",
            command=command,
        )

    if result.returncode != 0:
        return AgentRunResult(
            provider="claude",
            success=False,
            output=result.stdout,
            error=(result.stderr or result.stdout).strip(),
            command=command,
        )

    return AgentRunResult(
        provider="claude",
        success=True,
        output=result.stdout,
        command=command,
    )


# ---------------------------------------------------------------------------
#  Criteria Agent
# ---------------------------------------------------------------------------

def run_criteria_agent(project_dir: Path) -> AgentRunResult:
    """
    启动 Claude Code agent 来执行 criteria 阶段。
    Agent 读取 SKILL.md 作为行为指南，自主分析需求和视频，输出验收标准文档。
    """
    skill_context = _build_skill_context(config.VIDEO_CRITERIA_DIR)
    scripts_dir = config.VIDEO_CRITERIA_DIR / "scripts"
    knowledge_dir = config.KNOWLEDGE_DIR

    prompt = textwrap.dedent(f"""\
    你是一个视频交付项目的需求分析 Agent。请严格按照以下 SKILL 文档中的步骤和策略哲学执行任务。

    ===== 你的行为指南 =====
    {skill_context}
    ===== 行为指南结束 =====

    ===== 当前任务 =====

    项目目录: {project_dir}
    用户需求文档: {project_dir / "intake" / "user_request.md"}
    结构化 brief: {project_dir / "intake" / "structured-brief.json"}

    工具脚本目录: {scripts_dir}
    经验库目录: {knowledge_dir}

    你需要完成以下工作:

    1. 读取用户需求文档和结构化 brief，理解甲方要什么
    2. 检查 intake/ 目录是否有视频文件（.mp4 / .mov / .mkv）。如有，运行:
       python "{scripts_dir / "probe_source.py"}" --input <视频路径>
       将探测结果保存到 {project_dir / "criteria" / "source_probe.json"}
    3. 如果经验库目录有相关经验文件，读取参考
    4. 按照 SKILL.md 的策略哲学，生成以下文档并写入 {project_dir / "criteria"}/：
       - project-brief.md（项目简报）
       - acceptance-criteria.md（验收标准，区分已确定参数和待填项）
       - pending-items.md（待确认项清单，标注来源和确认方式）
       - demo-plan.json（Demo 计划，JSON 格式）

    关键规则:
    - 能推的参数自己推，不要留空白。参考 SKILL 中的 references 材料
    - 推不了的标注来源，写清楚「来源：demo 确认 / 甲方试听选择」
    - 每条标准自检：能不能让一个没参与过这个项目的人判断「合格/不合格」？
    - 不要生成任何说明文字输出到 stdout，把所有产物写入文件

    开始执行。
    """)

    return _run_claude_agent(prompt, project_dir)


# ---------------------------------------------------------------------------
#  QA Agent
# ---------------------------------------------------------------------------

def run_qa_agent(project_dir: Path) -> AgentRunResult:
    """
    启动 Claude Code agent 来执行 QA 阶段。
    Agent 读取 SKILL.md 作为行为指南，调用检查脚本和视觉审核，输出质检报告。
    """
    skill_context = _build_skill_context(config.VIDEO_QA_DIR)
    qa_scripts_dir = config.VIDEO_QA_DIR / "scripts"
    visual_script = config.VISUAL_REVIEW_SCRIPT
    knowledge_dir = config.KNOWLEDGE_DIR

    prompt = textwrap.dedent(f"""\
    你是一个视频交付项目的质检 Agent。请严格按照以下 SKILL 文档中的策略哲学和步骤执行。

    ===== 你的行为指南 =====
    {skill_context}
    ===== 行为指南结束 =====

    ===== 当前任务 =====

    项目目录: {project_dir}
    验收标准: {project_dir / "criteria" / "acceptance-criteria.md"}
    原片 probe: {project_dir / "criteria" / "source_probe.json"}

    待检成片: 在 {project_dir / "production"} 目录下查找 .mp4 文件
    待检字幕: 在 {project_dir / "production"} 目录下查找 .srt 文件

    QA 检查脚本目录: {qa_scripts_dir}
    视觉审核脚本: {visual_script}
    经验库目录: {knowledge_dir}

    你需要完成以下工作:

    【轨道一：工程参数硬核查】
    1. 找到 production/ 目录下的成片视频和 SRT 字幕文件
    2. 读取 criteria/source_probe.json 作为基线参数
    3. 运行以下检查脚本（按需）:
       # 工程参数检查
       python "{qa_scripts_dir / "check_engineering.py"}" --probe-baseline <probe.json> --input <成片.mp4> --output {project_dir / "qa" / "engineering-report.json"}

       # SRT 检查（如有字幕）
       python "{qa_scripts_dir / "check_srt.py"}" --input <字幕.srt> --video-width <宽度> --video-height <高度> --output {project_dir / "qa" / "srt-report.json"}

       # 音频检查
       python "{qa_scripts_dir / "check_audio.py"}" --input <成片.mp4> --output {project_dir / "qa" / "audio-report.json"}

    【轨道二：视觉/听觉内容审核】
    4. 根据验收标准，构造具体的审核 prompt（参考 SKILL 中的 gemini-visual-qa.md 模板）
    5. 调用视觉审核脚本:
       python "{visual_script}" --video <成片路径> --prompt "<你构造的审核prompt>" --provider {config.VISUAL_PROVIDER}
       将结果保存到 {project_dir / "qa" / "visual-report.json"}

    【输出质检报告】
    6. 综合所有检查结果，按照 SKILL 中的报告模板，撰写完整的质检报告
       写入: {project_dir / "qa" / "qa-report.md"}

    判定规则:
    - 任何工程参数项不合格 → Fail
    - 任何视觉项标注「不合格」→ Fail
    - 视觉项标注「需人工确认」→ Conditional Pass
    - 全部通过 → Pass

    7. 如果发现新类型问题，写入经验库: {knowledge_dir}

    开始执行。
    """)

    return _run_claude_agent(prompt, project_dir)
