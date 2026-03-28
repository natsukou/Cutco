---
name: video-ffmpeg
description: 本地视频剪辑专家。当用户提到"剪视频"、"剪辑视频"、"混剪"、"裁剪视频"、"生成视频"、"AI 视频"、"配音"、"字幕"、"视频处理"、"视频编辑"、"ffmpeg"、"本地剪辑"等关键词时触发。完全基于 ffmpeg 和本地工具实现，无需任何 API 依赖。支持素材混剪、视频裁剪、配音生成、字幕生成、AI 视频生成、关键帧动画等完整视频创作流程。
metadata:
  openclaw:
    emoji: "🎬"
---

# Video FFmpeg Skill - 本地视频剪辑专家

本技能提供完全基于本地工具的视频剪辑能力，无需任何外部 API 依赖。支持完整的视频创作流程，从素材混剪到 AI 视频。

## 核心能力

### 1️⃣ 素材混剪
将多个视频、音频、文本素材组合成一个完整的视频。

**技术实现**：
- `ffmpeg -i input1.mp4 -i input2.mp4` - 多输入
- `filter_complex` - 复杂滤镜链
- `concat` - 视频拼接
- `amix` - 音频混合
- `drawtext` - 文字叠加

**输出格式**：
- 支持任意分辨率
- 支持任意帧率
- 支持多种编码格式

---

### 2️⃣ 视频裁剪
按时间段切分视频，提取需要的片段。

**技术实现**：
- `ffmpeg -i input.mp4 -ss 00:00:10 -to 00:00:20` - 时间段裁剪
- `trim` 滤镜 - 精确帧级裁剪
- `select` 滤镜 - 帧选择

**输出格式**：
- 精确到帧
- 支持时间码格式
- 支持帧数格式

---

### 3️⃣ 配音生成
使用 TTS（Text-to-Speech）生成配音。

**技术实现**：
- **edge-tts** - 微软 Edge TTS（免费，高质量）
- **espeak** - 本地 TTS（快速）
- **festival** - 本地 TTS（可定制）
- **OpenAI TTS API** - 可选（需要 API Key）

**输出格式**：
- WAV、MP3、AAC
- 多种音色选择
- 语速、音调调整

---

### 4️⃣ 字幕生成
使用 ASR（Automatic Speech Recognition）识别语音并生成字幕。

**技术实现**：
- **OpenAI Whisper** - 本地运行（高精度）
- **faster-whisper** - Whisper 优化版本（快速）
- **vosk** - 轻量级离线 ASR
- **DeepSpeech** - Mozilla ASR

**输出格式**：
- SRT 格式（通用）
- ASS 格式（高级）
- VTT 格式（Web 字幕）

---

### 5️⃣ AI 视频生成
文生视频、图生视频。

**技术实现**：
- **Stable Video Diffusion** - 本地运行（需要 GPU）
- **API 服务** - 可选调用外部 API
  - RunwayML
  - Pika Labs
  - Stability AI

**输出格式**：
- MP4、MOV
- 支持任意分辨率
- 支持多种时长

---

### 6️⃣ 关键帧动画
为素材添加动画效果，使用 Remotion。

**技术实现**：
- **Remotion** - React 视频动画库
- **React** - 组件化动画
- **Framer Motion** - 动画库

**输出格式**：
- MP4、MOV、GIF
- 支持复杂动画
- 支持交互式设计

---

## 快速开始

### 环境依赖

```bash
# 必需工具
ffmpeg -version          # 视频处理
python3 --version        # Python 脚本

# 可选工具
edge-tts --version       # TTS
whisper --version        # ASR
node --version           # Remotion
remotion --version       # 视频动画
```

**安装依赖**：

```bash
# 安装 ffmpeg
# Ubuntu/Debian
apt-get install ffmpeg

# macOS
brew install ffmpeg

# 安装 Python 工具
pip3 install edge-tts openai-whisper

# 安装 Remotion
npm install remotion
```

---

## 工作流

### 工作流 1：快速混剪

```bash
./scripts/quick-mix.sh \
  --videos video1.mp4 video2.mp4 \
  --audio bgm.mp3 \
  --output output.mp4 \
  --duration 30
```

**功能**：
- 多视频拼接
- 音频混合
- 自动转场
- 统一编码

---

### 工作流 2：视频裁剪

```bash
./scripts/trim-video.sh \
  --input video.mp4 \
  --start 00:00:10 \
  --end 00:00:30 \
  --output clip.mp4
```

**功能**：
- 精确时间段裁剪
- 帧级精度
- 无重编码（快速）

---

### 工作流 3：配音生成

```bash
./scripts/generate-tts.sh \
  --text "今天天气真好" \
  --voice zh-CN-XiaoxiaoNeural \
  --output audio.wav
```

**功能**：
- 文本转语音
- 多种音色
- 语速调整

---

### 工作流 4：字幕生成

```bash
./scripts/generate-subtitles.sh \
  --input video.mp4 \
  --model base \
  --output subtitles.srt
```

**功能**：
- 语音识别
- 时间轴生成
- 格式转换

---

### 工作流 5：AI 视频生成

```bash
./scripts/generate-ai-video.sh \
  --prompt "一只可爱的小狗在公园里" \
  --duration 5 \
  --output ai-video.mp4
```

**功能**：
- 文生视频
- 图生视频
- 可自定义时长

---

### 工作流 6：关键帧动画

```bash
./scripts/create-animation.sh \
  --template animation.jsx \
  --params '{"text":"Hello World"}' \
  --output animation.mp4
```

**功能**：
- React 组件动画
- 关键帧控制
- 复杂效果

---

## 核心脚本

### quick-mix.sh

快速混剪脚本，支持多视频、音频拼接。

```bash
./quick-mix.sh \
  --videos <video1> <video2> ... \
  --audio <audio> \
  --output <output> \
  [--duration <seconds>] \
  [--transition <type>]
```

**参数**：
- `--videos` - 视频文件列表
- `--audio` - 背景音乐
- `--output` - 输出文件
- `--duration` - 总时长（秒）
- `--transition` - 转场类型

**转场类型**：
- `fade` - 淡入淡出
- `wipe` - 擦除
- `slide` - 滑动

---

### trim-video.sh

视频裁剪脚本。

```bash
./trim-video.sh \
  --input <input> \
  --start <start_time> \
  --end <end_time> \
  --output <output>
```

**时间格式**：
- `HH:MM:SS` - 时间码
- `N` - 第 N 秒
- `N:M` - 第 N 分 M 秒

---

### generate-tts.sh

配音生成脚本。

```bash
./generate-tts.sh \
  --text <text> \
  --voice <voice> \
  --output <output> \
  [--speed <speed>] \
  [--pitch <pitch>]
```

**音色选项**：
- `zh-CN-XiaoxiaoNeural` - 小晓（女）
- `zh-CN-YunxiNeural` - 云希（男）
- `zh-CN-XiaoyiNeural` - 小艺（女）

---

### generate-subtitles.sh

字幕生成脚本。

```bash
./generate-subtitles.sh \
  --input <input> \
  --model <model> \
  --output <output>
```

**模型选项**：
- `tiny` - 最快，精度较低
- `base` - 快速，精度中等
- `small` - 中等速度，精度较高
- `medium` - 较慢，精度很高
- `large` - 最慢，精度最高

---

### generate-ai-video.sh

AI 视频生成脚本。

```bash
./generate-ai-video.sh \
  --prompt <prompt> \
  --duration <duration> \
  --output <output> \
  [--image <image>]
```

**参数**：
- `--prompt` - 文本提示
- `--image` - 输入图片（图生视频）
- `--duration` - 视频时长（秒）

---

### create-animation.sh

关键帧动画脚本。

```bash
./create-animation.sh \
  --template <template> \
  --params <params> \
  --output <output>
```

**参数**：
- `--template` - Remotion 模板文件
- `--params` - JSON 格式的参数
- `--output` - 输出视频

---

## 技术细节

### FFmpeg 基础命令

#### 视频裁剪

```bash
# 时间码格式
ffmpeg -i input.mp4 -ss 00:00:10 -to 00:00:20 -c:v libx264 -c:a aac output.mp4

# 秒数格式
ffmpeg -i input.mp4 -ss 10 -to 20 -c:v libx264 -c:a aac output.mp4
```

#### 视频拼接

```bash
# 使用 concat 滤镜
ffmpeg -i video1.mp4 -i video2.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" output.mp4
```

#### 音频混合

```bash
# 混合两个音频
ffmpeg -i audio1.mp3 -i audio2.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first[outa]" \
  -map "[outa]" output.mp3
```

#### 文字叠加

```bash
# 添加字幕
ffmpeg -i input.mp4 \
  -vf "drawtext=text='Hello World':fontsize=24:fontcolor=white:x=10:y=10" \
  -c:a copy output.mp4
```

---

### TTS 技术实现

#### edge-tts

```bash
edge-tts \
  --text "今天天气真好" \
  --voice zh-CN-XiaoxiaoNeural \
  --write-media output.wav
```

#### espeak

```bash
espeak "今天天气真好" -w output.wav
```

---

### ASR 技术实现

#### Whisper

```bash
# 基础使用
whisper input.mp4 --model base --output_format srt

# 快速模式
whisper input.mp4 --model tiny --output_format srt

# 高精度模式
whisper input.mp4 --model large --output_format srt
```

#### faster-whisper

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("input.mp4")

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
```

---

### Remotion 动画

#### 基础模板

```jsx
// Animation.jsx
import {Composition} from 'remotion';
import {HelloWorld} from './HelloWorld';

export const RemotionVideo = () => {
  return (
    <>
      <Composition
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={60}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
```

#### 组件示例

```jsx
// HelloWorld.jsx
import {AbsoluteFill, Sequence, useVideoConfig} from 'remotion';

export const HelloWorld = ({text}) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: 'white'}}>
      <h1 style={{fontSize: 100, textAlign: 'center'}}>
        {text}
      </h1>
    </AbsoluteFill>
  );
};
```

---

## 输出格式

### 输出文件

```bash
# 视频文件
output.mp4    # MP4 格式（通用）
output.mov    # MOV 格式（高质量）
output.webm   # WebM 格式（Web 优化）

# 音频文件
output.wav    # WAV 格式（无损）
output.mp3    # MP3 格式（压缩）
output.aac    # AAC 格式（高效）

# 字幕文件
output.srt    # SRT 格式（通用）
output.ass    # ASS 格式（高级）
output.vtt    # VTT 格式（Web）
```

---

## 最佳实践

### 📐 常用视频标准

**横屏视频（1080P）**：
- 分辨率：1920x1080
- 帧率：30fps
- 编码：H.264
- 码率：10-15 Mbps
- 音频：AAC，48kHz，128kbps

**竖屏视频（1080P）**：
- 分辨率：1080x1920
- 帧率：30fps
- 编码：H.264
- 码率：8-12 Mbps
- 音频：AAC，44.1kHz，128kbps

**高清视频（720P）**：
- 分辨率：1280x720
- 帧率：30fps
- 编码：H.264
- 码率：5-8 Mbps
- 音频：AAC，44.1kHz，96-128kbps

---

### 🎬 编码参数优化

**高质量编码**：
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset slow \
  -crf 18 \
  -c:a aac \
  -b:a 192k \
  output.mp4
```

**快速编码**：
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset ultrafast \
  -crf 23 \
  -c:a aac \
  -b:a 128k \
  output.mp4
```

**参数说明**：
- `-preset slow` - 编码速度与质量平衡（slow/medium/fast/ultrafast）
- `-crf 18` - 质量参数（18-28，越小质量越高）
- `-b:a 192k` - 音频比特率

---

### ⚡ 性能优化

#### 并行处理

```bash
# 使用 GNU Parallel 并行处理多个视频
parallel ffmpeg -i {} -c:v libx264 -preset medium -crf 23 {.}.mp4 ::: *.avi
```

#### 硬件加速

```bash
# NVIDIA NVENC
ffmpeg -i input.mp4 -c:v h264_nvenc -preset p4 -b:v 10M output.mp4

# Intel QSV
ffmpeg -i input.mp4 -c:v h264_qsv -preset medium -b:v 10M output.mp4

# AMD VCE
ffmpeg -i input.mp4 -c:v h264_amf -preset slow -b:v 10M output.mp4
```

---

### 🔧 故障排查

#### FFmpeg 命令失败

**错误**: `Unknown encoder 'libx264'`

**解决**：
```bash
# 重新编译 ffmpeg，启用 libx264
sudo apt-get install libx264-dev

# 或使用内置编码器
ffmpeg -i input.mp4 -c:v h264 output.mp4
```

#### TTS 失败

**错误**: `edge-tts not found`

**解决**：
```bash
pip3 install edge-tts
```

#### ASR 失败

**错误**: `whisper not found`

**解决**：
```bash
pip3 install openai-whisper
```

---

## 高级功能

### 批量处理

```bash
# 批量裁剪视频
for i in *.mp4; do
  ffmpeg -i "$i" -ss 0 -to 30 -c:v libx264 -c:a aac "clip_$i"
done
```

### 格式转换

```bash
# 批量转换为 MP4
for i in *.avi; do
  ffmpeg -i "$i" -c:v libx264 -c:a aac "${i%.*}.mp4"
done
```

### 音频提取

```bash
# 提取音频
ffmpeg -i input.mp4 -vn -acodec copy audio.aac

# 提取并转码
ffmpeg -i input.mp4 -vn -acodec libmp3lame -ab 192k audio.mp3
```

---

## 参考资源

- **FFmpeg 官方文档**: https://ffmpeg.org/documentation.html
- **Whisper 文档**: https://github.com/openai/whisper
- **Edge-TTS 文档**: https://github.com/rany2/edge-tts
- **Remotion 文档**: https://www.remotion.dev/

---

*本 skill 完全基于本地工具实现，无需任何 API 依赖，提供完整的视频创作能力。*
