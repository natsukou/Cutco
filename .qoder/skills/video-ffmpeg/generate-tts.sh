#!/bin/bash
# 配音生成脚本（基于 edge-tts）
#
# 使用方式：
#   ./generate-tts.sh --text <text> --voice <voice> --output <output> [--speed <speed>] [--pitch <pitch>]
#
# 示例：
#   ./generate-tts.sh --text "今天天气真好" --voice zh-CN-XiaoxiaoNeural --output audio.wav
#   ./generate-tts.sh --text "欢迎观看我的视频" --voice zh-CN-YunxiNeural --output audio.mp3 --speed 1.2

set -e

# 默认参数
VOICE="zh-CN-XiaoxiaoNeural"
SPEED="1.0"
PITCH="0"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --text)
            TEXT="$2"
            shift 2
            ;;
        --voice)
            VOICE="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --speed)
            SPEED="$2"
            shift 2
            ;;
        --pitch)
            PITCH="$2"
            shift 2
            ;;
        *)
            echo "❌ 未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必填参数
if [ -z "$TEXT" ]; then
    echo "用法: $0 --text <text> --voice <voice> --output <output> [--speed <speed>] [--pitch <pitch>]"
    echo ""
    echo "示例:"
    echo "  $0 --text \"今天天气真好\" --voice zh-CN-XiaoxiaoNeural --output audio.wav"
    echo "  $0 --text \"欢迎观看我的视频\" --voice zh-CN-YunxiNeural --output audio.mp3 --speed 1.2"
    echo ""
    echo "常用音色:"
    echo "  zh-CN-XiaoxiaoNeural  - 小晓（女）"
    echo "  zh-CN-YunxiNeural     - 云希（男）"
    echo "  zh-CN-XiaoyiNeural    - 小艺（女）"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    # 根据扩展名确定输出格式
    OUTPUT="audio-$(date +%Y%m%d-%H%M%S).wav"
fi

echo "🎙️  开始生成配音..."
echo "   文案: $TEXT"
echo "   音色: $VOICE"
echo "   语速: $SPEED"
echo "   音调: $PITCH"
echo "   输出: $OUTPUT"
echo ""

# 检查 edge-tts 是否安装
if ! command -v edge-tts &> /dev/null; then
    echo "❌ edge-tts 未安装，请先安装:"
    echo "   pip3 install edge-tts"
    exit 1
fi

# 执行 TTS
edge-tts \
  --text "$TEXT" \
  --voice "$VOICE" \
  --rate "+$((($SPEED - 1) * 100))%" \
  --pitch "+${PITCH}Hz" \
  --write-media "$OUTPUT"

echo ""
echo "✅ 配音生成完成！"
echo "   输出文件: $OUTPUT"
