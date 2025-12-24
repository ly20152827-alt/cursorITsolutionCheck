# -*- coding: utf-8 -*-
"""
FastAPI主应用
"""

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Template
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

from app.models.database import get_db, init_db, Project, Document, ReviewRecord, ReviewStandard, ReviewRule
from app.services.document_parser.parser import DocumentParserFactory
from app.services.review_engine.ai_reviewer import AIReviewer
from app.services.rule_engine.rule_engine import RuleEngine
from app.services.report_generator.report_generator import ReportGenerator

app = FastAPI(title="技术方案审核AI助手系统", version="1.0.0")

# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，确保所有错误都返回JSON格式"""
    import traceback
    error_detail = str(exc)
    error_traceback = traceback.format_exc()
    
    # 记录错误日志
    print(f"全局异常捕获: {error_detail}")
    print(f"错误堆栈: {error_traceback}")
    
    # 返回JSON格式的错误响应
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": error_detail,
            "path": str(request.url)
        }
    )

# 配置静态文件
BASE_DIR = Path(__file__).parent.parent.parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

# 挂载静态文件目录
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 创建必要的目录（延迟到启动时创建，避免Vercel环境问题）
UPLOAD_DIR = Path("data/documents")
REPORT_DIR = Path("data/reports")


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    print("技术方案审核AI助手系统启动中...")
    
    try:
        # 创建必要的目录
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        print("✓ 目录创建成功")
    except Exception as e:
        print(f"⚠ 目录创建警告: {str(e)}")
        # 在Vercel环境中，某些目录可能无法创建，但不影响基本功能
    
    try:
        # 初始化数据库（延迟初始化，避免模块导入时失败）
        init_db()
        print("✓ 数据库初始化成功")
    except Exception as e:
        print(f"⚠ 数据库初始化警告: {str(e)}")
        # 在Vercel环境中，如果使用PostgreSQL，需要配置DATABASE_URL
        # SQLite在Vercel中可能无法正常工作（文件系统只读）


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回首页"""
    try:
        index_file = templates_dir / "index.html"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        else:
            # 如果文件不存在，返回简单的HTML
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head><title>技术方案审核AI助手系统</title></head>
            <body>
                <h1>技术方案审核AI助手系统</h1>
                <p>系统正在启动中，请稍候...</p>
                <p><a href="/api/status">查看API状态</a></p>
            </body>
            </html>
            """)
    except Exception as e:
        # 如果读取文件失败，返回错误页面
        return HTMLResponse(
            content=f"<h1>系统错误</h1><p>无法加载页面: {str(e)}</p>",
            status_code=500
        )


@app.get("/api/status")
async def status():
    """系统状态"""
    import os
    return {
        "message": "技术方案审核AI助手系统",
        "version": "1.0.0",
        "status": "运行中",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "database_configured": bool(os.getenv("DATABASE_URL"))
    }


@app.get("/api/projects")
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    try:
        # 测试数据库连接
        try:
            db.execute("SELECT 1")
        except Exception as db_error:
            print(f"数据库连接测试失败: {str(db_error)}")
            return JSONResponse(
                status_code=200,
                content={
                    "code": 200,
                    "message": "数据库未配置，返回空列表",
                    "data": [],
                    "warning": "请在Vercel项目设置中配置DATABASE_URL环境变量"
                }
            )
        
        projects = db.query(Project).offset(skip).limit(limit).all()
        
        return {
            "code": 200,
            "data": [
                {
                    "project_id": p.id,
                    "name": p.name,
                    "project_type": p.project_type,
                    "status": p.status,
                    "create_time": p.create_time.isoformat() if p.create_time else None
                }
                for p in projects
            ]
        }
    except Exception as e:
        print(f"获取项目列表错误: {str(e)}")
        import traceback
        traceback.print_exc()
        # 返回JSON格式的错误，而不是抛出异常
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "获取项目列表失败",
                "detail": str(e),
                "data": []
            }
        )


@app.post("/api/projects")
async def create_project(
    request: Request,
    db: Session = Depends(get_db)
):
    """创建项目"""
    try:
        # 尝试从JSON body获取数据
        body = await request.json()
        name = body.get("name")
        project_type = body.get("project_type")
    except:
        # 如果失败，尝试从查询参数获取（向后兼容）
        name = request.query_params.get("name")
        project_type = request.query_params.get("project_type")
    
    if not name:
        raise HTTPException(status_code=400, detail="项目名称不能为空")
    
    project = Project(
        name=name,
        project_type=project_type or "施工前期",
        status="待审核"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "code": 200,
        "message": "项目创建成功",
        "data": {
            "project_id": project.id,
            "name": project.name,
            "status": project.status
        }
    }


@app.post("/api/projects/{project_id}/documents/upload")
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传文档"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 保存文件（Vercel环境中需要使用临时目录或云存储）
    try:
        # 尝试使用配置的目录
        file_path = UPLOAD_DIR / f"{project_id}_{file.filename}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # 如果失败，使用系统临时目录
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / f"{project_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 创建文档记录
    document = Document(
        project_id=project_id,
        file_name=file.filename,
        file_path=str(file_path),
        file_type=Path(file.filename).suffix,
        file_size=file_path.stat().st_size,
        parse_status="待解析"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return {
        "code": 200,
        "message": "文档上传成功",
        "data": {
            "document_id": document.id,
            "file_name": document.file_name,
            "file_size": document.file_size
        }
    }


@app.post("/api/documents/{document_id}/parse")
async def parse_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """解析文档"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    try:
        # 解析文档
        parsed_content = DocumentParserFactory.parse_document(document.file_path)
        
        # 更新文档记录
        document.content = parsed_content.get("content", "")
        document.chapters = parsed_content.get("chapters", [])
        document.parse_status = "解析完成"
        db.commit()
        
        return {
            "code": 200,
            "message": "文档解析成功",
            "data": {
                "document_id": document.id,
                "chapters_count": len(parsed_content.get("chapters", [])),
                "content_length": len(parsed_content.get("content", ""))
            }
        }
    except Exception as e:
        document.parse_status = "解析失败"
        db.commit()
        raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)}")


@app.post("/api/documents/{document_id}/review")
async def review_document(
    document_id: int,
    use_ai: bool = True,
    db: Session = Depends(get_db)
):
    """审核文档"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.parse_status != "解析完成":
        raise HTTPException(status_code=400, detail="文档尚未解析完成")
    
    try:
        # 准备文档内容
        document_content = {
            "content": document.content or "",
            "chapters": document.chapters or []
        }
        
        # AI审核
        ai_reviewer = AIReviewer()
        review_result = ai_reviewer.review_document(document_content)
        
        # 规则引擎审核
        rule_engine = RuleEngine()
        rule_results = rule_engine.check_rules(
            document_content["content"],
            document_content["chapters"]
        )
        
        # 合并规则引擎结果
        for rule_result in rule_results:
            if rule_result.get("status") == "不通过":
                review_result["issues"].append({
                    "type": "规则检查",
                    "severity": rule_result.get("severity", "一般"),
                    "description": rule_result.get("description", ""),
                    "suggestion": rule_result.get("suggestion", "")
                })
        
        # 重新计算得分（合并规则引擎结果后）
        review_result["score"] = ai_reviewer._calculate_score(
            review_result["completeness"],
            review_result["chapter_reviews"]
        )
        
        # 生成报告
        project = db.query(Project).filter(Project.id == document.project_id).first()
        project_info = {
            "name": project.name if project else "",
            "project_type": project.project_type if project else ""
        }
        
        report_generator = ReportGenerator()
        report = report_generator.generate_report(review_result, project_info)
        
        # 保存审核记录
        review_record = ReviewRecord(
            project_id=document.project_id,
            document_id=document_id,
            review_type="AI审核" if use_ai else "规则审核",
            review_result=review_result,
            issues=review_result.get("issues", []),
            suggestions=review_result.get("suggestions", []),
            score=review_result.get("score", 0),
            status="审核完成"
        )
        db.add(review_record)
        
        # 更新项目状态
        if project:
            if review_result["score"] >= 80:
                project.status = "审核通过"
            elif review_result["score"] >= 60:
                project.status = "有条件通过"
            else:
                project.status = "审核不通过"
        
        db.commit()
        db.refresh(review_record)
        
        # 保存报告文件（Vercel环境中可能需要使用临时目录）
        try:
            report_file = REPORT_DIR / f"report_{review_record.id}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_generator.export_to_json(report, str(report_file))
        except Exception as e:
            # 如果保存失败，记录但不影响返回结果
            print(f"报告文件保存警告: {str(e)}")
        
        return {
            "code": 200,
            "message": "审核完成",
            "data": {
                "review_id": review_record.id,
                "score": review_result["score"],
                "issues_count": len(review_result.get("issues", [])),
                "suggestions_count": len(review_result.get("suggestions", [])),
                "report": report
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审核失败: {str(e)}")


@app.get("/api/projects/{project_id}/reviews")
async def get_project_reviews(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取项目的审核记录"""
    reviews = db.query(ReviewRecord).filter(ReviewRecord.project_id == project_id).all()
    
    return {
        "code": 200,
        "data": [
            {
                "review_id": r.id,
                "score": r.score,
                "status": r.status,
                "review_time": r.review_time.isoformat() if r.review_time else None,
                "issues_count": len(r.issues) if r.issues else 0
            }
            for r in reviews
        ]
    }


@app.get("/api/review-points")
async def get_review_points():
    """获取审核要点库"""
    from app.core.review_point_library import ReviewPointLibrary
    
    library = ReviewPointLibrary()
    all_points = library.get_all_review_points()
    
    # 格式化数据
    formatted_points = {}
    for chapter_name, points in all_points.items():
        formatted_points[chapter_name] = points
    
    return {
        "code": 200,
        "data": formatted_points
    }


@app.post("/api/review-standards/upload")
async def upload_review_standard(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """上传审核规范文件"""
    # 保存文件
    file_path = UPLOAD_DIR / f"standard_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 解析文件内容
    try:
        parsed_content = DocumentParserFactory.parse_document(str(file_path))
        content = parsed_content.get("content", "")
    except Exception as e:
        content = ""
    
    # 创建规范记录
    standard = ReviewStandard(
        name=name or file.filename,
        category=category or "通用规范",
        file_name=file.filename,
        file_path=str(file_path),
        file_type=Path(file.filename).suffix,
        content=content,
        parsed_content=parsed_content,
        status="已上传"
    )
    db.add(standard)
    db.commit()
    db.refresh(standard)
    
    return {
        "code": 200,
        "message": "审核规范上传成功",
        "data": {
            "standard_id": standard.id,
            "name": standard.name,
            "category": standard.category,
            "file_name": standard.file_name
        }
    }


@app.get("/api/review-standards")
async def get_review_standards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取审核规范列表"""
    standards = db.query(ReviewStandard).offset(skip).limit(limit).all()
    
    return {
        "code": 200,
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "file_name": s.file_name,
                "status": s.status,
                "create_time": s.create_time.isoformat() if s.create_time else None,
                "rules_count": len(s.rules) if s.rules else 0
            }
            for s in standards
        ]
    }


@app.get("/api/ai-models")
async def get_ai_models():
    """获取可用的AI模型列表"""
    from app.services.ai_rule_generator import AIRuleGenerator
    
    models = AIRuleGenerator.get_available_models()
    return {
        "code": 200,
        "data": models
    }


@app.post("/api/review-standards/{standard_id}/generate-rules")
async def generate_rules_from_standard(
    standard_id: int,
    model_name: str = "deepseek-chat",
    api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """从审核规范生成审核规则"""
    standard = db.query(ReviewStandard).filter(ReviewStandard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="审核规范不存在")
    
    # 使用AI生成规则
    from app.services.ai_rule_generator import AIRuleGenerator
    
    generator = AIRuleGenerator(model_name=model_name, api_key=api_key)
    content = standard.content or standard.parsed_content.get("content", "") if standard.parsed_content else ""
    
    if not content:
        raise HTTPException(status_code=400, detail="规范内容为空，无法生成规则")
    
    generated_rules = generator.generate_rules_from_standard(content, standard.category)
    
    # 保存生成的规则
    saved_rules = []
    for rule_data in generated_rules:
        rule = ReviewRule(
            standard_id=standard_id,
            rule_name=rule_data.get("rule_name", ""),
            rule_type=rule_data.get("rule_type", "内容检查"),
            rule_content=json.dumps(rule_data, ensure_ascii=False),
            rule_pattern=rule_data.get("rule_pattern", ""),
            required_content=rule_data.get("required_content", []),
            review_focus=rule_data.get("review_focus", ""),
            severity=rule_data.get("severity", "一般"),
            is_ai_generated=True,
            ai_model=model_name
        )
        db.add(rule)
        saved_rules.append(rule)
    
    db.commit()
    
    # 刷新规则ID
    for rule in saved_rules:
        db.refresh(rule)
    
    return {
        "code": 200,
        "message": f"成功生成{len(saved_rules)}条审核规则",
        "data": {
            "standard_id": standard_id,
            "rules_count": len(saved_rules),
            "rules": [
                {
                    "id": r.id,
                    "rule_name": r.rule_name,
                    "rule_type": r.rule_type,
                    "severity": r.severity,
                    "is_ai_generated": r.is_ai_generated
                }
                for r in saved_rules
            ]
        }
    }


@app.get("/api/review-standards/{standard_id}/rules")
async def get_standard_rules(
    standard_id: int,
    db: Session = Depends(get_db)
):
    """获取规范的所有规则"""
    standard = db.query(ReviewStandard).filter(ReviewStandard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="审核规范不存在")
    
    rules = db.query(ReviewRule).filter(ReviewRule.standard_id == standard_id).all()
    
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "rule_name": r.rule_name,
                "rule_type": r.rule_type,
                "rule_content": r.rule_content,
                "rule_pattern": r.rule_pattern,
                "required_content": r.required_content,
                "review_focus": r.review_focus,
                "severity": r.severity,
                "priority": r.priority,
                "is_active": r.is_active,
                "is_ai_generated": r.is_ai_generated,
                "ai_model": r.ai_model,
                "create_time": r.create_time.isoformat() if r.create_time else None
            }
            for r in rules
        ]
    }


@app.post("/api/review-rules")
async def create_review_rule(
    rule_data: dict,
    db: Session = Depends(get_db)
):
    """创建审核规则（人工编写）"""
    rule = ReviewRule(
        standard_id=rule_data.get("standard_id"),
        rule_name=rule_data.get("rule_name", ""),
        rule_type=rule_data.get("rule_type", "内容检查"),
        rule_content=rule_data.get("rule_content", ""),
        rule_pattern=rule_data.get("rule_pattern", ""),
        required_content=rule_data.get("required_content", []),
        review_focus=rule_data.get("review_focus", ""),
        severity=rule_data.get("severity", "一般"),
        priority=rule_data.get("priority", 0),
        is_active=rule_data.get("is_active", True),
        is_ai_generated=False
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return {
        "code": 200,
        "message": "规则创建成功",
        "data": {
            "rule_id": rule.id,
            "rule_name": rule.rule_name
        }
    }


@app.put("/api/review-rules/{rule_id}")
async def update_review_rule(
    rule_id: int,
    rule_data: dict,
    db: Session = Depends(get_db)
):
    """更新审核规则"""
    rule = db.query(ReviewRule).filter(ReviewRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    # 更新字段
    if "rule_name" in rule_data:
        rule.rule_name = rule_data["rule_name"]
    if "rule_type" in rule_data:
        rule.rule_type = rule_data["rule_type"]
    if "rule_content" in rule_data:
        rule.rule_content = rule_data["rule_content"]
    if "rule_pattern" in rule_data:
        rule.rule_pattern = rule_data["rule_pattern"]
    if "required_content" in rule_data:
        rule.required_content = rule_data["required_content"]
    if "review_focus" in rule_data:
        rule.review_focus = rule_data["review_focus"]
    if "severity" in rule_data:
        rule.severity = rule_data["severity"]
    if "priority" in rule_data:
        rule.priority = rule_data["priority"]
    if "is_active" in rule_data:
        rule.is_active = rule_data["is_active"]
    
    db.commit()
    db.refresh(rule)
    
    return {
        "code": 200,
        "message": "规则更新成功",
        "data": {
            "rule_id": rule.id,
            "rule_name": rule.rule_name
        }
    }


@app.delete("/api/review-rules/{rule_id}")
async def delete_review_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """删除审核规则"""
    rule = db.query(ReviewRule).filter(ReviewRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    db.delete(rule)
    db.commit()
    
    return {
        "code": 200,
        "message": "规则删除成功"
    }


@app.get("/api/reviews/{review_id}/report")
async def get_review_report(
    review_id: int,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """获取审核报告"""
    review = db.query(ReviewRecord).filter(ReviewRecord.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="审核记录不存在")
    
    project = db.query(Project).filter(Project.id == review.project_id).first()
    project_info = {
        "name": project.name if project else "",
        "project_type": project.project_type if project else ""
    }
    
    report_generator = ReportGenerator()
    report = report_generator.generate_report(review.review_result, project_info)
    
    if format == "text":
        try:
            report_file = REPORT_DIR / f"report_{review_id}.txt"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_generator.export_to_text(report, str(report_file))
        except Exception as e:
            # 如果保存失败，使用临时目录
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            report_file = temp_dir / f"report_{review_id}.txt"
            report_generator.export_to_text(report, str(report_file))
        return {
            "code": 200,
            "message": "报告已生成",
            "data": {
                "report_file": str(report_file)
            }
        }
    
    return {
        "code": 200,
        "data": report
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
