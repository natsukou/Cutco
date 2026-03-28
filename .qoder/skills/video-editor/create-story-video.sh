#!/bin/bash
# 创建故事视频（文生图 + 配音）
#
# 使用方式：
#   ./create-story-video.sh <story_name> <segments_file>
#
# segments_file 格式（每行一个片段）：
#   prompt|text
#
# 示例：
#   cat << 'EOF' > segments.txt
#   一只可爱的小兔子在草地上玩耍，阳光明媚|今天天气真好，小兔子来到草地上玩耍。
#   小兔子发现了一根胡萝卜，开心地跳起来|哇！这里有一根大胡萝卜！
#   小兔子抱着胡萝卜开心地跑回家|我要带回家和妈妈一起分享。
#   EOF
#   ./create-story-video.sh "小兔子的故事" segments.txt

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 请先设置环境变量 VECTCUT_API_KEY"
    exit 1
fi

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "用法: $0 <story_name> <segments_file>"
    echo ""
    echo "segments_file 格式（每行一个片段）："
    echo "  prompt|text"
    echo ""
    echo "示例："
    echo "  cat << 'EOF' > segments.txt"
    echo "  一只可爱的小兔子在草地上玩耍|今天天气真好。"
    echo "  小兔子发现了一根胡萝卜|哇，这里有胡萝卜！"
    echo "  EOF"
    echo "  $0 \"小兔子的故事\" segments.txt"
    exit 1
fi

STORY_NAME=$1
SEGMENTS_FILE=$2

if [ ! -f "$SEGMENTS_FILE" ]; then
    echo "❌ 文件不存在: $SEGMENTS_FILE"
    exit 1
fi

echo "🎬 开始创建故事视频..."
echo "   故事: $STORY_NAME"
echo "   片段文件: $SEGMENTS_FILE"
echo ""

# 创建草稿
echo "📝 步骤 1/4: 创建草稿..."
DRAFT_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/create_draft \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$STORY_NAME\",\"width\":1080,\"height\":1920}")

DRAFT_ID=$(echo "$DRAFT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('draft_id',''))" 2>/dev/null)

if [ -z "$DRAFT_ID" ]; then
    echo "❌ 创建草稿失败"
    echo "$DRAFT_RESPONSE"
    exit 1
fi

echo "✅ 草稿创建成功 (Draft ID: $DRAFT_ID)"
echo ""

# 读取并处理片段
echo "📝 步骤 2/4: 生成插图和配音..."
echo ""

CURRENT_TIME=0
SEGMENT_NUM=0

while IFS='|' read -r PROMPT TEXT; do
    SEGMENT_NUM=$((SEGMENT_NUM + 1))

    # 跳过空行
    if [ -z "$PROMPT" ] || [ -z "$TEXT" ]; then
        continue
    fi

    echo "🎨 片段 $SEGMENT_NUM: ${TEXT:0:30}..."

    # 生成图片
    IMAGE_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/generate_image \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"draft_id\":\"$DRAFT_ID\",\"prompt\":\"$PROMPT\",\"model\":\"nano_banana_pro\"}")

    IMAGE_URL=$(echo "$IMAGE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('image_url',''))" 2>/dev/null)

    if [ -z "$IMAGE_URL" ]; then
        echo "   ❌ 图片生成失败"
        continue
    fi

    echo "   ✅ 图片生成成功"

    # 生成配音
    VOICE_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/generate_speech \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"$TEXT\",\"draft_id\":\"$DRAFT_ID\",\"provider\":\"minimax\",\"model\":\"speech-01\",\"voice_id\":\"female_tianmei\"}")

    AUDIO_URL=$(echo "$VOICE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('audio_url',''))" 2>/dev/null)

    if [ -z "$AUDIO_URL" ]; then
        echo "   ❌ 配音生成失败"
        continue
    fi

    echo "   ✅ 配音生成成功"

    # 获取音频时长
    DURATION_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/get_duration \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"url\":\"$AUDIO_URL\"}")

    DURATION=$(echo "$DURATION_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('duration',0))" 2>/dev/null)

    echo "   ⏱️  音频时长: ${DURATION} 秒"

    # 添加图片到草稿（时长对齐配音）
    ADD_IMAGE_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/add_image \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"draft_id\":\"$DRAFT_ID\",\"image_url\":\"$IMAGE_URL\",\"duration\":$DURATION,\"target_start\":$CURRENT_TIME}")

    if echo "$ADD_IMAGE_RESPONSE" | grep -q '"code":0'; then
        echo "   ✅ 图片添加成功（位置: ${CURRENT_TIME}s）"
    else
        echo "   ❌ 图片添加失败"
    fi

    # 添加字幕
    ADD_TEXT_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/add_text \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"draft_id\":\"$DRAFT_ID\",\"text\":\"$TEXT\",\"start\":$CURRENT_TIME,\"end\":$(echo "$CURRENT_TIME + $DURATION" | bc),\"style\":{\"font_size\":32,\"color\":\"#FFFFFF\",\"background_color\":\"#00000080\",\"y\":0.8}}")

    if echo "$ADD_TEXT_RESPONSE" | grep -q '"code":0'; then
        echo "   ✅ 字幕添加成功"
    else
        echo "   ⚠️  字幕添加失败（可选）"
    fi

    CURRENT_TIME=$(echo "$CURRENT_TIME + $DURATION" | bc)
    echo ""
done

echo "📝 步骤 3/4: 查询草稿结构..."
QUERY_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/query_script \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"draft_id\":\"$DRAFT_ID\"}")

echo "$QUERY_RESPONSE" | python3 -m json.tool > /tmp/story_draft_structure.json
echo "✅ 草稿结构已保存到 /tmp/story_draft_structure.json"
echo ""

echo "📝 步骤 4/4: 渲染视频..."
echo "⏳ 这可能需要 2-5 分钟，请耐心等待..."

RENDER_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/generate_video \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"draft_id\":\"$DRAFT_ID\",\"resolution\":\"1080P\"}")

TASK_ID=$(echo "$RENDER_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('task_id',''))" 2>/dev/null)

if [ -z "$TASK_ID" ]; then
    echo "❌ 渲染任务创建失败"
    echo "$RENDER_RESPONSE"
    exit 1
fi

echo "✅ 渲染任务创建成功 (Task ID: $TASK_ID)"
echo ""
echo "⏳ 轮询渲染进度..."

# 轮询任务状态
while true; do
    sleep 10

    STATUS_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/task_status \
        -H "Authorization: Bearer $VECTCUT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"task_id\":\"$TASK_ID\"}")

    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('status',''))" 2>/dev/null)
    PROGRESS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('progress',0))" 2>/dev/null)

    echo "   状态: $STATUS | 进度: $PROGRESS%"

    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "🎉 渲染完成！"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ 渲染失败"
        echo "$STATUS_RESPONSE"
        exit 1
    fi
done

# 获取视频链接
VIDEO_URL=$(echo "$STATUS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('video_url',''))" 2>/dev/null)
DRAFT_URL=$(echo "$DRAFT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('draft_url',''))" 2>/dev/null)

echo ""
echo "✅ 故事视频创建完成！"
echo ""
echo "📋 结果信息："
echo "   视频链接: [$VIDEO_URL]($VIDEO_URL)"
echo "   Draft URL: [$STORY_NAME]($DRAFT_URL)"
echo "   Draft ID: $DRAFT_ID"
echo "   Task ID: $TASK_ID"
echo ""
echo "💡 可以在剪映/CapCut 中打开草稿继续编辑"
