#!/bin/bash
# 生成 TTS 配音脚本
#
# 使用方式：
#   ./generate-voiceover.sh <text> [draft_id]
#
# 示例：
#   ./generate-voiceover.sh "今天天气真好，小兔子来到草地上玩耍。"
#   ./generate-voiceover.sh "欢迎观看我的视频！" "draft_123"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 请先设置环境变量 VECTCUT_API_KEY"
    exit 1
fi

if [ -z "$1" ]; then
    echo "用法: $0 <text> [draft_id]"
    echo ""
    echo "示例:"
    echo "  $0 \"今天天气真好，小兔子来到草地上玩耍。\""
    echo "  $0 \"欢迎观看我的视频！\" \"draft_123\""
    exit 1
fi

TEXT=$1
DRAFT_ID=$2

echo "🎬 开始生成配音..."
echo "   文案: $TEXT"
echo "   草稿: ${DRAFT_ID:-无（仅生成音频）}"
echo ""

# 构建 JSON payload
if [ -n "$DRAFT_ID" ]; then
    PAYLOAD="{\"text\":\"$TEXT\",\"draft_id\":\"$DRAFT_ID\",\"provider\":\"minimax\",\"model\":\"speech-01\",\"voice_id\":\"female_tianmei\"}"
else
    PAYLOAD="{\"text\":\"$TEXT\",\"provider\":\"minimax\",\"model\":\"speech-01\",\"voice_id\":\"female_tianmei\"}"
fi

# 生成配音
echo "📝 生成配音中..."
RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/generate_speech \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# 保存响应
echo "$RESPONSE" > /tmp/voiceover_result.json

# 解析结果
CODE=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',-1))" 2>/dev/null)

if [ "$CODE" = "0" ]; then
    echo "✅ 配音生成成功！"
    echo ""

    # 提取信息
    AUDIO_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('audio_url',''))" 2>/dev/null)
    MATERIAL_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('material_id',''))" 2>/dev/null)

    if [ -n "$DRAFT_ID" ]; then
        # 返回草稿信息
        RESULT_DRAFT_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('draft_id',''))" 2>/dev/null)
        RESULT_DRAFT_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('draft_url',''))" 2>/dev/null)

        echo "📋 结果信息："
        echo "   Audio URL: $AUDIO_URL"
        echo "   Material ID: $MATERIAL_ID"
        echo "   Draft ID: $RESULT_DRAFT_ID"
        echo "   Draft URL: $RESULT_DRAFT_URL"
        echo ""
        echo "💡 配音已自动添加到草稿！"
    else
        # 仅返回音频 URL
        echo "📋 结果信息："
        echo "   Audio URL: $AUDIO_URL"
        echo ""
        echo "💡 可以使用以下命令添加到草稿："
        echo "curl -X POST http://open.vectcut.com/cut_jianying/add_audio \\"
        echo "  -H \"Authorization: Bearer \$VECTCUT_API_KEY\" \\"
        echo "  -H \"Content-Type: application/json\" \\"
        echo "  -d '{\"draft_id\":\"<your_draft_id>\",\"audio_url\":\"$AUDIO_URL\"}'"
    fi

    # 获取音频时长
    echo ""
    echo "📊 获取音频时长..."
    DURATION_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/get_duration \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"url\":\"$AUDIO_URL\"}")

    DURATION=$(echo "$DURATION_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('duration',0))" 2>/dev/null)
    echo "   音频时长: ${DURATION} 秒"
    echo ""
    echo "💡 提示：图片/视频时长可以设置为 $DURATION 秒以实现音画对齐"

else
    echo "❌ 配音生成失败"
    echo "$RESPONSE"
    exit 1
fi
