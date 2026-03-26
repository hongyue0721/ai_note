# Backend

backend 是项目的核心业务服务，基于 **FastAPI + SQLAlchemy + PostgreSQL** 实现。它负责鉴权、文件上传、预览分类、内容入库、parse jobs、review、搜索、图谱、解题和管理员配置能力。

## 主要接口能力

- `GET /healthz`：健康检查
- `GET /v1/meta/app`：应用元信息
- `/v1/auth/*`：用户注册、登录、space-enter、用户信息
- `/v1/admin/auth/login`、`GET/PUT /v1/admin/me`：管理员登录和凭据维护
- `/v1/files/*`：上传策略、本地上传、确认上传
- `/v1/preview/upload-tags`：上传预览与标签分类
- `/v1/ingestions`：创建待解析实体与 parse job
- `/v1/notes/*`、`/v1/problems/*`：内容管理
- `/v1/search`、`/v1/graph/*`、`/v1/solve`：搜索、图谱概览、AI 解题
- `/v1/dashboard`、`/v1/admin/monitor/overview`：用户/管理员统计
- `/v1/admin/runtime-config/models`：运行时模型配置
- `/v1/review/tasks*`、`/v1/parse-jobs*`：审核与任务重试

## 目录结构

```text
apps/backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    main.py
  requirements.txt
```

## 本地运行

```bash
cd apps/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 说明

- backend 启动时会校验数据库连通性、建表、seed 管理员、确保运行时模型配置存在
- `/uploads` 当前通过静态目录挂载提供文件访问
- solve 链路当前是 **AI-only**，`allow_ai_fallback=false` 会直接返回 400
