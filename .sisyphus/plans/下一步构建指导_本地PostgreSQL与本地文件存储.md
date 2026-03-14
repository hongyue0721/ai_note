# 下一步构建指导：本地 PostgreSQL + 本地文件存储

## TL;DR
> **Summary**: 本文档用于指导下一位执行型 AI 在 `D:\vibe_coding\note` 基础上继续构建 Smartnote 比赛级完整成品。核心技术决策已固定为：**本地 PostgreSQL + 本地文件存储**。同时明确当前已完成内容、未完成事项、推荐执行顺序、必须遵守的实现边界与每一步验收方式。
> **Deliverables**:
> - 当前系统完成度总览
> - 未完成事项分级清单（按优先级）
> - 本地 PostgreSQL 方案
> - 本地文件存储方案
> - 下一位 AI 的分阶段操作指导
> - 每一阶段的验收标准
> - 风险、默认值、迁移路径
> **Effort**: Large
> **Parallel**: YES - 4 waves
> **Critical Path**: AI 配置 → 真实 AI 联调 → 本地存储落地 → 前端成品化 → 部署固定化

## Context
### Original Request
用户要求：
- 将未完成的项目**详细**写入 md 文档
- 明确采用 **本地 PostgreSQL + 本地文件存储** 作为存储方案
- 文档要足够细，能让下一步 AI 直接按文档继续构建

### Interview Summary
当前仓库 `D:\vibe_coding\note` 已从骨架推进到“比赛级可运行主干”阶段：
- 后端已完成用户/管理员鉴权、文件记录、ingestion、parse jobs、worker 框架、review、dashboard/monitor、problems/notes list-detail、solve/search/graph 路由、admin parse-jobs、内容 patch 接口
- 学生端与后台端已搭建并可 build
- 远端服务器 `root@146.190.84.189` 可用于验证
- OpenAI 相关代码已接入，但**缺真实配置联调**
- 部署编排已补一部分，但**未完全固定为长期运行方案**

### Gaps Addressed in This Guide
本指南专门解决以下问题：
- 当前到底完成到哪一步？
- 还差哪些事？
- 以后怎么继续干？
- 本地 PostgreSQL 和本地文件存储具体怎么落？
- 下一位 AI 要按什么顺序继续做？

## Work Objectives
### Core Objective
给下一位执行型 AI 一份**决策完整**的操作指导文档，使其不需要重新判断架构方向，直接按既定方案推进项目。

### Deliverables
- 一套明确的本地存储架构
- 一套明确的剩余任务优先级
- 一套明确的实施顺序
- 一套明确的目录、路径、环境变量、部署方式建议
- 一套明确的验收标准

### Definition of Done
本文档完成后，应满足：
- [ ] 下一位 AI 能清楚知道当前系统的完成度
- [ ] 下一位 AI 能直接照着文档继续施工
- [ ] 本地 PostgreSQL + 本地文件存储方案不留判断空白
- [ ] 所有未完成事项都有优先级和操作导向

### Must Have
- 明确说明当前已完成/未完成项
- 明确本地 PostgreSQL 连接与用途
- 明确本地文件目录结构与文件元数据存法
- 明确部署与验证顺序
- 明确下一步 AI 的执行建议

### Must NOT Have
- 不允许把文件二进制塞进数据库
- 不允许在没有必要的情况下重构已完成主干
- 不允许引入重型企业级复杂架构
- 不允许把当前比赛级项目错误升级成“全量商业级系统”

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification should be agent-executed where possible.
- Test decision: tests-after + smoke verification
- QA policy: 每个关键阶段必须至少有一次本地 build 或远端 smoke 验证
- Evidence:
  - `docs/34_OpenAI接入实现记录.md`
  - `docs/36_AI分类Agent实现记录.md`
  - `docs/38_Solve服务实现记录.md`
  - `docs/40_搜索服务实现记录.md`
  - `docs/42_图谱服务实现记录.md`
  - `docs/52_smoke测试实现记录.md`

## Current State Audit
### Already Implemented (Confirmed)
#### Backend
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `GET /v1/me`
- `POST /v1/admin/auth/login`
- `GET /v1/admin/me`
- `POST /v1/files/upload-policy`
- `POST /v1/files/confirm`
- `POST /v1/ingestions`
- `GET /v1/parse-jobs/{job_id}`
- `POST /v1/parse-jobs/{job_id}/retry`
- `GET /v1/problems`
- `GET /v1/problems/{problem_id}`
- `PATCH /v1/problems/{problem_id}`
- `GET /v1/notes`
- `GET /v1/notes/{note_id}`
- `PATCH /v1/notes/{note_id}`
- `GET /v1/review/tasks`
- `POST /v1/review/tasks/{task_id}/decision`
- `GET /v1/dashboard`
- `GET /v1/admin/monitor/overview`
- `GET /v1/admin/parse-jobs`
- `POST /v1/solve`
- `GET /v1/search`
- `GET /v1/graph/overview`
- `GET /v1/graph/weak-tags`

#### Worker
- `apps/worker/main.py` 可轮询 parse jobs
- 已支持 mock 分类执行
- 已支持在配置 OpenAI key 时切入真实 classifier 路径
- 低置信度可自动进入 `review_tasks`

#### Frontend
##### Student
- 登录
- 上传表单
- 文件种类与分类选择
- 文件选择器
- 最近任务状态区
- 内容列表与详情卡片
- 搜索区
- 图谱概览展示

##### Admin
- 管理员登录
- 审核任务列表
- 审核操作
- 监控总览
- 解析任务列表

#### Docs / Traceability
- `docs/01` ~ `docs/52` 已形成完整阶段留痕

### Not Fully Completed
#### AI / Agent Layer
- 真实 OpenAI 配置尚未提供
- 未完成真实 OpenAI 联调验证
- `solve_history` 未实现
- 未实现 AI 结果独立历史表

#### Search / Graph
- 目前为比赛级轻量实现
- 无分页、复杂筛选、独立图谱数据层

#### Frontend Productization
- 学生端与后台端仍偏单页/大面板结构
- 未做完整多路由页面体系
- 上传体验仍未做到进度条/拖拽/PDF预览

#### Deployment
- Docker Compose 已扩，但未完成远端整套 `compose up -d` 实测
- 未配置长期运行方案（systemd/nginx/caddy）

#### Testing
- 已有 smoke test，但无完整 E2E 和 API 回归体系

## Architecture Decision: Local PostgreSQL + Local File Storage
### Final Decision
当前项目统一采用：

1. **本地 PostgreSQL** 存结构化数据
2. **本地磁盘目录** 存原始文件
3. 数据库记录文件元数据与业务数据

### Why This Is the Right Choice Now
- 当前系统已经按 PostgreSQL 建模，不需要重构
- 比赛级项目追求“能跑、能验收、能演示”，本地方案更快
- 本地文件存储比 MinIO / S3 简单，减少当前复杂度
- 后续如需迁移到对象存储，只需保留 `files` 表的 `object_key` / `file_url` / `storage_provider` 兼容层即可

### Local PostgreSQL Standard
#### Recommended Defaults
- Host: `localhost`
- Port: `5432`
- DB Name: `stargraph`
- User: `postgres`
- Password: 自定义本地密码

#### Connection String
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/stargraph
```

#### Scope of PostgreSQL
PostgreSQL 存：
- 用户与管理员
- 文件元数据
- problems / notes
- parse_jobs
- review_tasks
- solve 结果（后续建议补历史表）

### Local File Storage Standard
#### Storage Root
统一使用本地目录：

Windows 开发：
```text
D:\vibe_coding\note\data\uploads
```

Linux/远端：
```text
/root/note/data/uploads
```

#### Directory Layout
建议按如下路径组织：
```text
data/uploads/{user_id}/{content_category}/{yyyy}/{mm}/{uuid}-{filename}
```

示例：
```text
data/uploads/d734a183/problem/2026/03/abc-math.png
data/uploads/d734a183/document/2026/03/xyz-biology-notes.pdf
```

#### Files Table Requirements
`files` 表必须持续保存：
- `id`
- `user_id`
- `object_key`（本地相对路径）
- `file_url`（静态访问地址）
- `mime_type`
- `file_kind`
- `content_category`
- `size_bytes`
- `sha256`
- `upload_status`
- `storage_provider`（建议后续默认写 `local`）

### Static Serving Strategy
建议后端后续增加本地静态文件暴露：
- URL: `/uploads/...`
- 将 `data/uploads` 挂为静态目录

Windows 开发：本地路径映射
Linux/远端：`/root/note/data/uploads`

### Migration Path to MinIO / S3
当前不做对象存储，但必须保留兼容点：
- 业务逻辑读取 `files.object_key`
- 业务逻辑读取 `files.file_url`
- 业务逻辑读取 `files.storage_provider`

未来迁移时：
- 本地路径 -> MinIO 对象 key
- 本地 URL -> CDN / 对象存储 URL
- 上层业务无需大改

## Execution Strategy
### Parallel Execution Waves
Wave 1: AI 真实联调
- 1. 提供真实 OpenAI 环境变量
- 2. 远端 `.env` 注入 OpenAI 配置
- 3. 真实调用 classifier
- 4. 真实调用 `/v1/solve`

Wave 2: 本地存储落地
- 5. 改 upload-policy / confirm 支持本地文件方案
- 6. 增加本地存储路径生成逻辑
- 7. 增加静态目录暴露

Wave 3: 前端成品化
- 8. 学生端多视图/多路由细化
- 9. 后台任务页独立化
- 10. solve 结果前端展示

Wave 4: 部署与验证
- 11. 完整 compose 联调
- 12. systemd/nginx/caddy 固定化
- 13. 扩展 smoke / E2E 测试

### Dependency Matrix
- OpenAI 真实联调 依赖 已实现的 OpenAI client / classifier / solver
- 本地文件存储 依赖 现有 files 表和 upload 接口
- 前端成品化 依赖 search/graph/solve API 已存在
- 部署固定化 依赖 compose 和 frontend Dockerfile 已存在

## Detailed TODOs for Next AI Builder

- [ ] 1. 真实 OpenAI 配置联调

  **What to do**:
  - 在远端 `/root/note/.env` 中加入：
    - `OPENAI_API_KEY`
    - `OPENAI_BASE_URL`（如有）
    - `OPENAI_MODEL_CLASSIFY`
    - `OPENAI_MODEL_SOLVE`
  - 启动 backend，执行一次最小分类与 solve 验证

  **Must NOT do**:
  - 不要把 key 写进仓库文件
  - 不要把真实 key 写入 docs

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: 涉及真实 AI 联调与错误处理
  - Skills: `[]`
  - Omitted: `frontend-ui-ux` — Reason: 当前不是 UI 任务

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: [2, 3] | Blocked By: []

  **References**:
  - `apps/backend/app/services/llm_client.py` — OpenAI 统一入口
  - `apps/backend/app/services/classifier.py` — 分类 service
  - `apps/backend/app/services/solver.py` — solve service
  - `docs/34_OpenAI接入实现记录.md`

  **Acceptance Criteria**:
  - [ ] 远端带真实 OpenAI 配置时，`python -c "from app.services.classifier import classify_content ..."` 可返回真实结果
  - [ ] 远端 `POST /v1/solve` 可返回真实 AI 结果

  **QA Scenarios**:
  ```
  Scenario: 真实分类成功
    Tool: Bash
    Steps: 在远端启动 backend，构造一个 parse job，让 worker 执行一次
    Expected: parse_job.result_json 不再是 mock 内容，llm_model 有值
    Evidence: docs/新增阶段实现记录

  Scenario: OpenAI key 缺失
    Tool: Bash
    Steps: 去掉 OPENAI_API_KEY 后再执行 worker
    Expected: worker 自动回退 mock，不崩溃
    Evidence: docs/新增阶段实现记录
  ```

  **Commit**: NO

- [ ] 2. 将上传链路切到本地文件存储

  **What to do**:
  - 设计本地路径生成器
  - 修改 `files/upload-policy` 与 `files/confirm` 返回的路径与 URL
  - 将 `storage_provider` 的默认语义转为 `local`
  - 明确 `object_key` 使用相对路径

  **Must NOT do**:
  - 不要把文件内容写进数据库
  - 不要删除后续对象存储兼容字段

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: 涉及后端、路径设计、后续迁移兼容
  - Skills: `[]`

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: [3] | Blocked By: [1]

  **References**:
  - `apps/backend/app/api/routes/files.py`
  - `apps/backend/app/models/file.py`
  - `docs/28_阶段9_数据库轻量补列记录.md`

  **Acceptance Criteria**:
  - [ ] `upload-policy` 返回本地路径语义
  - [ ] `confirm` 返回本地静态 URL 语义

  **QA Scenarios**:
  ```
  Scenario: 图片上传路径生成
    Tool: Bash
    Steps: 调用 upload-policy -> confirm
    Expected: object_key 落到本地 uploads 目录结构约定下
    Evidence: docs/新增阶段实现记录

  Scenario: PDF 上传路径生成
    Tool: Bash
    Steps: 调用 upload-policy -> confirm
    Expected: content_category=document 时路径分层正确
    Evidence: docs/新增阶段实现记录
  ```

  **Commit**: NO

- [ ] 3. 增加本地静态文件暴露

  **What to do**:
  - 在 FastAPI 中挂载 `/uploads`
  - 将本地上传目录映射为静态目录

  **Must NOT do**:
  - 不要暴露整个项目目录
  - 不要把私有配置目录当静态目录挂出去

  **Acceptance Criteria**:
  - [ ] 上传后的文件 URL 可直接访问

- [ ] 4. 前端成品化补完

  **What to do**:
  - 学生端补多视图/路由（如有时间）
  - 补 solve 结果展示区域
  - 补后台任务页独立区域

  **Acceptance Criteria**:
  - [ ] 学生端可完整展示上传 -> 分类 -> 内容 -> 搜索 -> 图谱 -> solve
  - [ ] 后台端可展示审核 / 监控 / parse jobs

- [ ] 5. 部署固定化

  **What to do**:
  - 实测 `docker compose up -d`
  - 规划 `nginx` 或 `caddy`
  - 如不用 compose 常驻，则补 `systemd`

  **Acceptance Criteria**:
  - [ ] 在远端能稳定启动 backend / worker / student / admin / postgres

- [ ] 6. 测试收口

  **What to do**:
  - 扩展 `scripts/smoke_check.py`
  - 增加 solve / admin parse-jobs / upload 分类验证

  **Acceptance Criteria**:
  - [ ] smoke script 覆盖主要主干

## Final Verification Wave
- [ ] F1. Route Audit — 确认新增路由在 `app.main` 中真实可注册
- [ ] F2. Local Storage Audit — 确认文件不入数据库、路径设计统一
- [ ] F3. Remote Smoke — 远端运行 smoke 并记录结果
- [ ] F4. Docs Audit — 确认每一步都有实现记录

## Commit Strategy
- 当前阶段继续按“文档留痕 + 远端验证”推进
- 未经明确要求，不主动 git commit

## Success Criteria
- 下一位 AI 能直接依据本文档继续施工，无需重新判断架构
- 本地 PostgreSQL + 本地文件存储方案已明确
- 未完成项有明确优先级与操作说明
- 所有建议均与当前仓库现实状态一致
