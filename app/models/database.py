# -*- coding: utf-8 -*-
"""
数据库模型定义
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="项目名称")
    project_type = Column(String(50), comment="项目类型（施工前期/竣工交付）")
    status = Column(String(50), default="待审核", comment="审核状态")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    documents = relationship("Document", back_populates="project")
    review_records = relationship("ReviewRecord", back_populates="project")


class Document(Base):
    """文档表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="关联项目ID")
    file_name = Column(String(200), nullable=False, comment="文件名")
    file_path = Column(String(500), comment="存储路径")
    file_type = Column(String(50), comment="文件类型")
    file_size = Column(Integer, comment="文件大小（字节）")
    parse_status = Column(String(50), default="待解析", comment="解析状态")
    content = Column(JSON, comment="解析后的内容")
    chapters = Column(JSON, comment="章节结构")
    parse_time = Column(DateTime, comment="解析时间")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    project = relationship("Project", back_populates="documents")
    review_records = relationship("ReviewRecord", back_populates="document")


class ReviewRecord(Base):
    """审核记录表"""
    __tablename__ = "review_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="关联项目ID")
    document_id = Column(Integer, ForeignKey("documents.id"), comment="关联文档ID")
    reviewer = Column(String(100), comment="审核人")
    review_type = Column(String(50), default="AI审核", comment="审核类型（AI/人工）")
    review_result = Column(JSON, comment="审核结果")
    issues = Column(JSON, comment="问题列表")
    suggestions = Column(JSON, comment="建议列表")
    score = Column(Integer, comment="审核得分（0-100）")
    status = Column(String(50), default="审核中", comment="审核状态")
    review_time = Column(DateTime, default=datetime.now, comment="审核时间")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    project = relationship("Project", back_populates="review_records")
    document = relationship("Document", back_populates="review_records")


class ReviewStandard(Base):
    """审核规范表"""
    __tablename__ = "review_standards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="规范名称")
    category = Column(String(100), comment="规范分类")
    file_name = Column(String(200), comment="文件名")
    file_path = Column(String(500), comment="文件存储路径")
    file_type = Column(String(50), comment="文件类型")
    content = Column(Text, comment="规范内容")
    parsed_content = Column(JSON, comment="解析后的内容")
    status = Column(String(50), default="待处理", comment="处理状态")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    rules = relationship("ReviewRule", back_populates="standard")


class ReviewRule(Base):
    """审核规则表"""
    __tablename__ = "review_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("review_standards.id"), comment="关联规范ID")
    rule_name = Column(String(200), nullable=False, comment="规则名称")
    rule_type = Column(String(50), comment="规则类型")
    rule_content = Column(Text, comment="规则内容")
    rule_pattern = Column(String(500), comment="规则匹配模式（正则表达式）")
    required_content = Column(JSON, comment="必含内容列表")
    review_focus = Column(Text, comment="审核重点")
    severity = Column(String(50), default="一般", comment="严重程度")
    priority = Column(Integer, default=0, comment="优先级")
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_ai_generated = Column(Boolean, default=False, comment="是否AI生成")
    ai_model = Column(String(100), comment="使用的AI模型")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    standard = relationship("ReviewStandard", back_populates="rules")


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="标题")
    category = Column(String(100), comment="分类")
    content = Column(Text, comment="内容")
    embedding = Column(JSON, comment="向量表示")
    source = Column(String(200), comment="来源")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


# 数据库配置
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/review_system.db")

# SQLite需要特殊参数，PostgreSQL不需要
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
