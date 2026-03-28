#!/bin/bash

# 提取音频
# 使用方法: ./extract_audio.sh --video_url "URL" --output "audio.mp3"

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
VIDEO_URL=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --video_url)
            VIDEO_URL="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$VIDEO_URL" ]; then
    echo "用法: $0 --video_url <URL> --output <输出文件名>"
    exit 1
fi

echo "🎵 正在提取音频..."
echo "   来源: $VIDEO_URL"
echo "   输出: $OUTPUT"
echo ""

curl -X POST "https://open.vectcut.com/process/extract_audio" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"video_url\":\"$VIDEO_URL\"}"

echo ""
echo "✅ 音频提取完成"
