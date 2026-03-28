"""
视觉理解脚本 —— 被 Claude Code Agent 调用

用法:
    python visual_review.py --video <path> --prompt <prompt_text> --provider gemini|glm
    python visual_review.py --video <path> --prompt-file <prompt_file> --provider gemini

输出: JSON 到 stdout

支持的 provider:
  - gemini : Google Gemini (gemini-2.0-flash 等)
  - glm    : 智谱 GLM-4V (glm-4v-flash 等)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
#  Gemini Provider
# ---------------------------------------------------------------------------

def _review_gemini(video_path: str, prompt: str) -> dict:
    try:
        import google.generativeai as genai
    except ImportError:
        return {"error": "google-generativeai 未安装。运行: pip install google-generativeai"}

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {"error": "GEMINI_API_KEY 环境变量未设置"}

    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    genai.configure(api_key=api_key)

    try:
        video_file = genai.upload_file(path=video_path)
        while video_file.state.name == "PROCESSING":
            time.sleep(5)
            video_file = genai.get_file(video_file.name)
        if video_file.state.name == "FAILED":
            return {"error": f"Gemini 文件上传失败: {video_file.name}"}

        model = genai.GenerativeModel(model_name)
        response = model.generate_content([video_file, prompt])
        raw = response.text.strip()

        # 尝试解析 JSON
        clean = raw.removeprefix("```json").removesuffix("```").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"raw_response": raw, "overall": "CONDITIONAL", "parse_note": "无法解析为 JSON，返回原文"}
    except Exception as e:
        return {"error": f"Gemini API 调用失败: {e}"}


# ---------------------------------------------------------------------------
#  GLM-4V Provider
# ---------------------------------------------------------------------------

def _review_glm(video_path: str, prompt: str) -> dict:
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        return {"error": "zhipuai 未安装。运行: pip install zhipuai"}

    api_key = os.environ.get("GLM_API_KEY", "").strip()
    if not api_key:
        return {"error": "GLM_API_KEY 环境变量未设置"}

    model_name = os.environ.get("GLM_MODEL", "glm-4v-flash")

    try:
        client = ZhipuAI(api_key=api_key)

        # GLM-4V 通过 URL 或 base64 传递视频
        # 对于本地文件，使用 base64 编码
        import base64
        video_bytes = Path(video_path).read_bytes()
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {"url": f"data:video/mp4;base64,{video_b64}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        raw = response.choices[0].message.content.strip()

        clean = raw.removeprefix("```json").removesuffix("```").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"raw_response": raw, "overall": "CONDITIONAL", "parse_note": "无法解析为 JSON，返回原文"}
    except Exception as e:
        return {"error": f"GLM API 调用失败: {e}"}


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

PROVIDERS = {
    "gemini": _review_gemini,
    "glm": _review_glm,
}


def main():
    parser = argparse.ArgumentParser(description="视觉理解脚本")
    parser.add_argument("--video", required=True, help="待审核视频路径")
    parser.add_argument("--prompt", help="审核 prompt 文本")
    parser.add_argument("--prompt-file", help="审核 prompt 文件路径")
    parser.add_argument("--provider", default="gemini", choices=list(PROVIDERS.keys()), help="视觉模型 provider")
    parser.add_argument("--output", help="输出 JSON 文件路径（不指定则输出到 stdout）")
    args = parser.parse_args()

    if not Path(args.video).exists():
        result = {"error": f"视频文件不存在: {args.video}"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.prompt:
        prompt = args.prompt
    else:
        print(json.dumps({"error": "必须指定 --prompt 或 --prompt-file"}, ensure_ascii=False))
        sys.exit(1)

    provider_fn = PROVIDERS[args.provider]
    result = provider_fn(args.video, prompt)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_json, encoding="utf-8")

    print(output_json)


if __name__ == "__main__":
    main()
