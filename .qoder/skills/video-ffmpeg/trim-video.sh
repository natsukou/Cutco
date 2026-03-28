#!/bin/bash
# 视频裁剪脚本
#
# 使用方式：
#   ./trim-video.sh --input <input> --start <start_time> --end <end_time> --output <output>
#
# 示例：
#   ./trim-video.sh --input video.mp4 --start 00:00:10 --end 00:00:30 --output clip.mp4
#   ./trim-video.sh --input video.mp4 --start 10 --end 30 --output clip.mp4

set -e

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT="$2"
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
            echo "❌ 未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必填参数
if [ -z "$INPUT" ] || [ -z "$START" ] || [ -z "$END" ]; then
    echo "用法: $0 --input <input> --start <start_time> --end <end_time> --output <output>"
    echo ""
    echo "示例:"
    echo "  $0 --input video.mp4 --start 00:00:10 --end 00:00:30 --output clip.mp4"
    echo "  $0 --input video.mp4 --start 10 --end 30 --output clip.mp4"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="clip-$(date +%Y%m%d-%H%M%S).mp4"
fi

echo "✂️  开始视频裁剪..."
echo "   输入: $INPUT"
echo "   开始时间: $START"
echo "   结束时间: $END"
echo "   输出: $OUTPUT"
echo ""

# 检查文件是否存在
if [ ! -f "$INPUT" ]; then
    echo "❌ 文件不存在: $INPUT"
    exit 1
fi

# 检查 ffmpeg 是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg 未安装，请先安装 ffmpeg"
    exit 1
fi

# 执行裁剪
ffmpeg -i "$INPUT" -ss "$START" -to "$END" -c:v libx264 -c:a aac -b:a 128k "$OUTPUT"

echo ""
echo "✅ 裁剪完成！"
echo "   输出文件: $OUTPUT"
