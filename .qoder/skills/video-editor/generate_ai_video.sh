#!/bin/bash

# 生成 AI 视频
# 使用方法: ./generate_ai_video.sh --prompt "提示词" --model "模型" --resolution "1080P"

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
PROMPT=""
MODEL=""
RESOLUTION="1080P"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --resolution)
            RESOLUTION="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$PROMPT" ]; then
    echo "用法: $0 --prompt <提示词> [--model <模型>] [--resolution <分辨率>]"
    echo "默认: model=runway, resolution=1080P"
    exit 1
fi

echo "🤖  正在生成 AI 视频..."
echo "   提示词: $PROMPT"
echo "   模型: ${MODEL:-runway}"
echo "   分辨率: $RESOLUTION"
echo ""

RESPONSE=$(curl -s -X POST "https://open.vectcut.com/cut_jianying/generate_ai_video" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\":\"$PROMPT\",\"model\":\"$MODEL\",\"resolution\":\"$RESOLUTION\"}")

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)

echo ""
echo "✅ AI 视频生成任务已提交"
echo "📋 Task ID: $TASK_ID"
echo ""
echo "💾 查询状态: ./check_ai_video.sh --task_id $TASK_ID"
