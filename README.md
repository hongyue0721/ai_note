# StarGraph AI（星图智学）

StarGraph AI 是一个面向学习笔记、题目解析与后台运维管理的全栈项目。当前仓库已经包含可运行的 student 用户端、admin 管理端、FastAPI backend、parse-job worker、PostgreSQL 持久化，以及基于 OpenAI 兼容网关的分类与解题能力。

## 文档入口

- `docs/01_system-overview.md`：系统功能、模块职责、数据流说明
- `docs/02_api-spec.md`：当前后端接口规范
- `docs/03_deployment-and-operations.md`：本地与 Docker Compose 部署、运行和运维说明
- `docs/04_tech-stack.md`：技术栈、依赖与架构选型说明

## 当前系统组成

- **backend**：FastAPI 服务，提供用户/管理员鉴权、文件上传、预览分类、ingestion、parse jobs、review、notes、problems、search、graph、solve、dashboard、runtime config 等接口
- **worker**：轮询 pending parse jobs，调用 backend 服务逻辑完成分类/解析，并同步实体 `parse_status`
- **student frontend**：用户通过 `space_key` 进入空间，完成上传笔记、询问问题、笔记管理、搜索、详情查看、标签编辑、下载原文件等操作
- **admin frontend**：管理员登录后查看数据管理页与管理设置页，处理运行时模型配置与管理员登录信息修改
- **postgres**：项目主数据库，持久化用户、管理员、文件、笔记、题目、parse jobs、review tasks、运行时模型配置等数据

## 核心能力

- 用户通过 `/v1/auth/space-enter` 进入专属空间并获得 JWT
- 管理员通过 `/v1/admin/auth/login` 登录，并可修改用户名/密码
- 文件上传采用 `upload-policy -> upload-local -> confirm` 三段式链路
- 上传文件可先走 `/v1/preview/upload-tags` 做预览分类，再确认入库
- `note` / `problem` 实体支持入库、查询、编辑、删除与 parse status 跟踪
- worker 处理 parse jobs，并驱动搜索、图谱概览、弱项标签等能力的数据来源
- `/v1/solve` 提供 AI-only 解题结果，student 端支持 Markdown 渲染与“加入笔记”
- admin 端支持运行时文本模型 / 视觉模型配置

## 目录结构

```text
note/
  apps/
    backend/
    frontend/
      admin/
      student/
    worker/
  docs/
  infra/
  tests/
  scripts/
  docker-compose.yml
```

## 快速启动

```bash
docker compose up -d --build
```

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
=======
默认端口：

- `8000` backend
- `3000` student frontend
- `3001` admin frontend

PostgreSQL 仅在容器内部网络使用，不再对宿主机公网开放。
>>>>>>> fix/worker-db-retry
