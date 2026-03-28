#!/bin/bash

# 查询 AI 视频生成状态
# 使用方法: ./check_ai_video.sh --task_id "xxx"

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
TASK_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --task_id)
            TASK_ID="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$TASK_ID" ]; then
    echo "用法: $0 --task_id <任务ID>"
    exit 1
fi

echo "🔍 正在查询任务状态..."
echo "   Task ID: $TASK_ID"
echo ""

RESPONSE=$(curl -s -X POST "https://open.vectcut.com/cut_jianying/aivideo/task_status" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"task_id\":\"$TASK_ID\"}")

echo $RESPONSE | python3 -m json.tool

echo ""
echo "💾 视频链接: $(echo $RESPONSE | grep -o '"video_url":"[^"]*' | cut -d'"' -f4)"
