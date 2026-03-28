"""VectCut API 视频编辑技能封装

基于 video-editor skill 的能力，提供 Python 接口调用 VectCut API 进行视频处理。
支持：视频裁剪、配音生成、字幕生成、AI视频生成、素材混剪、云渲染等功能。
"""
from __future__ import annotations

import os
import time
from typing import Any

import requests

VECTCUT_BASE_URL = "https://open.vectcut.com"


def _get_api_key() -> str:
    """获取 VECTCUT_API_KEY 环境变量。"""
    api_key = os.environ.get("VECTCUT_API_KEY", "").strip()
    if not api_key:
        raise ValueError("VECTCUT_API_KEY 环境变量未设置")
    return api_key


def _headers() -> dict[str, str]:
    """构建请求头。"""
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


def create_draft(name: str, width: int = 1080, height: int = 1920) -> dict[str, Any]:
    """创建剪映草稿。
    
    Args:
        name: 草稿名称
        width: 视频宽度，默认 1080（竖屏）
        height: 视频高度，默认 1920（竖屏）
    
    Returns:
        包含 draft_id、draft_url 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/create_draft"
    payload = {"name": name, "width": width, "height": height}
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def split_video(video_url: str, start: float, end: float) -> dict[str, Any]:
    """切分视频，提取指定时间段。
    
    Args:
        video_url: 视频 URL
        start: 开始时间（秒）
        end: 结束时间（秒）
    
    Returns:
        包含新视频 URL 的字典
    """
    url = f"{VECTCUT_BASE_URL}/process/split_video"
    payload = {"video_url": video_url, "start": start, "end": end}
    response = requests.post(url, headers=_headers(), json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def extract_audio(video_url: str) -> dict[str, Any]:
    """从视频中提取音频。
    
    Args:
        video_url: 视频 URL
    
    Returns:
        包含音频 URL 的字典
    """
    url = f"{VECTCUT_BASE_URL}/process/extract_audio"
    payload = {"video_url": video_url}
    response = requests.post(url, headers=_headers(), json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def get_duration(media_url: str) -> dict[str, Any]:
    """获取媒体文件时长。
    
    Args:
        media_url: 媒体文件 URL
    
    Returns:
        包含 duration（秒）的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/get_duration"
    payload = {"url": media_url}
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def generate_speech(
    text: str,
    provider: str = "minimax",
    model: str = "speech-01",
    voice_id: str = "",
    volume: float = 1.0,
    target_start: float = 0,
) -> dict[str, Any]:
    """生成语音（TTS）。
    
    Args:
        text: 要合成的文本
        provider: 服务商，默认 minimax
        model: 模型名称，默认 speech-01
        voice_id: 音色 ID
        volume: 音量，默认 1.0
        target_start: 在时间线上的起始位置
    
    Returns:
        包含 audio_url 的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/generate_speech"
    payload = {
        "text": text,
        "provider": provider,
        "model": model,
        "voice_id": voice_id,
        "volume": volume,
        "target_start": target_start,
    }
    response = requests.post(url, headers=_headers(), json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def add_video(
    draft_id: str,
    video_url: str,
    start: float = 0,
    end: float | None = None,
    target_start: float = 0,
) -> dict[str, Any]:
    """向草稿添加视频素材。
    
    Args:
        draft_id: 草稿 ID
        video_url: 视频 URL
        start: 视频开始时间（秒）
        end: 视频结束时间（秒），None 表示使用完整视频
        target_start: 在时间线上的起始位置（秒）
    
    Returns:
        包含 material_id 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/add_video"
    payload: dict[str, Any] = {
        "draft_id": draft_id,
        "video_url": video_url,
        "start": start,
        "target_start": target_start,
    }
    if end is not None:
        payload["end"] = end
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def add_audio(
    draft_id: str,
    audio_url: str,
    volume: float = 1.0,
    target_start: float = 0,
) -> dict[str, Any]:
    """向草稿添加音频素材。
    
    Args:
        draft_id: 草稿 ID
        audio_url: 音频 URL
        volume: 音量，默认 1.0
        target_start: 在时间线上的起始位置（秒）
    
    Returns:
        包含 material_id 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/add_audio"
    payload = {
        "draft_id": draft_id,
        "audio_url": audio_url,
        "volume": volume,
        "target_start": target_start,
    }
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def add_text(
    draft_id: str,
    text: str,
    start: float,
    end: float,
    style: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """向草稿添加文本/字幕。
    
    Args:
        draft_id: 草稿 ID
        text: 文本内容
        start: 开始时间（秒）
        end: 结束时间（秒）
        style: 样式配置，如字体大小、颜色等
    
    Returns:
        包含 material_id 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/add_text"
    payload: dict[str, Any] = {
        "draft_id": draft_id,
        "text": text,
        "start": start,
        "end": end,
    }
    if style:
        payload["style"] = style
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def add_image(
    draft_id: str,
    image_url: str,
    duration: float,
    target_start: float = 0,
) -> dict[str, Any]:
    """向草稿添加图片素材。
    
    Args:
        draft_id: 草稿 ID
        image_url: 图片 URL
        duration: 显示时长（秒）
        target_start: 在时间线上的起始位置（秒）
    
    Returns:
        包含 material_id 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/add_image"
    payload = {
        "draft_id": draft_id,
        "image_url": image_url,
        "duration": duration,
        "target_start": target_start,
    }
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def generate_ai_video(
    prompt: str,
    model: str = "kling-v1",
    resolution: str = "1080x1920",
) -> dict[str, Any]:
    """生成 AI 视频（文生视频）。
    
    Args:
        prompt: 视频描述提示词
        model: 模型名称，默认 kling-v1
        resolution: 分辨率，默认 1080x1920
    
    Returns:
        包含 task_id 的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/generate_ai_video"
    payload = {"prompt": prompt, "model": model, "resolution": resolution}
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def check_ai_video_status(task_id: str) -> dict[str, Any]:
    """查询 AI 视频生成任务状态。
    
    Args:
        task_id: 任务 ID
    
    Returns:
        包含 status、progress、video_url 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/aivideo/task_status"
    headers = {"Authorization": f"Bearer {_get_api_key()}"}
    response = requests.get(url, headers=headers, params={"task_id": task_id}, timeout=30)
    response.raise_for_status()
    return response.json()


def wait_for_ai_video(
    task_id: str,
    poll_interval: int = 10,
    max_wait: int = 600,
) -> dict[str, Any]:
    """轮询等待 AI 视频生成完成。
    
    Args:
        task_id: 任务 ID
        poll_interval: 轮询间隔（秒）
        max_wait: 最大等待时间（秒）
    
    Returns:
        最终任务状态字典
    """
    start_time = time.time()
    while time.time() - start_time < max_wait:
        result = check_ai_video_status(task_id)
        status = result.get("status", "")
        if status in ("completed", "failed"):
            return result
        time.sleep(poll_interval)
    return {"status": "timeout", "task_id": task_id}


def asr_llm(video_url: str) -> dict[str, Any]:
    """使用 LLM 进行语音识别，适合短视频字幕。
    
    Args:
        video_url: 视频 URL
    
    Returns:
        包含 segments（每句文本、开始时间、结束时间）的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/asr_llm"
    payload = {"video_url": video_url}
    response = requests.post(url, headers=_headers(), json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def asr_basic(video_url: str) -> dict[str, Any]:
    """基础语音识别，速度快，适合横屏字幕。
    
    Args:
        video_url: 视频 URL
    
    Returns:
        包含识别结果的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/asr_basic"
    payload = {"video_url": video_url}
    response = requests.post(url, headers=_headers(), json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def asr_nlp(video_url: str) -> dict[str, Any]:
    """语义分句语音识别，适合竖屏字幕。
    
    Args:
        video_url: 视频 URL
    
    Returns:
        包含识别结果的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/asr_nlp"
    payload = {"video_url": video_url}
    response = requests.post(url, headers=_headers(), json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def render_draft(
    draft_id: str,
    resolution: str = "1080P",
    framerate: str = "30",
) -> dict[str, Any]:
    """发起草稿云渲染。
    
    Args:
        draft_id: 草稿 ID
        resolution: 分辨率，默认 1080P
        framerate: 帧率，默认 30
    
    Returns:
        包含 task_id 的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/generate_video"
    payload = {"draft_id": draft_id, "resolution": resolution, "framerate": framerate}
    response = requests.post(url, headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def check_render_status(task_id: str) -> dict[str, Any]:
    """查询渲染任务状态。
    
    Args:
        task_id: 任务 ID
    
    Returns:
        包含 status、progress、video_url 等信息的字典
    """
    url = f"{VECTCUT_BASE_URL}/cut_jianying/task_status"
    headers = {"Authorization": f"Bearer {_get_api_key()}"}
    response = requests.get(url, headers=headers, params={"task_id": task_id}, timeout=30)
    response.raise_for_status()
    return response.json()


def wait_for_render(
    task_id: str,
    poll_interval: int = 10,
    max_wait: int = 600,
) -> dict[str, Any]:
    """轮询等待渲染完成。
    
    Args:
        task_id: 任务 ID
        poll_interval: 轮询间隔（秒）
        max_wait: 最大等待时间（秒）
    
    Returns:
        最终任务状态字典
    """
    start_time = time.time()
    while time.time() - start_time < max_wait:
        result = check_render_status(task_id)
        status = result.get("status", "")
        if status in ("completed", "failed"):
            return result
        time.sleep(poll_interval)
    return {"status": "timeout", "task_id": task_id}


# ---- 便捷工作流函数 ----

def create_subtitles_from_video(
    draft_id: str,
    video_url: str,
    style: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """从视频自动生成字幕并添加到草稿。
    
    Args:
        draft_id: 草稿 ID
        video_url: 视频 URL
        style: 字幕样式配置
    
    Returns:
        添加的字幕素材信息列表
    """
    # 使用 ASR 识别语音
    asr_result = asr_llm(video_url)
    segments = asr_result.get("segments", [])
    
    # 默认字幕样式
    default_style = {
        "font_size": 28,
        "color": "#FFFFFF",
        "background_color": "#00000080",
        "y": 0.8,
    }
    final_style = {**default_style, **(style or {})}
    
    # 添加字幕到草稿
    subtitles = []
    for seg in segments:
        result = add_text(
            draft_id=draft_id,
            text=seg.get("text", ""),
            start=seg.get("start", 0),
            end=seg.get("end", 0),
            style=final_style,
        )
        subtitles.append(result)
    
    return subtitles


def create_voiceover_video(
    draft_id: str,
    text: str,
    video_url: str | None = None,
    image_url: str | None = None,
    provider: str = "minimax",
    voice_id: str = "",
) -> dict[str, Any]:
    """创建带配音的视频/图片展示。
    
    Args:
        draft_id: 草稿 ID
        text: 配音文本
        video_url: 背景视频 URL（与 image_url 二选一）
        image_url: 背景图片 URL（与 video_url 二选一）
        provider: TTS 服务商
        voice_id: 音色 ID
    
    Returns:
        包含音频 material_id 和时长的字典
    """
    # 生成配音
    speech_result = generate_speech(text=text, provider=provider, voice_id=voice_id)
    audio_url = speech_result.get("audio_url", "")
    
    # 获取音频时长
    duration_result = get_duration(audio_url)
    audio_duration = duration_result.get("duration", 0)
    
    # 添加音频到草稿
    audio_material = add_audio(draft_id=draft_id, audio_url=audio_url)
    
    # 添加视频或图片背景
    if video_url:
        add_video(draft_id=draft_id, video_url=video_url, target_start=0)
    elif image_url:
        add_image(
            draft_id=draft_id,
            image_url=image_url,
            duration=audio_duration,
            target_start=0,
        )
    
    return {
        "audio_material": audio_material,
        "duration": audio_duration,
        "audio_url": audio_url,
    }
