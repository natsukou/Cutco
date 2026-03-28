"""FFmpeg 本地视频编辑技能封装

完全基于本地工具实现，无需任何 API 依赖：
- ffmpeg: 视频处理
- edge-tts: 语音合成
- whisper: 语音识别
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def _run_command(cmd: list[str], timeout: int = 300) -> tuple[int, str, str]:
    """运行 shell 命令并返回结果。"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_ffmpeg() -> bool:
    """检查 ffmpeg 是否已安装。"""
    returncode, _, _ = _run_command(["ffmpeg", "-version"], timeout=5)
    return returncode == 0


def check_edge_tts() -> bool:
    """检查 edge-tts 是否已安装。"""
    returncode, _, _ = _run_command(["edge-tts", "--version"], timeout=5)
    return returncode == 0


def check_whisper() -> bool:
    """检查 whisper 是否已安装。"""
    returncode, _, _ = _run_command(["whisper", "--version"], timeout=5)
    return returncode == 0


def get_tool_status() -> dict[str, bool]:
    """获取所有工具的安装状态。"""
    return {
        "ffmpeg": check_ffmpeg(),
        "edge_tts": check_edge_tts(),
        "whisper": check_whisper(),
    }


# ---- 视频处理 ----

def trim_video(
    input_path: str | Path,
    start_time: str | float,
    end_time: str | float,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """裁剪视频片段。
    
    Args:
        input_path: 输入视频路径
        start_time: 开始时间（秒或 HH:MM:SS 格式）
        end_time: 结束时间（秒或 HH:MM:SS 格式）
        output_path: 输出路径，默认自动生成
    
    Returns:
        包含 output_path、success、message 的字典
    """
    input_path = Path(input_path)
    if not input_path.exists():
        return {"success": False, "error": f"文件不存在: {input_path}"}
    
    if output_path is None:
        timestamp = os.path.getmtime(input_path)
        output_path = input_path.parent / f"trimmed_{input_path.stem}_{int(timestamp)}.mp4"
    else:
        output_path = Path(output_path)
    
    # 转换时间格式
    start_str = str(start_time) if isinstance(start_time, (int, float)) else start_time
    end_str = str(end_time) if isinstance(end_time, (int, float)) else end_time
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-ss", start_str,
        "-to", end_str,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "128k",
        str(output_path),
    ]
    
    returncode, stdout, stderr = _run_command(cmd, timeout=120)
    
    if returncode == 0 and output_path.exists():
        return {
            "success": True,
            "output_path": str(output_path),
            "message": f"视频裁剪完成: {start_str} - {end_str}",
        }
    else:
        return {
            "success": False,
            "error": stderr or "裁剪失败",
            "stdout": stdout,
        }


def extract_audio(
    input_path: str | Path,
    output_path: str | Path | None = None,
    format: str = "mp3",
) -> dict[str, Any]:
    """从视频中提取音频。
    
    Args:
        input_path: 输入视频路径
        output_path: 输出路径，默认自动生成
        format: 音频格式（mp3, wav, aac）
    
    Returns:
        包含 output_path、success、message 的字典
    """
    input_path = Path(input_path)
    if not input_path.exists():
        return {"success": False, "error": f"文件不存在: {input_path}"}
    
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_audio.{format}"
    else:
        output_path = Path(output_path)
    
    codec_map = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "aac": "aac",
    }
    codec = codec_map.get(format, "libmp3lame")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", codec,
    ]
    if format == "mp3":
        cmd.extend(["-ab", "192k"])
    cmd.append(str(output_path))
    
    returncode, stdout, stderr = _run_command(cmd, timeout=60)
    
    if returncode == 0 and output_path.exists():
        return {
            "success": True,
            "output_path": str(output_path),
            "message": f"音频提取完成: {output_path.name}",
        }
    else:
        return {
            "success": False,
            "error": stderr or "提取失败",
        }


def merge_videos(
    video_paths: list[str | Path],
    output_path: str | Path,
    transition: str | None = None,
) -> dict[str, Any]:
    """合并多个视频。
    
    Args:
        video_paths: 视频路径列表
        output_path: 输出路径
        transition: 转场类型（fade, wipe, slide）
    
    Returns:
        包含 output_path、success、message 的字典
    """
    if not video_paths:
        return {"success": False, "error": "未提供视频文件"}
    
    # 创建临时文件列表
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for path in video_paths:
            f.write(f"file '{Path(path).resolve()}'\n")
        list_file = f.name
    
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "128k",
            str(output_path),
        ]
        
        returncode, stdout, stderr = _run_command(cmd, timeout=300)
        
        if returncode == 0 and Path(output_path).exists():
            return {
                "success": True,
                "output_path": str(output_path),
                "message": f"视频合并完成，共 {len(video_paths)} 个文件",
            }
        else:
            return {
                "success": False,
                "error": stderr or "合并失败",
            }
    finally:
        os.unlink(list_file)


# ---- TTS 语音合成 ----

def generate_speech(
    text: str,
    output_path: str | Path,
    voice: str = "zh-CN-XiaoxiaoNeural",
    speed: float = 1.0,
    pitch: int = 0,
) -> dict[str, Any]:
    """使用 edge-tts 生成语音。
    
    Args:
        text: 要合成的文本
        output_path: 输出音频路径
        voice: 音色 ID
        speed: 语速（0.5-2.0）
        pitch: 音调调整（-50 到 50）
    
    Returns:
        包含 output_path、success、message 的字典
    """
    if not check_edge_tts():
        return {
            "success": False,
            "error": "edge-tts 未安装，请运行: pip3 install edge-tts",
        }
    
    output_path = Path(output_path)
    
    # 计算语速百分比
    rate_pct = int((speed - 1) * 100)
    rate_str = f"{rate_pct:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    
    cmd = [
        "edge-tts",
        "--text", text,
        "--voice", voice,
        "--rate", rate_str,
        "--pitch", pitch_str,
        "--write-media", str(output_path),
    ]
    
    returncode, stdout, stderr = _run_command(cmd, timeout=60)
    
    if returncode == 0 and output_path.exists():
        return {
            "success": True,
            "output_path": str(output_path),
            "message": f"配音生成完成: {output_path.name}",
            "text": text,
            "voice": voice,
        }
    else:
        return {
            "success": False,
            "error": stderr or "TTS 失败",
        }


# ---- ASR 语音识别 ----

def generate_subtitles(
    input_path: str | Path,
    output_path: str | Path | None = None,
    model: str = "base",
    language: str = "zh",
) -> dict[str, Any]:
    """使用 Whisper 生成字幕。
    
    Args:
        input_path: 输入视频/音频路径
        output_path: 输出字幕路径，默认自动生成
        model: 模型大小（tiny, base, small, medium, large）
        language: 语言代码
    
    Returns:
        包含 output_path、success、message 的字典
    """
    if not check_whisper():
        return {
            "success": False,
            "error": "whisper 未安装，请运行: pip3 install openai-whisper",
        }
    
    input_path = Path(input_path)
    if not input_path.exists():
        return {"success": False, "error": f"文件不存在: {input_path}"}
    
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.srt"
    else:
        output_path = Path(output_path)
    
    output_dir = output_path.parent
    output_name = output_path.stem
    
    cmd = [
        "whisper",
        str(input_path),
        "--model", model,
        "--language", language,
        "--output_format", "srt",
        "--output_dir", str(output_dir),
        "--output_filename", output_name,
    ]
    
    returncode, stdout, stderr = _run_command(cmd, timeout=300)
    
    # Whisper 生成的文件名可能不同
    generated_file = output_dir / f"{output_name}.srt"
    if not generated_file.exists():
        # 尝试查找生成的文件
        for f in output_dir.glob("*.srt"):
            if input_path.stem in f.name:
                generated_file = f
                break
    
    if returncode == 0 and generated_file.exists():
        return {
            "success": True,
            "output_path": str(generated_file),
            "message": f"字幕生成完成: {generated_file.name}",
            "model": model,
        }
    else:
        return {
            "success": False,
            "error": stderr or "字幕生成失败",
        }


# ---- 视频合成 ----

def add_audio_to_video(
    video_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    volume: float = 1.0,
) -> dict[str, Any]:
    """将音频添加到视频。
    
    Args:
        video_path: 视频路径
        audio_path: 音频路径
        output_path: 输出路径
        volume: 音量倍数
    
    Returns:
        包含 output_path、success、message 的字典
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    
    if not video_path.exists():
        return {"success": False, "error": f"视频不存在: {video_path}"}
    if not audio_path.exists():
        return {"success": False, "error": f"音频不存在: {audio_path}"}
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-filter_complex", f"[1:a]volume={volume}[aout]",
        "-map", "0:v:0",
        "-map", "[aout]",
        "-shortest",
        str(output_path),
    ]
    
    returncode, stdout, stderr = _run_command(cmd, timeout=120)
    
    if returncode == 0 and Path(output_path).exists():
        return {
            "success": True,
            "output_path": str(output_path),
            "message": "音频合成完成",
        }
    else:
        return {
            "success": False,
            "error": stderr or "合成失败",
        }


def add_subtitles_to_video(
    video_path: str | Path,
    subtitle_path: str | Path,
    output_path: str | Path,
    font_size: int = 24,
    font_color: str = "white",
    position: str = "bottom",
) -> dict[str, Any]:
    """将字幕添加到视频。
    
    Args:
        video_path: 视频路径
        subtitle_path: 字幕文件路径（srt 格式）
        output_path: 输出路径
        font_size: 字体大小
        font_color: 字体颜色
        position: 位置（top, center, bottom）
    
    Returns:
        包含 output_path、success、message 的字典
    """
    video_path = Path(video_path)
    subtitle_path = Path(subtitle_path)
    
    if not video_path.exists():
        return {"success": False, "error": f"视频不存在: {video_path}"}
    if not subtitle_path.exists():
        return {"success": False, "error": f"字幕不存在: {subtitle_path}"}
    
    # 位置映射
    pos_map = {
        "top": "(w-text_w)/2:50",
        "center": "(w-text_w)/2:(h-text_h)/2",
        "bottom": "(w-text_w)/2:(h-th-50)",
    }
    pos = pos_map.get(position, pos_map["bottom"])
    
    # 转义字幕路径中的特殊字符
    escaped_subtitle = str(subtitle_path).replace("\\", "/").replace(":", "\\:")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={escaped_subtitle}:force_style='FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'",
        "-c:a", "copy",
        str(output_path),
    ]
    
    returncode, stdout, stderr = _run_command(cmd, timeout=180)
    
    if returncode == 0 and Path(output_path).exists():
        return {
            "success": True,
            "output_path": str(output_path),
            "message": "字幕合成完成",
        }
    else:
        return {
            "success": False,
            "error": stderr or "字幕合成失败",
        }


# ---- 便捷工作流 ----

def create_voiceover_video(
    video_path: str | Path,
    text: str,
    output_path: str | Path,
    voice: str = "zh-CN-XiaoxiaoNeural",
) -> dict[str, Any]:
    """为视频添加 AI 配音。
    
    Args:
        video_path: 原视频路径
        text: 配音文本
        output_path: 输出路径
        voice: 音色
    
    Returns:
        包含 output_path、success、message 的字典
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    
    if not video_path.exists():
        return {"success": False, "error": f"视频不存在: {video_path}"}
    
    # 生成临时音频文件
    temp_audio = output_path.parent / f"temp_audio_{os.urandom(4).hex()}.wav"
    
    try:
        # 生成语音
        tts_result = generate_speech(text, temp_audio, voice=voice)
        if not tts_result["success"]:
            return tts_result
        
        # 合成到视频
        merge_result = add_audio_to_video(video_path, temp_audio, output_path)
        return merge_result
        
    finally:
        # 清理临时文件
        if temp_audio.exists():
            temp_audio.unlink()


def create_subtitled_video(
    video_path: str | Path,
    output_path: str | Path,
    model: str = "base",
) -> dict[str, Any]:
    """自动生成字幕并添加到视频。
    
    Args:
        video_path: 视频路径
        output_path: 输出路径
        model: Whisper 模型
    
    Returns:
        包含 output_path、subtitle_path、success、message 的字典
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    
    if not video_path.exists():
        return {"success": False, "error": f"视频不存在: {video_path}"}
    
    # 生成字幕
    subtitle_result = generate_subtitles(video_path, model=model)
    if not subtitle_result["success"]:
        return subtitle_result
    
    subtitle_path = subtitle_result["output_path"]
    
    try:
        # 合成字幕到视频
        merge_result = add_subtitles_to_video(video_path, subtitle_path, output_path)
        merge_result["subtitle_path"] = subtitle_path
        return merge_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"字幕合成失败: {e}",
            "subtitle_path": subtitle_path,
        }
