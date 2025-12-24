# -*- coding: utf-8 -*-
"""
系统配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/review_system.db")

# 文件存储配置
UPLOAD_DIR = BASE_DIR / "data" / "documents"
REPORT_DIR = BASE_DIR / "data" / "reports"
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"

# 创建必要的目录
for dir_path in [UPLOAD_DIR, REPORT_DIR, KNOWLEDGE_BASE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# AI模型配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

# 审核配置
REVIEW_CONFIG = {
    "min_score_pass": 80,  # 通过的最低分数
    "min_score_conditional": 60,  # 有条件通过的最低分数
    "enable_ai_review": True,  # 是否启用AI审核
    "enable_rule_review": True,  # 是否启用规则审核
}

# 日志配置
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 允许的文件类型
ALLOWED_FILE_TYPES = [".docx", ".doc", ".pdf", ".txt"]

# 文件大小限制（MB）
MAX_FILE_SIZE_MB = 50
