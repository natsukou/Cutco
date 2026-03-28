#!/bin/bash
# 快速混剪脚本
#
# 使用方式：
#   ./quick-mix.sh --videos <video1> <video2> ... --audio <audio> --output <output> [--duration <seconds>] [--transition <type>]
#
# 示例：
#   ./quick-mix.sh --videos video1.mp4 video2.mp4 --audio bgm.mp3 --output output.mp4
#   ./quick-mix.sh --videos video1.mp4 video2.mp4 --audio bgm.mp3 --output output.mp4 --duration 30 --transition fade

set -e

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --videos)
            shift
            VIDEOS=()
            while [[ $# -gt 0 && ! $1 =~ ^-- ]]; do
                VIDEOS+=("$1")
                shift
            done
            ;;
        --audio)
            AUDIO="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --transition)
            TRANSITION="$2"
            shift 2
            ;;
        *)
            echo "❌ 未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必填参数
if [ ${#VIDEOS[@]} -eq 0 ]; then
    echo "用法: $0 --videos <video1> <video2> ... --audio <audio> --output <output> [--duration <seconds>] [--transition <type>]"
    echo ""
    echo "示例:"
    echo "  $0 --videos video1.mp4 video2.mp4 --audio bgm.mp3 --output output.mp4"
    echo "  $0 --videos video1.mp4 video2.mp4 --audio bgm.mp3 --output output.mp4 --duration 30 --transition fade"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="output-$(date +%Y%m%d-%H%M%S).mp4"
fi

echo "🎬 开始快速混剪..."
echo "   视频: ${VIDEOS[@]}"
echo "   音频: ${AUDIO:-无}"
echo "   输出: $OUTPUT"
echo "   时长: ${DURATION:-自动}"
echo "   转场: ${TRANSITION:-无}"
echo ""

# 检查 ffmpeg 是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg 未安装，请先安装 ffmpeg"
    exit 1
fi

# 检查视频文件是否存在
for video in "${VIDEOS[@]}"; do
    if [ ! -f "$video" ]; then
        echo "❌ 视频文件不存在: $video"
        exit 1
    fi
done

# 检查音频文件是否存在（如果指定）
if [ -n "$AUDIO" ] && [ ! -f "$AUDIO" ]; then
    echo "❌ 音频文件不存在: $AUDIO"
    exit 1
fi

# 构建 ffmpeg 命令
FFMPEG_CMD="ffmpeg -y"

# 添加视频输入
for video in "${VIDEOS[@]}"; do
    FFMPEG_CMD="$FFMPEG_CMD -i \"$video\""
done

# 添加音频输入（如果指定）
if [ -n "$AUDIO" ]; then
    FFMPEG_CMD="$FFMPEG_CMD -i \"$AUDIO\""
fi

# 构建滤镜链
FILTER_COMPLEX="[0:v]"
AUDIO_FILTER=""

# 构建视频拼接滤镜
for ((i=1; i<${#VIDEOS[@]}; i++)); do
    FILTER_COMPLEX="$FILTER_COMPLEX[$i:v]"
done

FILTER_COMPLEX="$FILTER_COMPLEX concat=n=${#VIDEOS[@]}:v=1[a]"

# 添加音频混合（如果指定）
if [ -n "$AUDIO" ]; then
    AUDIO_INPUT_COUNT=${#VIDEOS[@]}
    AUDIO_FILTER="[${AUDIO_INPUT_COUNT}:a]"
    
    # 构建音频输入
    for ((i=0; i<${#VIDEOS[@]}; i++)); do
        AUDIO_FILTER="$AUDIO_FILTER[$i:a]"
    done
    
    AUDIO_FILTER="$AUDIO_FILTER amix=inputs=$((AUDIO_INPUT_COUNT + 1)):duration=first[b]"
fi

# 构建完整滤镜
if [ -n "$AUDIO" ]; then
    FILTER_COMPLEX="$FILTER_COMPLEX;$AUDIO_FILTER"
fi

# 添加输出映射
FFMPEG_CMD="$FFMPEG_CMD -filter_complex \"$FILTER_COMPLEX\" -map \"[a]\""

# 添加音频映射（如果指定）
if [ -n "$AUDIO" ]; then
    FFMPEG_CMD="$FFMPEG_CMD -map \"[b]\""
fi

# 添加编码参数
FFMPEG_CMD="$FFMPEG_CMD -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k"

# 添加时长限制（如果指定）
if [ -n "$DURATION" ]; then
    FFMPEG_CMD="$FFMPEG_CMD -t $DURATION"
fi

# 添加输出文件
FFMPEG_CMD="$FFMPEG_CMD \"$OUTPUT\""

echo "📝 执行命令:"
echo "$FFMPEG_CMD"
echo ""

# 执行命令
eval $FFMPEG_CMD

echo ""
echo "✅ 混剪完成！"
echo "   输出文件: $OUTPUT"
