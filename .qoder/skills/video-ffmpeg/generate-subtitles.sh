#!/bin/bash
# 字幕生成脚本（基于 Whisper）
#
# 使用方式：
#   ./generate-subtitles.sh --input <input> --model <model> --output <output>
#
# 示例：
#   ./generate-subtitles.sh --input video.mp4 --model base --output subtitles.srt
#   ./generate-subtitles.sh --input video.mp4 --model tiny --output subtitles.srt

set -e

# 默认参数
MODEL="base"
OUTPUT_FORMAT="srt"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
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
if [ -z "$INPUT" ]; then
    echo "用法: $0 --input <input> --model <model> --output <output>"
    echo ""
    echo "示例:"
    echo "  $0 --input video.mp4 --model base --output subtitles.srt"
    echo "  $0 --input video.mp4 --model tiny --output subtitles.srt"
    echo ""
    echo "模型选项:"
    echo "  tiny   - 最快，精度较低"
    echo "  base   - 快速，精度中等"
    echo "  small  - 中等速度，精度较高"
    echo "  medium - 较慢，精度很高"
    echo "  large  - 最慢，精度最高"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="subtitles-$(date +%Y%m%d-%H%M%S).srt"
fi

echo "📝 开始生成字幕..."
echo "   输入: $INPUT"
echo "   模型: $MODEL"
echo "   输出: $OUTPUT"
echo ""

# 检查文件是否存在
if [ ! -f "$INPUT" ]; then
    echo "❌ 文件不存在: $INPUT"
    exit 1
fi

# 检查 whisper 是否安装
if ! command -v whisper &> /dev/null; then
    echo "❌ whisper 未安装，请先安装:"
    echo "   pip3 install openai-whisper"
    exit 1
fi

# 执行 ASR
whisper "$INPUT" --model "$MODEL" --output_format "$OUTPUT_FORMAT" --output_dir "$(dirname "$OUTPUT")" --output_filename "$(basename "$OUTPUT" ."$OUTPUT_FORMAT")"

echo ""
echo "✅ 字幕生成完成！"
echo "   输出文件: $OUTPUT"
