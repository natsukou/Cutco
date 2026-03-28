from __future__ import annotations

from pathlib import Path

from mvp_platform import criteria_stage, qa_stage, store


def main() -> None:
    sample_video = Path(r"C:\Users\Admin\output_video.mp4")
    sample_srt = Path(r"C:\Users\Admin\video-agent-mvp\sample_data\demo_subtitles.srt")
    if not sample_video.exists():
        raise FileNotFoundError(f"Missing sample video: {sample_video}")

    state = store.create_project(
        "smoke-demo",
        "给一条短视频做 demo 配音与字幕方案，先明确验收标准，再做 QA。",
    )
    project_id = state["id"]
    store.copy_external_file(project_id, sample_video, "intake", "source_video")
    criteria_stage.run(project_id)
    store.confirm_criteria(project_id)
    criteria_stage.write_confirmed_pattern(project_id)
    store.copy_external_file(project_id, sample_video, "production", "demo_video")
    store.copy_external_file(project_id, sample_srt, "production", "demo_srt")
    final_state = qa_stage.run(project_id)

    print(f"project_id={project_id}")
    print(f"status={final_state['status']}")
    print(f"verdict={final_state['verdict']}")
    print(f"qa_report={final_state['files']['qa_report']}")


if __name__ == "__main__":
    main()
