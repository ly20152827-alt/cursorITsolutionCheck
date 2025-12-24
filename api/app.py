# -*- coding: utf-8 -*-
"""
Vercel FastAPI入口点
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入FastAPI应用
from app.api.main import app

# 导出app供Vercel使用
__all__ = ["app"]

