---
name: video-editor
description: 快速视频剪辑专家。当用户提到"剪视频"、"剪辑视频"、"混剪"、"裁剪视频"、"生成视频"、"AI 视频"、"配音"、"字幕"、"视频处理"、"视频编辑"等关键词时触发。支持素材混剪、视频裁剪、配音生成、字幕生成、AI 视频生成、关键帧动画等常见视频处理场景。基于 VectCut API 实现端到端的视频创作流程。
homepage: "https://www.vectcut.com/"
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      env: ["VECTCUT_API_KEY"]
    primaryEnv: "VECTCUT_API_KEY"
dependency:
---

# Video Editor Skill - 快速视频剪辑

本技能提供快速、直观的视频剪辑能力，专注于常见视频处理场景。让 AI 能够像专业剪辑师一样快速完成视频创作任务。

## 核心能力

### 常见场景支持

#### 1️⃣ 素材混剪
将多个视频、音频、文本素材组合成一个完整的视频。
**流程**：创建草稿 → 添加视频 → 添加音频 → 添加字幕 → 添加转场/特效 → 云渲染

#### 2️⃣ 视频裁剪
按时间段切分视频，提取需要的片段。
**流程**：使用 split_video 切分 → 创建草稿 → 添加切分后的视频 → 渲染

#### 3️⃣ 配音生成
使用 TTS 生成配音并添加到视频。
**流程**：调用 generate_speech 生成音频 → 创建草稿 → 添加音频 → 配合视频/图片

#### 4️⃣ 字幕生成
自动识别视频语音并生成字幕。
**流程**：使用 ASR 接口识别语音 → 创建草稿 → 添加文本素材为字幕

#### 5️⃣ AI 视频生成
文生视频、图生视频。
**流程**：调用 generate_ai_video → 轮询任务状态 → 获取生成结果

#### 6️⃣ 关键帧动画
为视频、图片、文字添加关键帧动画。
**流程**：添加素材 → 设置关键帧 → 配置动画参数

---

## 快速开始

### 环境配置

确保已设置 API Key：

```bash
export VECTCUT_API_KEY="your_api_key_here"
```

---

## 常用工作流

### 工作流 1：快速混剪

```bash
# 1. 创建草稿（默认 1080x1920 竖屏）
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"混剪视频","width":1080,"height":1920}'

# 假设返回 draft_id=xxx

# 2. 添加视频（第一段：0-10秒）
curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "video_url":"https://example.com/video1.mp4",
    "start":0,
    "end":10,
    "target_start":0
  }'

# 3. 添加视频（第二段：接在后面）
curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "video_url":"https://example.com/video2.mp4",
    "start":5,
    "end":15,
    "target_start":10
  }'

# 4. 添加转场（加在第一段视频上）
curl -X POST http://open.vectcut.com/cut_jianying/modify_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "material_id":"material_id_from_video1",
    "transition":{"type":"wipe","duration":0.5}
  }'

# 5. 添加背景音乐
curl -X POST http://open.vectcut.com/cut_jianying/add_audio \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "audio_url":"https://example.com/bgm.mp3",
    "volume":0.3
  }'

# 6. 云渲染
curl -X POST http://open.vectcut.com/cut_jianying/generate_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "resolution":"1080P"
  }'

# 返回 task_id，轮询状态
```

---

### 工作流 2：文生图 + 配音（绘本/故事视频）

```bash
# 1. 创建草稿
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"故事视频"}'

# 假设返回 draft_id=xxx

# 2. 生成第一张插图
curl -X POST http://open.vectcut.com/cut_jianying/generate_image \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "prompt":"一只小兔子在草地上玩耍，阳光明媚",
    "model":"nano_banana_pro"
  }'

# 假设返回 image_url=xxx

# 3. 生成配音
curl -X POST http://open.vectcut.com/cut_jianying/generate_speech \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text":"今天天气真好，小兔子来到草地上玩耍。",
    "provider":"minimax",
    "model":"speech-01",
    "voice_id":"female_tianmei"
  }'

# 返回 audio_url=yyy

# 4. 获取配音时长
curl -X POST http://open.vectcut.com/cut_jianying/get_duration \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"yyy"}'

# 假设返回 duration=5.3

# 5. 添加图片到草稿（时长对齐配音）
curl -X POST http://open.vectcut.com/cut_jianying/add_image \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "image_url":"xxx",
    "duration":5.3
  }'

# 6. 添加字幕
curl -X POST http://open.vectcut.com/cut_jianying/add_text \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"xxx",
    "text":"今天天气真好，小兔子来到草地上玩耍。",
    "start":0,
    "end":5.3,
    "style":{
      "font_size":32,
      "color":"#FFFFFF",
      "background_color":"#00000080"
    }
  }'
```

---

### 工作流 3：视频裁剪

```bash
# 1. 切分视频（提取 10-30 秒片段）
curl -X POST http://open.vectcut.com/cut_jianying/split_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url":"https://example.com/original.mp4",
    "start":10,
    "end":30
  }'

# 返回 new_video_url=xxx

# 2. 创建草稿并添加
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"裁剪后的视频"}'

curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"yyy",
    "video_url":"xxx"
  }'
```

---

### 工作流 4：自动字幕生成

```bash
# 1. 使用 ASR 识别语音（推荐使用 asr_llm）
curl -X POST http://open.vectcut.com/cut_jianying/asr_llm \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url":"https://example.com/video.mp4"
  }'

# 返回 segments（包含每句文本、开始时间、结束时间）

# 2. 创建草稿并添加视频
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"带字幕的视频"}'

# 3. 添加视频
curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"zzz",
    "video_url":"https://example.com/video.mp4"
  }'

# 4. 批量添加字幕（根据 ASR 返回的 segments）
# 对每个 segment 调用 add_text
curl -X POST http://open.vectcut.com/cut_jianying/add_text \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id":"zzz",
    "text":"第一句话",
    "start":0,
    "end":2.5,
    "style":{
      "font_size":28,
      "color":"#FFFFFF",
      "y":0.8
    }
  }'
```

---

### 工作流 5：AI 视频生成

```bash
# 1. 发起文生视频任务
curl -X POST http://open.vectcut.com/cut_jianying/generate_ai_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt":"一只可爱的小狗在公园里追逐飞盘",
    "model":"kling-v1",
    "resolution":"1080x1920"
  }'

# 返回 task_id=xxx

# 2. 轮询任务状态
curl -X GET "http://open.vectcut.com/cut_jianying/aivideo/task_status?task_id=xxx" \
  -H "Authorization: Bearer $VECTCUT_API_KEY"

# 返回 status, progress, video_url, draft_id

# 3. 等待 status=completed，获取 video_url
```

---

## 核心接口速查

### 草稿管理
- `POST /create_draft` - 创建草稿
- `POST /modify_draft` - 修改草稿（名称、封面）
- `POST /remove_draft` - 删除草稿
- `POST /query_script` - 查询草稿脚本结构

### 素材编排
- `POST /add_video` - 添加视频
- `POST /modify_video` - 修改视频
- `POST /remove_video` - 删除视频
- `POST /add_image` - 添加图片
- `POST /modify_image` - 修改图片
- `POST /remove_image` - 删除图片
- `POST /add_audio` - 添加音频
- `POST /add_text` - 添加文本
- `POST /modify_text` - 修改文本
- `POST /remove_text` - 删除文本
- `POST /add_sticker` - 添加贴纸
- `POST /add_effect` - 添加特效
- `POST /add_filter` - 添加滤镜

### 关键帧
- `POST /add_video_keyframe` - 添加关键帧

### AI 能力
- `POST /generate_image` - AI 图片生成
- `POST /generate_ai_video` - AI 视频生成
- `GET /aivideo/task_status` - 查询 AI 视频任务状态
- `POST /generate_speech` - TTS 语音合成
- `POST /digital_human/create` - 创建数字人
- `GET /digital_human/task_status` - 查询数字人状态

### 处理工具
- `POST /split_video` - 切分视频
- `POST /extract_audio` - 提取音频
- `POST /get_duration` - 获取素材时长

### ASR 语音识别
- `POST /asr_basic` - 基础识别（速度快，横屏字幕）
- `POST /asr_nlp` - 语义分句（竖屏字幕）
- `POST /asr_llm` - AI 关键词提取（短视频字幕，推荐）

### 渲染与查询
- `POST /generate_video` - 云渲染
- `POST /task_status` - 查询任务状态

### 枚举查询
- `GET /get_transition_types` - 转场类型
- `GET /get_effect_types` - 特效类型
- `GET /get_filter_types` - 滤镜类型
- `GET /get_font_types` - 字体类型
- `GET /get_text_intro_types` - 文字入场动画
- `GET /get_text_outro_types` - 文字出场动画

---

## 输出格式要求

完成任务后，必须包含以下信息：

```markdown
✅ 任务完成

**草稿信息**：
- Draft ID: `draft_id`
- Draft URL: [草稿名称](draft_url)
- 可在剪映/CapCut 中打开继续编辑

**素材 ID**：
- 视频素材: `material_id`
- 音频素材: `material_id`
- 字幕素材: `material_id`

**渲染结果**（如果已渲染）：
- 视频链接: [下载视频](video_url)
- 任务 ID: `task_id`
```

---

## 最佳实践

### 📐 画面比例选择
- 竖屏短视频：1080x1920 (9:16)
- 横屏视频：1920x1080 (16:9)
- 正方形：1080x1080 (1:1)

### 🎬 转场技巧
- 转场必须加在前一个元素上
- 相邻两个素材首尾紧接时才生效
- 常用转场：fade（淡入淡出）、wipe（擦除）、slide（滑动）

### 📝 字幕优化
- 竖屏推荐：`asr_llm` → 每句不超过 12 字
- 横屏推荐：`asr_basic` → 完整句级时间
- 字幕位置：y=0.8（底部 80% 处）
- 字幕样式：白色文字 + 半透明黑色背景

### 🎵 音画同步
- 使用 `get_duration` 获取音频时长
- 图片/视频时长设置为音频时长
- 使用 `target_start` 控制素材在时间线上的位置

### ⚡ 性能优化
- ASR 接口按需选择：`asr_llm > asr_nlp > asr_basic`
- 云渲染需要 2-5 分钟，建议最后再渲染
- 生成过程中可以使用 `query_script` 预览草稿结构

---

## 故障排查

### 常见错误

**错误 231001: reaction type is invalid**
- 检查 API 请求格式是否正确
- 确保 reaction_type 嵌套结构正确

**草稿不存在**
- 检查 draft_id 是否正确
- 确认草稿未被删除

**渲染失败**
- 检查素材 URL 是否可访问
- 确认素材格式支持（MP4、JPG、PNG、MP3）
- 检查素材时长是否合理

**字幕时间不对**
- 使用 `get_duration` 获取准确时长
- 检查 start/end 参数是否正确

---

## 参考资源

- **VectCut 官方文档**: https://www.vectcut.com/
- **API 文档**: http://open.vectcut.com/
- **剪映/CapCut**: https://www.capcut.com/

---

*本 skill 基于 VectCut API，提供快速视频剪辑能力。*
