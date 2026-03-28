#!/bin/bash

# 切分视频
# 使用方法: ./split_video.sh --video_url "URL" --start 10 --end 30 --output "output.mp4"

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
VIDEO_URL=""
START=0
END=0
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --video_url)
            VIDEO_URL="$2"
            shift 2
            ;;
        --start)
            START="$2"
            shift 2
            ;;
        --end)
            END="$2"
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
    echo "用法: $0 --video_url <URL> --start <开始时间> --end <结束时间> --output <输出文件名>"
    exit 1
fi

echo "✂️  正在切分视频..."
echo "   来源: $VIDEO_URL"
echo "   时间段: ${START}s - ${END}s"
echo ""

curl -X POST "https://open.vectcut.com/process/split_video" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"video_url\":\"$VIDEO_URL\",\"start\":$START,\"end\":$END}"

echo ""
echo "✅ 视频切分完成"
