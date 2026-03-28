#!/bin/bash
# 快速视频混剪脚本
#
# 使用方式：
#   ./quick-mix.sh <output_name> <width> <height>
#
# 示例：
#   ./quick-mix.sh "我的混剪" 1080 1920

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 请先设置环境变量 VECTCUT_API_KEY"
    echo "export VECTCUT_API_KEY=\"your_api_key\""
    exit 1
fi

OUTPUT_NAME=${1:-"混剪视频"}
WIDTH=${2:-1080}
HEIGHT=${3:-1920}

echo "🎬 开始创建混剪视频..."
echo "   名称: $OUTPUT_NAME"
echo "   尺寸: ${WIDTH}x${HEIGHT}"
echo ""

# 创建草稿
echo "📝 步骤 1/5: 创建草稿..."
DRAFT_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/create_draft \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$OUTPUT_NAME\",\"width\":$WIDTH,\"height\":$HEIGHT}")

DRAFT_ID=$(echo "$DRAFT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('draft_id',''))" 2>/dev/null)
DRAFT_URL=$(echo "$DRAFT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('draft_url',''))" 2>/dev/null)

if [ -z "$DRAFT_ID" ]; then
    echo "❌ 创建草稿失败"
    echo "$DRAFT_RESPONSE"
    exit 1
fi

echo "✅ 草稿创建成功"
echo "   Draft ID: $DRAFT_ID"
echo "   Draft URL: $DRAFT_URL"
echo ""

# 提示用户继续添加素材
echo "📌 接下来请手动添加素材："
echo ""
echo "添加视频（示例）："
echo "curl -X POST http://open.vectcut.com/cut_jianying/add_video \\"
echo "  -H \"Authorization: Bearer \$VECTCUT_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"draft_id\":\"$DRAFT_ID\",\"video_url\":\"https://example.com/video.mp4\",\"start\":0,\"end\":10,\"target_start\":0}'"
echo ""
echo "添加音频（示例）："
echo "curl -X POST http://open.vectcut.com/cut_jianying/add_audio \\"
echo "  -H \"Authorization: Bearer \$VECTCUT_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"draft_id\":\"$DRAFT_ID\",\"audio_url\":\"https://example.com/bgm.mp3\",\"volume\":0.3}'"
echo ""
echo "渲染视频（示例）："
echo "curl -X POST http://open.vectcut.com/cut_jianying/generate_video \\"
echo "  -H \"Authorization: Bearer \$VECTCUT_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"draft_id\":\"$DRAFT_ID\",\"resolution\":\"1080P\"}'"
echo ""

# 保存 draft_id 到文件
echo "$DRAFT_ID" > /tmp/current_draft_id.txt
echo "💾 Draft ID 已保存到 /tmp/current_draft_id.txt"
echo ""
echo "✨ 准备完成！可以开始添加素材了"
