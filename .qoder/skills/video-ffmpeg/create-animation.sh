#!/bin/bash
# 关键帧动画脚本（基于 Remotion）
#
# 使用方式：
#   ./create-animation.sh --template <template> --params <params> --output <output>
#
# 示例：
#   ./create-animation.sh --template animation.jsx --params '{"text":"Hello World"}' --output animation.mp4
#   ./create-animation.sh --template intro.jsx --params '{"title":"视频标题","subtitle":"副标题"}' --output intro.mp4

set -e

# 默认参数
WIDTH=1920
HEIGHT=1080
FPS=30

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --params)
            PARAMS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "❌ 未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必填参数
if [ -z "$TEMPLATE" ]; then
    echo "用法: $0 --template <template> --params <params> --output <output>"
    echo ""
    echo "示例:"
    echo "  $0 --template animation.jsx --params '{\"text\":\"Hello World\"}' --output animation.mp4"
    echo "  $0 --template intro.jsx --params '{\"title\":\"视频标题\",\"subtitle\":\"副标题\"}' --output intro.mp4"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="animation-$(date +%Y%m%d-%H%M%S).mp4"
fi

echo "🎨 开始创建动画..."
echo "   模板: $TEMPLATE"
echo "   参数: $PARAMS"
echo "   输出: $OUTPUT"
echo ""

# 检查文件是否存在
if [ ! -f "$TEMPLATE" ]; then
    echo "❌ 模板文件不存在: $TEMPLATE"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装:"
    echo "   # macOS"
    echo "   brew install node"
    echo ""
    echo "   # Ubuntu/Debian"
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
fi

# 检查 Remotion 是否安装
if ! command -v npx &> /dev/null; then
    echo "❌ npx 未安装，请先安装 Node.js"
    exit 1
fi

# 检查是否在 Remotion 项目中
if [ ! -f "package.json" ] || ! grep -q "remotion" "package.json"; then
    echo "⚠️  当前目录不是 Remotion 项目"
    echo "💡 建议在 Remotion 项目根目录下使用此脚本"
    echo ""
    echo "初始化 Remotion 项目:"
    echo "   npx create-video@latest my-animation"
    echo "   cd my-animation"
    echo ""
fi

# 生成动画
echo "⏳ 正在生成动画，这可能需要几分钟..."

# 使用 Remotion CLI 渲染视频
npx remotion render "$TEMPLATE" "$OUTPUT" \
  --props="$PARAMS" \
  --width=$WIDTH \
  --height=$HEIGHT \
  --fps=$FPS \
  --overwrite

echo ""
echo "✅ 动画创建完成！"
echo "   输出文件: $OUTPUT"
echo "   分辨率: ${WIDTH}x${HEIGHT}"
echo "   帧率: $FPS fps"
