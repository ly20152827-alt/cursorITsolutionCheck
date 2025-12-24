# 快速启动指南

## 一、环境准备

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 检查依赖安装

确保以下关键库已安装：
- fastapi
- uvicorn
- sqlalchemy
- python-docx (用于Word文档解析)
- PyPDF2 (用于PDF文档解析)

## 二、启动服务

### 方式1：使用启动脚本（推荐）

```bash
python run.py
```

### 方式2：直接使用uvicorn

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方式3：使用Python模块

```bash
python -m app.api.main
```

## 三、验证服务

服务启动后，访问以下地址：

1. **API文档（Swagger UI）**: http://localhost:8000/docs
2. **API文档（ReDoc）**: http://localhost:8000/redoc
3. **根路径**: http://localhost:8000/

## 四、使用示例

### 1. 使用Python脚本

运行示例脚本：

```bash
python example_usage.py
```

### 2. 使用curl命令

#### 创建项目
```bash
curl -X POST "http://localhost:8000/api/projects?name=测试项目&project_type=施工前期"
```

#### 上传文档
```bash
curl -X POST "http://localhost:8000/api/projects/1/documents/upload" \
  -F "file=@机场场道工程施工组织设计范本.docx"
```

#### 解析文档
```bash
curl -X POST "http://localhost:8000/api/documents/1/parse"
```

#### 审核文档
```bash
curl -X POST "http://localhost:8000/api/documents/1/review?use_ai=true"
```

#### 获取报告
```bash
curl "http://localhost:8000/api/reviews/1/report?format=json"
```

### 3. 使用Web界面

访问 http://localhost:8000/docs，在Swagger UI界面中可以直接测试所有API接口。

## 五、常见问题

### 1. 端口被占用

如果8000端口被占用，可以修改端口：

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 2. 文档解析失败

- 确保已安装 `python-docx` (Word文档)
- 确保已安装 `PyPDF2` (PDF文档)
- 检查文档格式是否支持

### 3. 数据库错误

系统使用SQLite数据库，首次运行会自动创建数据库文件：
`data/review_system.db`

如果遇到数据库错误，可以删除该文件重新创建。

### 4. 导入错误

确保在项目根目录运行命令，而不是在app目录内。

## 六、下一步

1. 查看 `README.md` 了解完整功能
2. 查看 `app/core/review_point_library.py` 了解审核要点库
3. 根据需要修改 `config/config.py` 进行配置
4. 集成大语言模型API（可选）

## 七、API接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 系统状态 |
| `/api/projects` | POST | 创建项目 |
| `/api/projects/{id}/documents/upload` | POST | 上传文档 |
| `/api/documents/{id}/parse` | POST | 解析文档 |
| `/api/documents/{id}/review` | POST | 审核文档 |
| `/api/projects/{id}/reviews` | GET | 获取项目审核记录 |
| `/api/reviews/{id}/report` | GET | 获取审核报告 |

详细API文档请访问：http://localhost:8000/docs
