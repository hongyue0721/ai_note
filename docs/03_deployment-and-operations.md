# 部署与运维说明

## 1. 运行组件

Docker Compose 当前定义了以下服务：

- `postgres`
- `backend`
- `worker`
- `student-frontend`
- `admin-frontend`

## 2. Docker Compose 启动

在仓库根目录执行：

```bash
docker compose up -d --build
```

默认访问端口：

- `8000`：backend
- `3000`：student frontend
- `3001`：admin frontend

说明：

- PostgreSQL 不再映射到宿主机公网端口，仅在容器网络内部使用
- backend / worker 通过 `.env` 提供运行时配置
- 上传文件通过 `./data/uploads` 挂载到 backend / worker

## 3. 环境变量

以根目录 `.env.example` 为模板。生产环境至少需要配置：

- `APP_ENV=production`
- `JWT_SECRET`
- `ADMIN_JWT_SECRET`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`（或与 `POSTGRES_*` 保持一致）
- `SEED_ADMIN_PASSWORD`
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` / 模型名

生产环境下，backend 会拒绝弱默认密钥和默认管理员密码。

## 4. 本地分服务运行

### backend

```bash
cd apps/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### worker

```bash
cd apps/worker
python main.py
```

### student frontend

```bash
cd apps/frontend/student
npm install
npm run dev
```

### admin frontend

```bash
cd apps/frontend/admin
npm install
npm run dev
```

## 5. 运维要点

- backend 启动时会先执行数据库连通性校验，失败会直接退出
- worker 在数据库不可用时会按固定间隔重试
- admin 端可以在线修改运行时模型配置
- 管理员用户名/密码可通过管理设置页在线修改

## 6. 安全注意事项

- 不要将 `.env` 提交进仓库
- 生产环境必须使用强随机 JWT / DB / 管理员密码
- PostgreSQL 不应暴露到公网
- 上传目录当前是静态挂载，需要按实际部署环境控制访问范围
