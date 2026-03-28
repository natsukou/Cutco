"""外部脚本桥接 — 保留工具函数供 agent 或其他模块直接调用。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import config


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
