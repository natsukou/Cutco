"""外部脚本桥接 — 保留工具函数供 agent 或其他模块直接调用。

包含：
- 本地脚本执行（probe、visual_review）
- VectCut API 视频编辑能力（vectcut_skill 模块）
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import config

# 导出 VectCut 技能函数
from .vectcut_skill import (  # noqa: F401
    # 草稿管理
    create_draft,
    # 视频处理
    split_video,
    extract_audio,
    get_duration,
    # 素材编排
    add_video,
    add_audio,
    add_text,
    add_image,
    # AI 能力
    generate_speech,
    generate_ai_video,
    check_ai_video_status,
    wait_for_ai_video,
    # ASR 字幕
    asr_llm,
    asr_basic,
    asr_nlp,
    create_subtitles_from_video,
    # 渲染
    render_draft,
    check_render_status,
    wait_for_render,
    # 便捷工作流
    create_voiceover_video,
)


def run_probe(video_path: Path) -> dict:
    """运行 probe_source.py 提取视频参数。"""
    try:
        result = subprocess.run(
            ["python", str(config.PROBE_SCRIPT), "--input", str(video_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return {"error": result.stderr or "probe 脚本返回空结果"}
    except Exception as e:
        return {"error": str(e)}


def run_visual_review(video_path: Path, prompt: str, provider: str = "") -> dict:
    """运行 visual_review.py 进行视觉审核。"""
    provider = provider or config.VISUAL_PROVIDER
    try:
        result = subprocess.run(
            [
                "python", str(config.VISUAL_REVIEW_SCRIPT),
                "--video", str(video_path),
                "--prompt", prompt,
                "--provider", provider,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return {"error": result.stderr or "视觉审核脚本返回空结果"}
    except Exception as e:
        return {"error": str(e)}
