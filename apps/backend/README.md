# Backend

当前后端采用 **FastAPI + Python 3.11**。

## 本轮已完成

- 建立最小应用结构
- 提供 `/healthz` 健康检查接口
- 提供 `/v1/meta/app` 元信息接口
- 加入基础配置加载逻辑

## 当前未完成

- 鉴权与演示用户
- 数据库会话与 ORM 模型
- 文件上传接口
- ingestion / parse_jobs 业务链路
- review / search / graph / solve 接口

## 目录说明

```text
apps/backend/
  app/
    api/
    core/
    schemas/
    main.py
  requirements.txt
```

## 本地运行

```bash
pip install -r apps/backend/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

在 `apps/backend` 目录下执行。
