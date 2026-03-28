#!/bin/bash

# 生成语音（TTS）
# 使用方法: ./generate_speech.sh --text "文本内容" --provider "minimax" --model "speech-01" --voice_id "xxx"

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
TEXT=""
PROVIDER="minimax"
MODEL="speech-01"
VOICE_ID=""
VOLUME=1.0
TARGET_START=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --text)
            TEXT="$2"
            shift 2
            ;;
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --voice_id)
            VOICE_ID="$2"
            shift 2
            ;;
        --volume)
            VOLUME="$2"
            shift 2
            ;;
        --target_start)
            TARGET_START="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$TEXT" ]; then
    echo "用法: $0 --text <文本内容> [--provider <服务商>] [--model <模型>] [--voice_id <音色ID>]"
    echo "默认: provider=minimax, model=speech-01"
    exit 1
fi

echo "🎙️  正在生成语音..."
echo "   文本: $TEXT"
echo "   服务商: $PROVIDER"
echo "   模型: $MODEL"
echo ""

curl -X POST "https://open.vectcut.com/cut_jianying/generate_speech" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"$TEXT\",\"provider\":\"$PROVIDER\",\"model\":\"$MODEL\",\"voice_id\":\"$VOICE_ID\",\"volume\":$VOLUME,\"target_start\":$TARGET_START}"

echo ""
echo "✅ 语音生成完成"
