from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "project-patterns"
DESKTOP_SKILLS_DIR = Path(r"C:\Users\Admin\Desktop\files (1)")

VIDEO_CRITERIA_DIR = DESKTOP_SKILLS_DIR / "video-criteria-gen"
VIDEO_QA_DIR = DESKTOP_SKILLS_DIR / "video-qa"

CRITERIA_SKILL_MD = VIDEO_CRITERIA_DIR / "SKILL.md"
QA_SKILL_MD = VIDEO_QA_DIR / "SKILL.md"

PROBE_SCRIPT = VIDEO_CRITERIA_DIR / "scripts" / "probe_source.py"
GEN_CRITERIA_SCRIPT = VIDEO_CRITERIA_DIR / "scripts" / "gen_criteria.py"
CHECK_ENGINEERING_SCRIPT = VIDEO_QA_DIR / "scripts" / "check_engineering.py"
CHECK_SRT_SCRIPT = VIDEO_QA_DIR / "scripts" / "check_srt.py"

CLAUDE_COMMAND = os.environ.get("CLAUDE_COMMAND", "claude")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "").strip()

AGENT_TIMEOUT = int(os.environ.get("MVP_AGENT_TIMEOUT", "300"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

VISUAL_PROVIDER = os.environ.get("MVP_VISUAL_PROVIDER", "gemini")  # gemini | glm
GLM_API_KEY = os.environ.get("GLM_API_KEY", "").strip()
GLM_MODEL = os.environ.get("GLM_MODEL", "glm-4v-flash").strip()

VISUAL_REVIEW_SCRIPT = BASE_DIR / "mvp_platform" / "scripts" / "visual_review.py"

APP_NAME = "Video Delivery Agent MVP"


def ensure_base_dirs() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
