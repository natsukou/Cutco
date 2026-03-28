# Video Delivery Agent MVP

一个黑客松导向的最小平台，用来演示视频交付项目的三阶段工作流：

1. `Criteria`
   - 读取用户需求和原片
   - 生成 `project-brief.md`、`acceptance-criteria.md`、`pending-items.md`、`demo-plan.json`
2. `Human / Demo`
   - 用户确认待确认项
   - 上传 demo 视频和 SRT
3. `QA`
   - 跑工程核查、音频核查、字幕核查
   - Gemini 视觉审核可选；未配置时自动回退为人工确认占位
   - 结果写入共享 `knowledge/project-patterns/`

## 运行

```powershell
cd C:\Users\Admin\video-agent-mvp
python app.py
```

打开：

```text
http://127.0.0.1:5055
```

## 环境变量

- `MVP_ENABLE_CLAUDE=1`
  - 默认不启用 Claude 真接入；设为 `1` 后才尝试调用 Claude Code CLI
- `CLAUDE_MODEL=<model>`
  - 指定 Claude Code CLI 的模型名
- `GEMINI_API_KEY=<key>`
  - 打开 Gemini 视觉/听觉审核
- `GEMINI_MODEL=gemini-2.0-flash`
  - 指定 Gemini 模型

## 关键目录

- `projects/<project_id>/`
  - 每个项目的状态和产物
- `knowledge/project-patterns/`
  - 两个 skill 共享的经验沉淀目录
- `C:\Users\Admin\Desktop\files (1)\video-criteria-gen`
  - 前置标准 skill 来源
- `C:\Users\Admin\Desktop\files (1)\video-qa`
  - 后置质检 skill 来源

## Smoke Test

根目录提供 `smoke_test.py`，会用本机已有的 `output_video.mp4` 和内置的示例 SRT 跑一遍闭环。
