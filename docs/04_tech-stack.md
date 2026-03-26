# 技术栈说明

## 1. 后端技术栈

- **Python 3.11**
- **FastAPI 0.116.1**：HTTP API 框架
- **SQLAlchemy 2.0**：ORM 与数据库访问
- **Pydantic 2** / **pydantic-settings**：配置与数据校验
- **psycopg 3**：PostgreSQL 驱动
- **python-jose**：JWT 生成与校验
- **passlib**：密码哈希与验证
- **httpx / openai**：AI 网关调用
- **pypdf**：PDF 文本抽取

## 2. 前端技术栈

### student

- **Vue 3**
- **TypeScript**
- **Vite 8**
- **marked + DOMPurify**：AI 解题 Markdown 渲染与安全清洗

### admin

- **Vue 3**
- **TypeScript**
- **Vite 8**

## 3. 后台任务与存储

- **PostgreSQL 16**：关系型主数据库
- **本地文件存储**：上传文件写入 `data/uploads`
- **独立 worker 进程**：轮询 parse jobs，执行解析与分类

## 4. 部署技术栈

- **Docker Compose**：本地和远端编排
- **nginx:stable-alpine**：前端静态文件容器
- **node:20-alpine**：前端构建镜像
- **python:3.11-slim**：backend / worker 基础镜像

## 5. 架构特征

- 前后端分离：student 与 admin 独立构建、独立容器
- backend 与 worker 共享同一套 backend 服务层逻辑
- parse-job 异步处理：用户入库与后台解析分离
- runtime config 持久化：管理员可在线调整文本模型 / 视觉模型配置
