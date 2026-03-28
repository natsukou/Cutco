#!/bin/bash
# 自动为视频添加字幕脚本
#
# 使用方式：
#   ./add-subtitles.sh <video_url> <draft_id>
#
# 示例：
#   ./add-subtitles.sh "https://example.com/video.mp4" "draft_123"

if [ -z "$VECTCUT_API_KEY" ]; then
    echo "❌ 请先设置环境变量 VECTCUT_API_KEY"
    exit 1
fi

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "用法: $0 <video_url> <draft_id>"
    echo ""
    echo "示例:"
    echo "  $0 \"https://example.com/video.mp4\" \"draft_123\""
    exit 1
fi

VIDEO_URL=$1
DRAFT_ID=$2

echo "🎬 开始为视频添加字幕..."
echo "   视频: $VIDEO_URL"
echo "   草稿: $DRAFT_ID"
echo ""

# 步骤 1: 使用 ASR 识别语音
echo "📝 步骤 1/3: 识别语音（使用 asr_llm）..."
ASR_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/asr_llm \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"video_url\":\"$VIDEO_URL\"}")

echo "$ASR_RESPONSE" > /tmp/asr_result.json

# 检查是否成功
if echo "$ASR_RESPONSE" | grep -q '"code":0'; then
    echo "✅ 语音识别成功"
    SEGMENT_COUNT=$(echo "$ASR_RESPONSE" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('output',{}).get('segments',[])))" 2>/dev/null)
    echo "   识别到 $SEGMENT_COUNT 个片段"
else
    echo "❌ 语音识别失败"
    echo "$ASR_RESPONSE"
    exit 1
fi
echo ""

# 步骤 2: 添加视频到草稿（如果还没有）
echo "📝 步骤 2/3: 添加视频到草稿..."
ADD_VIDEO_RESPONSE=$(curl -s -X POST http://open.vectcut.com/cut_jianying/add_video \
    -H "Authorization: Bearer $VECTCUT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"draft_id\":\"$DRAFT_ID\",\"video_url\":\"$VIDEO_URL\"}")

if echo "$ADD_VIDEO_RESPONSE" | grep -q '"code":0'; then
    echo "✅ 视频添加成功"
else
    echo "⚠️  视频添加可能失败（可能已经存在）"
fi
echo ""

# 步骤 3: 批量添加字幕
echo "📝 步骤 3/3: 批量添加字幕..."

# 提取 segments 并为每个添加字幕
python3 << PYTHON_SCRIPT
import json
import sys

# 读取 ASR 结果
with open('/tmp/asr_result.json', 'r') as f:
    asr_data = json.load(f)

segments = asr_data.get('output', {}).get('segments', [])

if not segments:
    print("❌ 没有找到字幕片段")
    sys.exit(1)

print(f"📊 准备添加 {len(segments)} 条字幕...")
print("")

for i, segment in enumerate(segments):
    text = segment.get('text', '').strip()
    start = segment.get('start_time', 0)
    end = segment.get('end_time', 0)

    if not text:
        continue

    # 调用 add_text API
    import subprocess

    payload = json.dumps({
        "draft_id": "$DRAFT_ID",
        "text": text,
        "start": start,
        "end": end,
        "style": {
            "font_size": 28,
            "color": "#FFFFFF",
            "background_color": "#00000080",
            "y": 0.8
        }
    })

    response = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'http://open.vectcut.com/cut_jianying/add_text',
        '-H', 'Authorization: Bearer ' + '$VECTCUT_API_KEY',
        '-H', 'Content-Type: application/json',
        '-d', payload
    ], capture_output=True, text=True)

    try:
        result = json.loads(response.stdout)
        if result.get('code') == 0:
            print(f"✅ [{i+1}/{len(segments)}] {text[:30]}...")
        else:
            print(f"❌ [{i+1}/{len(segments)}] {text[:30]}... (失败)")
    except:
        print(f"⚠️  [{i+1}/{len(segments)}] {text[:30]}... (解析失败)")

print("")
print("✅ 字幕添加完成！")
print("📝 草稿 ID: $DRAFT_ID")
print("💡 可以在剪映/CapCut 中打开继续编辑")
PYTHON_SCRIPT
