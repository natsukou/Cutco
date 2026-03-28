#!/bin/bash
# AI 视频生成脚本（基于 Stable Video Diffusion）
#
# 使用方式：
#   ./generate-ai-video.sh --prompt <prompt> --duration <duration> --output <output> [--image <image>]
#
# 示例：
#   ./generate-ai-video.sh --prompt "一只可爱的小狗在公园里" --duration 5 --output ai-video.mp4
#   ./generate-ai-video.sh --prompt "人物行走" --duration 3 --output ai-video.mp4 --image person.jpg

set -e

# 默认参数
DURATION=5
FPS=30
WIDTH=1024
HEIGHT=576

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --image)
            IMAGE="$2"
            shift 2
            ;;
        *)
            echo "❌ 未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必填参数
if [ -z "$PROMPT" ]; then
    echo "用法: $0 --prompt <prompt> --duration <duration> --output <output> [--image <image>]"
    echo ""
    echo "示例:"
    echo "  $0 --prompt \"一只可爱的小狗在公园里\" --duration 5 --output ai-video.mp4"
    echo "  $0 --prompt \"人物行走\" --duration 3 --output ai-video.mp4 --image person.jpg"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="ai-video-$(date +%Y%m%d-%H%M%S).mp4"
fi

echo "🎥 开始生成 AI 视频..."
echo "   提示: $PROMPT"
echo "   时长: $DURATION 秒"
echo "   输出: $OUTPUT"
if [ -n "$IMAGE" ]; then
    echo "   输入图片: $IMAGE"
fi
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查是否安装了 Stable Video Diffusion
if ! python3 -c "import torch" 2>/dev/null; then
    echo "❌ PyTorch 未安装，请先安装:"
    echo "   pip3 install torch torchvision"
    exit 1
fi

# 检查图片文件是否存在（如果指定）
if [ -n "$IMAGE" ] && [ ! -f "$IMAGE" ]; then
    echo "❌ 图片文件不存在: $IMAGE"
    exit 1
fi

# 生成 AI 视频
echo "⏳ 正在生成视频，这可能需要几分钟..."

# 创建 Python 脚本生成视频
python3 << PYTHON_SCRIPT
import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video

# 加载模型
print("📦 加载模型...")
pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# 准备输入
if "$IMAGE":
    # 图生视频
    from PIL import Image
    image = Image.open("$IMAGE").convert("RGB")
    print("🖼️  加载输入图片...")
else:
    # 文生视频（需要先生成图片）
    print "⚠️  文生视频需要先使用文生图模型，当前仅支持图生视频"
    print "💡 提示: 请使用 --image 参数指定输入图片"
    exit(1)

# 生成视频
print("🎥 生成视频中...")
frames = pipe(image, decode_chunk_size=8, num_frames=$((DURATION * FPS))).frames[0]

# 保存视频
print("💾 保存视频...")
export_to_video(frames, "$OUTPUT", fps=$FPS)
print(f"✅ 视频已保存: $OUTPUT")
PYTHON_SCRIPT

echo ""
echo "✅ AI 视频生成完成！"
echo "   输出文件: $OUTPUT"
echo "   时长: $DURATION 秒"
echo "   帧率: $FPS fps"
