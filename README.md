# 技术方案审核AI助手系统

## 项目简介

技术方案审核AI助手系统是专为民航机场建设领域的管理局设计的智能审核工具，用于对施工阶段前期准备和竣工交付的技术方案进行自动化审核。

## 功能特性

- 🌐 **Web界面**：现代化的Web界面，操作简单直观
- 📄 **文档解析**：支持Word、PDF等格式的文档自动解析
- 🤖 **AI智能审核**：基于审核要点库进行智能审核分析
- ⚙️ **规则引擎**：可配置的审核规则检查
- 📊 **审核报告**：自动生成详细的审核报告
- 🗄️ **数据管理**：项目、文档、审核记录的统一管理
- 📈 **实时进度**：实时显示审核进度和状态

## 系统架构

```
app/
├── api/              # API接口层
├── core/             # 核心模块（审核要点库）
├── models/           # 数据模型
├── services/         # 业务服务层
│   ├── document_parser/    # 文档解析服务
│   ├── review_engine/      # AI审核引擎
│   ├── rule_engine/        # 规则引擎
│   └── report_generator/   # 报告生成服务
└── utils/            # 工具函数

config/               # 配置文件
data/                 # 数据存储目录
tests/                # 测试文件
```

## 安装部署

### 1. 环境要求

- Python 3.10+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

系统首次运行时会自动创建数据库。

### 4. 启动服务

```bash
# 方式1：使用启动脚本（推荐）
python run.py

# 方式2：直接运行
python -m app.api.main

# 方式3：使用uvicorn
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问Web界面

启动后访问：**http://localhost:8000**

Web界面提供完整的图形化操作，包括：
- 项目管理
- 文档上传
- 审核进度查看
- 审核结果展示
- 报告查看

### 6. 访问API文档

API文档地址：http://localhost:8000/docs

## API接口说明

### 1. 创建项目

```http
POST /api/projects
参数：
- name: 项目名称
- project_type: 项目类型（可选）
```

### 2. 上传文档

```http
POST /api/projects/{project_id}/documents/upload
Content-Type: multipart/form-data
参数：
- file: 文档文件
```

### 3. 解析文档

```http
POST /api/documents/{document_id}/parse
```

### 4. 审核文档

```http
POST /api/documents/{document_id}/review
参数：
- use_ai: 是否使用AI审核（默认true）
```

### 5. 获取审核报告

```http
GET /api/reviews/{review_id}/report?format=json
参数：
- format: 报告格式（json/text）
```

## 审核要点库

系统内置了基于机场场道工程施工组织设计的完整审核要点库，包括：

1. **文档完整性**：检查必含章节是否齐全
2. **编制说明**：审核编制依据、原则等
3. **工程概况**：检查项目基本信息、工程特点等
4. **施工部署**：审核施工目标、组织架构等
5. **施工准备**：检查技术、现场、材料等准备情况
6. **主要施工方法**：审核施工工艺、技术措施等
7. **施工进度计划**：检查进度计划合理性
8. **资源配置计划**：审核人力、材料、设备配置
9. **质量保证措施**：检查质量管理体系
10. **安全保证措施**：审核安全管理体系、重大危险源管理
11. **文明施工环保**：检查环保措施
12. **季节性施工措施**：审核季节性施工方案
13. **应急预案**：检查应急预案完整性
14. **附图附表**：检查图表完整性

## 配置说明

在 `config/config.py` 中可以配置：

- 数据库连接
- AI模型API密钥（可选）
- 审核评分标准
- 文件存储路径

## 使用示例

### Python调用示例

```python
import requests

# 1. 创建项目
response = requests.post("http://localhost:8000/api/projects", 
                         params={"name": "测试项目", "project_type": "施工前期"})
project_id = response.json()["data"]["project_id"]

# 2. 上传文档
with open("施工组织设计.docx", "rb") as f:
    files = {"file": f}
    response = requests.post(f"http://localhost:8000/api/projects/{project_id}/documents/upload", 
                             files=files)
    document_id = response.json()["data"]["document_id"]

# 3. 解析文档
response = requests.post(f"http://localhost:8000/api/documents/{document_id}/parse")

# 4. 审核文档
response = requests.post(f"http://localhost:8000/api/documents/{document_id}/review")
review_id = response.json()["data"]["review_id"]

# 5. 获取报告
response = requests.get(f"http://localhost:8000/api/reviews/{review_id}/report")
report = response.json()["data"]
```

## 开发计划

### 第一阶段（已完成）
- ✅ 基础文档解析
- ✅ 审核要点库
- ✅ 规则引擎
- ✅ 基础报告生成

### 第二阶段（计划中）
- ⏳ 集成大语言模型
- ⏳ 知识库构建
- ⏳ 向量检索
- ⏳ 智能对比分析

### 第三阶段（计划中）
- ⏳ 知识图谱
- ⏳ 高级分析功能
- ⏳ Web前端界面
- ⏳ 用户权限管理

## 注意事项

1. 首次使用需要安装所有依赖包
2. Word文档解析需要安装 `python-docx`
3. PDF文档解析需要安装 `PyPDF2`
4. AI功能需要配置API密钥（可选）
5. 建议使用虚拟环境

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
