# StarGraph AI

StarGraph AI（星图智学）是一个面向学生错题整理、笔记沉淀、知识点关联与 AI 辅助解析的演示型学习系统。它的产品目标来自 `D:\vibe_coding\smartnote` 中的 MVP 方案：用户上传题目或笔记后，系统完成文件落库、内容解析、知识点提取、人工审核、搜索检索与轻量图谱展示；当本地资料未命中时，再由 AI 返回参考解析。

当前这个 `stargraph-ai` 目录不是纯方案仓，而是已经落成的可运行副本：包含 FastAPI 后端、轮询式 worker、学生端与管理端前端、Docker Compose 编排，以及 E2E 测试资产。

---

## 1. 项目在做什么

核心场景只有一条主链路：

1. 用户注册 / 登录 / 进入自己的空间
2. 上传图片、PDF、文本等学习材料
3. 后端创建 ingestion 与 parse job
4. worker 或预览接口调用模型做分类、抽取和标签建议
5. 笔记与错题以知识点标签建立可检索关系
6. 学生端查看内容、搜索内容、看知识点概览与薄弱点
7. 管理端查看运行状态、解析任务、运行时模型配置

这与 `smartnote` 里的首月 MVP 原理一致：

- 不先做重型微服务
- 不先上真正图数据库
- 先把“上传 → 解析 → 标签 → 关联 → 搜索 → 展示”跑通
- AI 负责提取和建议，不直接充当最终事实来源

---

## 2. 仓库结构

```text
stargraph-ai/
  apps/
    backend/              # FastAPI API、数据库模型、服务逻辑
    worker/               # 解析任务轮询 worker
    frontend/
      student/            # 学生端 Vue 3 + Vite
      admin/              # 管理端 Vue 3 + Vite
  infra/                  # Dockerfile / systemd 等部署资产
  libs/                   # 预留共享库目录
  scripts/                # smoke / regression 脚本
  tests/                  # Playwright E2E
  .env.example
  docker-compose.yml
  package.json
  playwright.config.ts
```

---

## 3. 技术栈

### 后端

- Python 3.11
- FastAPI
- Pydantic v2 / pydantic-settings
- SQLAlchemy 2
- Alembic（依赖已存在）
- PostgreSQL 16
- python-jose + passlib（JWT 与密码哈希）
- httpx / OpenAI SDK / pypdf

后端依赖来源：`apps/backend/requirements.txt`

### 前端

- Vue 3
- TypeScript
- Vite

前端包定义：

- `apps/frontend/student/package.json`
- `apps/frontend/admin/package.json`

### 运行与部署

- Docker Compose
- Nginx 静态托管前端
- 本地文件存储目录 `data/uploads`
- PostgreSQL 作为主业务库

### 测试

- Playwright E2E
- Python smoke / regression 脚本

---

## 4. 系统原理

### 4.1 总体架构

项目遵循 `smartnote` 中“逻辑分层、统一部署、接口先行”的实现思路：

```text
Student/Admin Frontend
        |
        v
     FastAPI API
        |
        +--> PostgreSQL
        +--> Local Upload Storage
        +--> Runtime Model Config
        +--> Parse Job Table
                 |
                 v
               Worker
                 |
                 v
            LLM classify / solve
```

### 4.2 为什么这样设计

- **先关系库，后图数据库**：当前图谱接口本质是根据解析结果中的 `knowledge_candidates` 聚合权重，而不是维护独立图数据库。
- **先任务表，后消息队列**：解析异步链路通过 `ParseJob` 表 + worker 轮询实现，符合 `smartnote` 中“数据库任务表 + 独立 worker”的 MVP 建议。
- **AI 只做建议层**：分类、标签提取、解题结果来自模型，但审核、替换标签、运行时模型配置都保留人工或后台控制入口。
- **统一返回格式**：接口基本采用 `{ code, message, data }` 返回结构，这与 `smartnote/12_API接口契约草案.md` 的约定一致。

### 4.3 主要业务链路

#### 上传与入库

1. `POST /v1/files/upload-policy` 申请文件记录与对象键
2. `POST /v1/files/upload-local` 实际写入本地文件
3. `POST /v1/files/confirm` 确认文件元数据
4. `POST /v1/ingestions` 创建 note / problem 与 parse job

#### 预览与确认

1. `POST /v1/preview/upload-tags` 对文本 / PDF / 图片做预分类
2. 前端拿到标题、学科、标签候选、摘要
3. `POST /v1/notes/confirm` 将预览结果直接确认成笔记

#### 解析与审核

1. ingestion 创建 `ParseJob`
2. worker / 服务逻辑补充 `result_json`
3. 管理端查看 `/v1/admin/parse-jobs`
4. 审核端通过 `/v1/review/tasks/{task_id}/decision` 批准、拒绝或替换标签

#### 搜索、图谱与解题

- `/v1/search` 跨笔记和错题检索
- `/v1/graph/overview` 聚合知识点权重
- `/v1/graph/weak-tags` 基于低置信度聚合薄弱点
- `/v1/solve` 在当前实现中直接走 AI-only 解题链路

---

## 5. 运行中的服务

`docker-compose.yml` 当前启动这些服务：

- `postgres`
- `backend`
- `worker`
- `student-frontend`
- `admin-frontend`

默认端口：

- Student frontend: `http://localhost:3000`
- Admin frontend: `http://localhost:3001`
- Backend API: `http://localhost:8000`
- Health API: `http://localhost:8000/healthz`

---

## 6. 快速开始

### 6.1 准备环境变量

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

### 6.2 必看配置

- `JWT_SECRET`
- `ADMIN_JWT_SECRET`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `STORAGE_PROVIDER`
- `UPLOADS_ROOT_DIR`
- `GEMINI_API_KEY` / `OPENAI_API_KEY`
- `SEED_ADMIN_USERNAME`
- `SEED_ADMIN_PASSWORD`

### 6.3 一键启动

```bash
docker compose up -d --build
```

### 6.4 查看状态

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f worker
```

### 6.5 停止

```bash
docker compose down
```

---

## 7. 环境变量说明

项目根目录提供 `.env.example`，当前可见配置分为四类。

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
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `QINIU_ACCESS_KEY`
- `QINIU_SECRET_KEY`
- `QINIU_BUCKET`
- `QINIU_DOMAIN`

### AI

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

## 8. 接口总览

基线路由定义见：

- `apps/backend/app/api/router.py`
- `apps/backend/app/api/routes/*.py`

除 `/healthz` 外，其余业务接口都通过 `/v1` 前缀挂载。

### 8.1 通用返回结构

成功响应一般形如：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

失败响应一般形如：

```json
{
  "code": 4000,
  "message": "error message",
  "data": null
}
```

### 8.2 鉴权说明

- 用户接口主要依赖 Bearer Token（`require_user_token`）
- 管理接口主要依赖管理员 Bearer Token（`require_admin_token`）
- 登录后返回 `access_token`

---

## 9. 全量接口说明

以下说明基于当前真实代码，而不是仅基于方案草案。

### 9.1 基础接口

#### `GET /healthz`

- 作用：服务健康检查
- 鉴权：否
- 返回：健康状态对象

#### `GET /v1/meta/app`

- 作用：读取应用名称和环境信息
- 鉴权：否
- 返回字段：`app_name`、`env`

---

### 9.2 用户与管理员鉴权

#### `POST /v1/auth/register`

- 作用：注册普通用户
- 鉴权：否
- 请求核心字段：`space_key`、`username`、`email`、`password`
- 返回：用户资料

#### `POST /v1/auth/login`

- 作用：普通用户登录
- 鉴权：否
- 请求核心字段：`space_key`、`username`、`password`
- 返回：`access_token` + `user`

#### `POST /v1/auth/space-enter`

- 作用：按空间字符串直接进入用户空间；当空间不存在时自动创建一个该空间用户
- 鉴权：否
- 请求核心字段：`space_key`
- 返回：`access_token` + `user`

#### `GET /v1/me`

- 作用：读取当前用户资料
- 鉴权：用户 Token

#### `POST /v1/admin/auth/login`

- 作用：管理员登录
- 鉴权：否
- 请求核心字段：`username`、`password`
- 返回：`access_token` + `admin`

#### `GET /v1/admin/me`

- 作用：读取当前管理员资料
- 鉴权：管理员 Token

---

### 9.3 文件接口

#### `POST /v1/files/upload-policy`

- 作用：申请上传策略并创建文件记录
- 鉴权：用户 Token
- 请求核心字段：
  - `filename`
  - `mime_type`
  - `file_kind`
  - `content_type`
- 当前支持 MIME：
  - `image/png`
  - `image/jpeg`
  - `application/pdf`
  - `text/plain`
  - `application/msword`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- 返回核心字段：
  - `file_id`
  - `object_key`
  - `upload_url`
  - `upload_token`
  - `max_size_bytes`
  - `accepted_as`

#### `POST /v1/files/upload-local`

- 作用：将文件实际写入本地上传目录
- 鉴权：用户 Token
- 请求方式：`multipart/form-data`
- 表单字段：`file_id`、`object_key`、`upload_file`
- 返回：`file_id`、`object_key`、`bytes_written`

#### `POST /v1/files/confirm`

- 作用：确认上传完成并写回文件元数据
- 鉴权：用户 Token
- 请求核心字段：
  - `file_id`
  - `object_key`
  - `size_bytes`
  - `mime_type`
  - `sha256`
- 返回核心字段：
  - `file_id`
  - `file_url`
  - `upload_status`
  - `file_kind`
  - `content_category`

---

### 9.4 预览与分类接口

#### `POST /v1/preview/upload-tags`

- 作用：对上传内容先做预分类与标签候选生成
- 鉴权：用户 Token
- 输入来源：
  - 已上传文件 `file_id`
  - 或直接文本 `text_content`
- 能力：
  - 文本预分类
  - PDF 前几页抽取文本
  - 图片在配置好模型时走图像分类链路
- 返回核心字段通常包含：
  - `entity_type`
  - `content_category`
  - `subject`
  - `title`
  - `normalized_text`
  - `knowledge_candidates`
  - `summary`
  - `model`
  - `confidence`
  - `needs_review`
  - `review_reason`

#### `POST /v1/notes/confirm`

- 作用：将预览结果直接确认成一条笔记，并同步落一条成功的 parse job
- 鉴权：用户 Token
- 请求核心字段：预览结果对象 + 可选 `file_id`
- 返回：完整笔记详情

---

### 9.5 内容录入与解析任务

#### `POST /v1/ingestions`

- 作用：创建一条 note 或 problem，并按需生成 parse job
- 鉴权：用户 Token
- 请求核心字段：
  - `entity_type`：`note` / `problem`
  - `file_id`
  - `text_content`
  - `subject`
  - `content_category`
  - `source_type`
  - `auto_parse`
- 返回核心字段：
  - `entity_type`
  - `entity_id`
  - `parse_job_id`
  - `parse_status`
  - `content_category`

#### `GET /v1/parse-jobs/{job_id}`

- 作用：查询当前用户自己的解析任务结果
- 鉴权：用户 Token
- 返回核心字段：
  - `id`
  - `status`
  - `entity_type`
  - `entity_id`
  - `content_category`
  - `result`
  - `error_message`
  - `attempt_count`
  - `created_at`
  - `updated_at`

#### `POST /v1/parse-jobs/{job_id}/retry`

- 作用：管理员重试失败或待处理的解析任务
- 鉴权：管理员 Token
- 限制：仅 `failed` 或 `pending` 允许重试

#### `GET /v1/admin/parse-jobs`

- 作用：管理员查看解析任务列表
- 鉴权：管理员 Token
- 查询参数：`status`
- 返回字段包括：任务状态、实体类型、尝试次数、错误信息、创建时间等

---

### 9.6 错题接口

#### `GET /v1/problems`

- 作用：获取当前用户错题列表
- 鉴权：用户 Token
- 查询参数：`subject`、`category`
- 返回字段：`id`、`title`、`subject`、`category`、`parse_status`、`stem_text`、`created_at`

#### `GET /v1/problems/{problem_id}`

- 作用：获取错题详情
- 鉴权：用户 Token
- 返回字段：
  - `id`
  - `title`
  - `subject`
  - `category`
  - `parse_status`
  - `stem_text`
  - `normalized_stem`
  - `answer_text`
  - `explanation_text`
  - `created_at`
  - `updated_at`

#### `PATCH /v1/problems/{problem_id}`

- 作用：更新错题内容
- 鉴权：用户 Token
- 说明：按提交字段做部分更新

---

### 9.7 笔记接口

#### `GET /v1/notes`

- 作用：获取当前用户笔记列表
- 鉴权：用户 Token
- 查询参数：`subject`、`category`
- 返回字段除基础信息外，还包含文件信息与标签信息

#### `GET /v1/notes/{note_id}`

- 作用：获取单条笔记详情
- 鉴权：用户 Token
- 返回字段包括：
  - 基础文本信息
  - `file_id` / `file_url`
  - `original_filename`
  - `mime_type`
  - `file_kind`
  - `tags`
  - `created_at` / `updated_at`

#### `PATCH /v1/notes/{note_id}`

- 作用：更新笔记字段并可同步更新标签
- 鉴权：用户 Token
- 特点：如果请求内包含 `tags`，会调用标签同步逻辑

#### `DELETE /v1/notes/{note_id}`

- 作用：删除笔记，并级联删除相关 parse jobs 与 review tasks
- 鉴权：用户 Token

#### `POST /v1/notes/confirm`

- 作用：把上传预览结果直接确认成最终笔记
- 鉴权：用户 Token

---

### 9.8 审核接口

#### `GET /v1/review/tasks`

- 作用：管理员查看审核任务列表
- 鉴权：管理员 Token
- 查询参数：`task_type`、`status`、`entity_type`

#### `POST /v1/review/tasks/{task_id}/decision`

- 作用：提交审核结论
- 鉴权：管理员 Token
- 请求核心字段：
  - `action`：`approve` / `reject` / `replace`
  - `edited_tags`
- 行为说明：
  - `approve`：标记通过
  - `reject`：标记拒绝
  - `replace`：替换标签，并回写 parse job 结果与 canonical tags

---

### 9.9 搜索接口

#### `GET /v1/search`

- 作用：跨错题与笔记做全文样式搜索
- 鉴权：用户 Token
- 查询参数：
  - `q`（必填）
  - `limit`
  - `offset`
  - `type`
  - `subject`
  - `category`
- 当前实现特点：
  - 基于 SQL `ilike`
  - 聚合 `Problem` 与 `Note`
  - `document-note` 会作为 note 的细分类型返回

---

### 9.10 图谱接口

#### `GET /v1/graph/overview`

- 作用：聚合知识点概览
- 鉴权：用户 Token
- 数据来源：最近最多 100 条带 `result_json` 的 parse jobs
- 返回内容：
  - `nodes`：按知识点置信度累计权重排序
  - `total_problems`
  - `total_notes`

#### `GET /v1/graph/weak-tags`

- 作用：输出薄弱知识点列表
- 鉴权：用户 Token
- 计算方式：对解析结果中每个标签的 `1 - confidence` 做累计排序

---

### 9.11 解题接口

#### `POST /v1/solve`

- 作用：调用 AI 解题链路
- 鉴权：用户 Token
- 请求核心字段：`question_text`、`subject`、`allow_ai_fallback`
- 当前限制：`allow_ai_fallback=false` 不支持，因为当前实现是 **AI-only solve pipeline**

---

### 9.12 仪表盘与管理接口

#### `GET /v1/dashboard`

- 作用：学生端仪表盘数据
- 鉴权：用户 Token
- 返回字段：
  - `today_problem_count`
  - `today_note_count`
  - `pending_review_count`
  - `pending_parse_job_count`
  - `failed_parse_job_count`

#### `GET /v1/admin/monitor/overview`

- 作用：管理端运行总览
- 鉴权：管理员 Token
- 返回字段包括：
  - 服务状态
  - parse job 总数 / 待处理 / 失败数
  - 最近错误
  - API 请求数与平均耗时
  - 用户数、笔记数
  - 用户笔记统计

#### `GET /v1/admin/runtime-config/models`

- 作用：读取运行时模型配置
- 鉴权：管理员 Token

#### `PUT /v1/admin/runtime-config/models`

- 作用：更新运行时模型配置
- 鉴权：管理员 Token

---

## 10. 本地开发

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

## 11. 测试与验证

### Playwright E2E

```bash
npm install
npx playwright test
```

子集脚本：

```bash
npm run test:e2e:student
npm run test:e2e:student-upload
npm run test:e2e:student-search
npm run test:e2e:student-solve
npm run test:e2e:admin
```

### 脚本化检查

可参考：

- `scripts/smoke_check.py`
- `scripts/regression_check.py`

---

## 12. 部署建议

当前最小部署方式仍然遵循 `smartnote` 的 MVP 思路：

1. 一台 Linux 云主机
2. Docker + Docker Compose
3. PostgreSQL 容器化
4. 前端静态托管
5. 后端 + worker 共用同一套环境变量
6. 上传目录挂卷持久化

推荐排障命令：

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f student-frontend
docker compose logs -f admin-frontend
```

---

## 13. 开发原则

结合 `smartnote` 方案与当前代码，可以把这个项目的原则概括为：

1. **只做 MVP 必需链路**：先把上传、解析、搜索、图谱、解题跑通。
2. **先接口契约，再前后端联动**：README 与后端路由需要成为对外契约。
3. **AI 给建议，不直接做真相**：标签可审核、可替换、可人工修正。
4. **先统一部署，后复杂拆分**：首阶段避免 Kafka / Celery / K8s 这类高运维复杂度方案。
5. **优先可演示、可排障、可验收**：这也是 `smartnote` 整套方案文档的核心目标。

---

## 14. 已知限制

- 当前图谱是知识点聚合视图，不是真正的图数据库实现。
- 当前搜索主要是 `ilike` 风格检索，不是完整向量检索系统。
- 当前 `/v1/solve` 是 AI-only 流程，还未实现“本地题库命中优先、未命中再回退 AI”的完整双通道。
- 当前仓库还存在其他未提交改动，发布 README 时应注意只提交文档相关变更。

---

## 15. 发布前安全检查

- 不要提交 `.env`
- 不要保留默认 JWT 密钥上线
- 不要公开真实管理员初始密码
- 不要把上传文件、日志、测试结果、数据库备份一起推到公开仓库

如果你想继续完善项目，建议优先阅读：

- `D:\vibe_coding\smartnote\01_项目总体要求_路线图_技术栈_时间计划.md`
- `D:\vibe_coding\smartnote\12_API接口契约草案.md`
- `apps/backend/app/api/router.py`
- `apps/backend/app/api/routes/`
