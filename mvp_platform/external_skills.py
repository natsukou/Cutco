"""外部脚本桥接 — 保留工具函数供 agent 或其他模块直接调用。

包含：
- 本地脚本执行（probe、visual_review）
- FFmpeg 本地视频编辑能力（ffmpeg_skill 模块）
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import config

# 导出 FFmpeg 本地技能函数
from .ffmpeg_skill import (  # noqa: F401
    # 工具检查
    check_ffmpeg,
    check_edge_tts,
    check_whisper,
    get_tool_status,
    # 视频处理
    trim_video,
    extract_audio,
    merge_videos,
    # TTS 语音合成
    generate_speech,
    # ASR 字幕生成
    generate_subtitles,
    # 视频合成
    add_audio_to_video,
    add_subtitles_to_video,
    # 便捷工作流
    create_voiceover_video,
    create_subtitled_video,
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
