#!/bin/bash

# 渲染草稿
# 使用方法: ./render.sh --draft_id "xxx" --resolution "1080P" --framerate "30"

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
DRAFT_ID=""
RESOLUTION="1080P"
FRAMERATE="30"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --draft_id)
            DRAFT_ID="$2"
            shift 2
            ;;
        --resolution)
            RESOLUTION="$2"
            shift 2
            ;;
        --framerate)
            FRAMERATE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$DRAFT_ID" ]; then
    echo "用法: $0 --draft_id <草稿ID> [--resolution <分辨率>] [--framerate <帧率>]"
    echo "默认: resolution=1080P, framerate=30"
    exit 1
fi

echo "🎬 正在发起渲染..."
echo "   Draft ID: $DRAFT_ID"
echo "   分辨率: $RESOLUTION"
echo "   帧率: $FRAMERATE"
echo ""

RESPONSE=$(curl -s -X POST "https://open.vectcut.com/cut_jianying/generate_video" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"draft_id\":\"$DRAFT_ID\",\"resolution\":\"$RESOLUTION\",\"framerate\":\"$FRAMERATE\"}")

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)

echo ""
echo "✅ 渲染任务已提交"
echo "📋 Task ID: $TASK_ID"
echo ""
echo "💾 查询进度: ./check_render.sh --task_id $TASK_ID"
