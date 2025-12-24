# 项目结构说明

## 目录结构

```
IT Solution Check/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── api/                      # API接口层
│   │   └── main.py              # FastAPI主应用
│   ├── core/                     # 核心模块
│   │   └── review_point_library.py  # 审核要点库
│   ├── models/                    # 数据模型
│   │   └── database.py          # 数据库模型定义
│   ├── services/                  # 业务服务层
│   │   ├── document_parser/      # 文档解析服务
│   │   │   └── parser.py        # Word/PDF解析器
│   │   ├── review_engine/        # AI审核引擎
│   │   │   └── ai_reviewer.py   # AI审核核心逻辑
│   │   ├── rule_engine/          # 规则引擎
│   │   │   └── rule_engine.py   # 规则检查引擎
│   │   └── report_generator/     # 报告生成服务
│   │       └── report_generator.py  # 报告生成器
│   └── utils/                     # 工具函数
│       └── __init__.py
├── config/                        # 配置文件
│   └── config.py                 # 系统配置
├── data/                          # 数据存储目录
│   ├── documents/                # 上传的文档
│   ├── reports/                  # 生成的报告
│   └── knowledge_base/           # 知识库文件
├── logs/                          # 日志目录
├── tests/                         # 测试文件目录
├── run.py                         # 启动脚本
├── example_usage.py                # 使用示例
├── requirements.txt               # Python依赖
├── README.md                      # 项目说明
├── QUICKSTART.md                  # 快速启动指南
└── .gitignore                     # Git忽略文件
```

## 核心模块说明

### 1. 审核要点库 (app/core/review_point_library.py)

基于机场场道工程施工组织设计标准结构设计的完整审核要点库，包含14个主要章节的审核要点：

- 文档完整性
- 编制说明
- 工程概况
- 施工部署
- 施工准备
- 主要施工方法
- 施工进度计划
- 资源配置计划
- 质量保证措施
- 安全保证措施
- 文明施工环保
- 季节性施工措施
- 应急预案
- 附图附表

### 2. 文档解析模块 (app/services/document_parser/parser.py)

支持多种文档格式的解析：
- Word文档 (.docx, .doc)
- PDF文档 (.pdf)

功能：
- 文本内容提取
- 章节结构识别
- 表格提取
- 元数据提取

### 3. AI审核引擎 (app/services/review_engine/ai_reviewer.py)

核心审核功能：
- 文档完整性检查
- 章节内容审核
- 必含内容检查
- 智能评分
- 问题识别和建议生成

### 4. 规则引擎 (app/services/rule_engine/rule_engine.py)

可配置的规则检查：
- 内容规则检查
- 章节规则检查
- 自定义规则支持
- 规则优先级管理

### 5. 报告生成器 (app/services/report_generator/report_generator.py)

报告生成功能：
- JSON格式报告
- 文本格式报告
- 问题分类汇总
- 审核结论生成

### 6. 数据库模型 (app/models/database.py)

数据表定义：
- Project: 项目表
- Document: 文档表
- ReviewRecord: 审核记录表
- ReviewRule: 审核规则表
- KnowledgeBase: 知识库表

### 7. API接口 (app/api/main.py)

RESTful API接口：
- 项目管理
- 文档上传和解析
- 文档审核
- 报告生成和查询

## 数据流

```
文档上传 → 文档解析 → 内容提取
                            ↓
                    审核要点库匹配
                            ↓
                    AI审核引擎分析
                            ↓
                    规则引擎检查
                            ↓
                    结果汇总评分
                            ↓
                    报告生成
```

## 扩展点

1. **AI模型集成**：在 `ai_reviewer.py` 中集成大语言模型API
2. **知识库构建**：在 `knowledge_base` 目录添加领域知识
3. **规则扩展**：在 `rule_engine.py` 中添加自定义规则
4. **前端界面**：可基于API开发Web前端
5. **向量检索**：集成向量数据库进行语义检索

## 配置文件

`config/config.py` 包含：
- 数据库配置
- 文件存储路径
- AI模型配置
- 审核评分标准
- 日志配置
