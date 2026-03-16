# StarGraph AI

StarGraph AI（星图智学）是一个面向学习资料整理与错题分析的完整演示型项目，包含：

- **FastAPI backend**：鉴权、文件上传、解析任务、笔记/题目、搜索、图谱、解题、管理端监控
- **Worker**：轮询并处理 parse jobs，同步实体 `parse_status`
- **Student frontend**：用户端工作台，支持字符串空间登录、上传笔记、提问、笔记管理、详情查看
- **Admin frontend**：管理端控制台，支持登录、运行状态观察、用户/笔记统计、运行时模型配置
- **E2E / Smoke / Regression assets**：Playwright 与脚本化验证资产

这个导出目录是一个**可上传到 GitHub 的独立副本**，目标是让新使用者能看懂项目、完成配置、启动本地环境，并理解基本部署方式。

---

## 目录结构

```text
stargraph-ai/
  apps/
    backend/
    worker/
    frontend/
      student/
      admin/
  docs/
  infra/
  libs/
  scripts/
  tests/
  .env.example
  docker-compose.yml
  playwright.config.ts
  package.json
```

---

## 技术栈

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL

### Frontend
- Vue 3
- Vite
- TypeScript

### Worker / Runtime
- Python worker 轮询任务
- Docker Compose 本地编排
- 本地文件存储（默认）

### Testing
- Playwright E2E
- Python smoke / regression scripts

---

## 当前主要能力

- 用户 / 管理员登录与 JWT
- 用户端通过字符串进入专属空间
- 文件上传链路：`upload-policy -> upload-local -> confirm`
- ingestion / parse-jobs / worker 处理链路
- notes / problems / search / graph / solve API
- student 工作台：上传笔记 / 询问问题 / 笔记管理 / 详情页
- admin 控制台：状态观察、请求指标、用户/笔记统计、模型运行时配置
- Playwright 学生端 / 管理端浏览器级回归资产

---

## 先决条件

推荐使用以下方式启动：

- **Docker**
- **Docker Compose**

如果你要本地单独运行子项目，还需要：

- Python 3.11+
- Node.js 20+
- npm

---

## 快速开始

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

### 2. 修改最关键配置

至少检查这些字段：

- `JWT_SECRET`
- `ADMIN_JWT_SECRET`
- `POSTGRES_*`
- `DATABASE_URL`
- `STORAGE_PROVIDER`
- `UPLOADS_ROOT_DIR`
- `OPENAI_API_KEY` 或 `GEMINI_API_KEY`
- `SEED_ADMIN_USERNAME`
- `SEED_ADMIN_PASSWORD`

### 3. 启动全部服务

```bash
docker compose up -d --build
```

### 4. 访问服务

- Student frontend: `http://localhost:3000`
- Admin frontend: `http://localhost:3001`
- Backend API: `http://localhost:8000`
- Health check: `http://localhost:8000/healthz`

### 5. 查看运行状态

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f worker
```

### 6. 停止服务

```bash
docker compose down
```

---

## 环境变量说明

项目根目录提供了 `.env.example`。

### 应用基础

- `APP_ENV`
- `APP_HOST`
- `APP_PORT`
- `APP_NAME`
- `JWT_SECRET`
- `ADMIN_JWT_SECRET`
- `CORS_ORIGINS`

### 数据库

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`

### 存储

- `STORAGE_PROVIDER`
- `UPLOADS_ROOT_DIR`
- `UPLOADS_URL_BASE`
- `MINIO_*`
- `QINIU_*`

### AI 配置

- `GEMINI_API_KEY`
- `GEMINI_MODEL_EXTRACT`
- `GEMINI_MODEL_SOLVE`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL_CLASSIFY`
- `OPENAI_MODEL_SOLVE`
- `OPENAI_TIMEOUT_SECONDS`

### 初始化管理员

- `SEED_ADMIN_USERNAME`
- `SEED_ADMIN_PASSWORD`
- `SEED_ADMIN_DISPLAY_NAME`

---

## 本地开发说明

### Backend

```bash
pip install -r apps/backend/requirements.txt
cd apps/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Worker

```bash
cd apps/worker
python main.py
```

### Student frontend

```bash
cd apps/frontend/student
npm install
npm run dev
```

### Admin frontend

```bash
cd apps/frontend/admin
npm install
npm run dev
```

---

## 测试与验证

### Playwright E2E

项目根目录：

```bash
npm install
npx playwright test
```

只跑 student：

```bash
npm run test:e2e:student
```

只跑 admin：

```bash
npm run test:e2e:admin
```

如果不是测试默认地址，请设置：

- `PLAYWRIGHT_STUDENT_URL`
- `PLAYWRIGHT_ADMIN_URL`

例如：

```bash
PLAYWRIGHT_STUDENT_URL=http://localhost:3000 PLAYWRIGHT_ADMIN_URL=http://localhost:3001 npx playwright test
```

### 脚本化检查

可参考：

- `scripts/smoke_check.py`
- `scripts/regression_check.py`

---

## Docker 部署说明

当前 `docker-compose.yml` 会启动以下服务：

- `postgres`
- `backend`
- `worker`
- `student-frontend`
- `admin-frontend`

其中：

- backend / worker 读取 `.env`
- frontend 通过 Nginx 提供静态产物
- backend 与 worker 共享上传目录：`./data/uploads`

---

## 生产部署建议

最小可行部署方式：

1. 一台 Linux 云主机
2. 安装 Docker 与 Docker Compose
3. 上传项目代码
4. 准备 `.env`
5. 执行 `docker compose up -d --build`
6. 用 Nginx / 反向代理接入域名（可选）

推荐最低排障命令：

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f student-frontend
docker compose logs -f admin-frontend
```

如果你希望服务自启动，可参考：

- `infra/systemd/stargraph-compose.service`

---

## 安全注意事项

这是最重要的一部分：

- **不要提交 `.env`**
- **不要使用默认 JWT 密钥直接上线**
- **不要在公网环境保留示例管理员密码**
- **不要提交 test-results、截图、运行日志、数据库备份、上传文件目录**

建议在正式公开前至少完成：

1. 更换 `JWT_SECRET`
2. 更换 `ADMIN_JWT_SECRET`
3. 更换管理员初始密码
4. 检查 `CORS_ORIGINS`
5. 检查数据库口令
6. 填入真实 AI Key

---

## 推荐阅读顺序

如果你想更快理解项目：

1. `README.md`
2. `apps/backend/README.md`
3. `apps/frontend/README.md`
4. `apps/worker/README.md`
5. `docs/65_接口文档_按当前真实代码生成.md`
6. `docs/71_全量未完成事项盘点_基于最新代码深扫.md`

---

## 当前已知限制

- student 上传仍是单文件链路，未支持多图同时上传
- graph 仍是轻量实现，不是完整 node-edge 图模型
- backend pytest / integration tests、CI、migration scaffolding 仍未完全收口
- 项目包含较多历史 docs，阅读时建议优先看 README 与 `docs/65` / `docs/71`

---

## License / Usage

当前导出目录更适合作为演示、学习和继续开发的基础版本。若要公开开源，建议你先完成：

- 敏感信息二次排查
- 文档统一收口
- LICENSE 明确化
- `.gitignore` 补齐
