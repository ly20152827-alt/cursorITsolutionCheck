# Vercel 部署指南

## 部署配置

项目已配置好Vercel部署所需的文件：
- `vercel.json` - Vercel配置文件
- `api/app.py` - FastAPI入口点

## 环境变量配置

在Vercel项目设置中添加以下环境变量：

### 必需的环境变量

```
PYTHON_VERSION=3.10
```

### 可选的环境变量

```
# 数据库配置（如果使用PostgreSQL）
DATABASE_URL=postgresql://user:password@host:port/dbname

# AI模型配置
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1

# 日志级别
LOG_LEVEL=INFO
```

## 注意事项

### 1. 数据库

Vercel是无服务器环境，SQLite文件系统是只读的，不适合生产环境。

**建议方案：**
- 使用PostgreSQL（推荐Vercel Postgres）
- 或使用其他云数据库服务

**配置PostgreSQL：**
1. 在Vercel项目设置中启用PostgreSQL
2. 更新 `DATABASE_URL` 环境变量
3. 修改 `app/models/database.py` 中的数据库连接

### 2. 文件存储

上传的文件不能存储在本地文件系统，需要使用云存储。

**建议方案：**
- Vercel Blob Storage
- AWS S3
- 或其他对象存储服务

### 3. 静态文件

静态文件已配置在 `vercel.json` 中，确保路径正确。

### 4. 依赖安装

确保 `requirements.txt` 包含所有必需的依赖。

## 部署步骤

1. 连接GitHub仓库到Vercel
2. 配置环境变量
3. 部署项目
4. 检查部署日志

## 故障排除

### 问题：找不到FastAPI应用

**解决方案：**
- 确保 `api/app.py` 存在
- 检查 `vercel.json` 配置是否正确
- 确认 `app/api/main.py` 中的 `app` 变量已导出

### 问题：数据库连接失败

**解决方案：**
- 检查 `DATABASE_URL` 环境变量
- 确认数据库服务可访问
- 检查防火墙设置

### 问题：静态文件404

**解决方案：**
- 检查静态文件路径配置
- 确认文件已提交到Git仓库
- 检查 `vercel.json` 中的路由配置

## 本地测试

使用Vercel CLI本地测试：

```bash
# 安装Vercel CLI
npm i -g vercel

# 在项目目录运行
vercel dev
```

## 相关链接

- [Vercel Python文档](https://vercel.com/docs/frameworks/backend/fastapi)
- [FastAPI部署指南](https://fastapi.tiangolo.com/deployment/)

