#!/bin/bash

# 创建剪映草稿
# 使用方法: ./create_draft.sh --name "草稿名称" --width 1080 --height 1920

VECTCUT_API_KEY="${VECTCUT_API_KEY:-}"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 错误: 请设置 VECTCUT_API_KEY 环境变量"
    exit 1
fi

# 解析参数
NAME=""
WIDTH=1080
HEIGHT=1920

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name)
            NAME="$2"
            shift 2
            ;;
        --width)
            WIDTH="$2"
            shift 2
            ;;
        --height)
            HEIGHT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$NAME" ]; then
    echo "用法: $0 --name <草稿名称> [--width <宽度>] [--height <高度>]"
    echo "默认分辨率: 1080x1920 (竖屏)"
    exit 1
fi

echo "🎬 正在创建草稿..."
echo "   名称: $NAME"
echo "   分辨率: ${WIDTH}x${HEIGHT}"
echo ""

curl -X POST "https://open.vectcut.com/cut_jianying/create_draft" \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$NAME\",\"width\":$WIDTH,\"height\":$HEIGHT}"

echo ""
echo "✅ 草稿创建完成"
echo "💾 请保存返回的 draft_id 和 draft_url"
