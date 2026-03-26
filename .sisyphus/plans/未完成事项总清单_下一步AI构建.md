# 未完成事项总清单（下一步 AI 构建）

## TL;DR
> **Summary**: 本文档汇总 `D:\vibe_coding\note` 当前所有已确认的未完成事项、阻塞、验收标准与下一步推荐顺序，供下一位执行型 AI 直接继续施工，不需要重新摸索项目目标、架构方向或近期变更。
> **Project Goal**: 这是一个面向学生的比赛级 AI 学习整理系统，不是企业级 SaaS。目标是“能运行、能演示、能验收”的完整成品。
> **Fixed Architecture**: **本地 PostgreSQL + 本地文件存储**。不要改回 MinIO 优先、云对象存储优先或 SQLite 主存储。
> **Most Important Remaining Work**: 真实 AI 联调 → 文件真实写盘 → 远端前端同步与构建 → compose/长期运行固定化 → 更完整前端成品化 → 更完整测试体系。

---

## 1. 项目是干什么的

这是一个将学生学习材料转为“**可整理、可搜索、可关联、可复盘**”的系统，处理对象包括：

- 错题图片
- 笔记图片
- PDF / doc / txt 学习文档
- 文本题目或笔记

学生主流程是：

1. 注册 / 登录
2. 上传资料
3. 选择内容分类（problem / note / document）
4. 系统创建 ingestion + parse job
5. worker 执行解析/分类
6. 生成结构化结果与知识点候选
7. 低置信度进入审核队列
8. 学生端查看内容、搜索结果、图谱概览
9. 题库未命中时使用 AI 参考解析（solve）

后台主流程是：

1. 管理员登录
2. 查看监控总览
3. 查看审核任务
4. 审核低置信度内容
5. 查看 parse jobs 列表与状态

---

## 2. 当前已经完成到什么程度

以下内容已在代码、文档或远端验证中确认完成。

### 2.1 后端主干已完成

已存在并可注册/调用的主干接口包括：

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
- `GET /healthz`

### 2.2 Worker 已完成

- 可轮询 parse jobs
- 支持 mock 处理
- 已接入真实 AI 分类代码路径
- 未配置 OpenAI 时可回退 mock

### 2.3 本地文件存储语义已完成

这条主线是最近已经推进完成的，不再属于“未完成”：

- `STORAGE_PROVIDER` 默认值已改为 `local`
- `UPLOADS_ROOT_DIR` / `UPLOADS_URL_BASE` 已加入配置层
- `object_key` 已改为相对路径
- `file_url` 已改为 `/uploads/{object_key}`
- FastAPI 已挂载 `/uploads` 静态目录

当前 `object_key` 规则已符合：

```text
{user_id}/{content_category}/{yyyy}/{mm}/{uuid}-{filename}
```

### 2.3.1 真实文件写盘闭环也已完成

最近已继续补齐并验证：

- 新增 `POST /v1/files/upload-local`
- 学生端改为 `upload-policy -> upload-local -> confirm -> ingestions`
- 远端已验证真实文件内容可写入 `/root/note/data/uploads/{object_key}`
- 远端已验证 `/uploads/{object_key}` 可返回真实文件内容

证据请看：

- `docs/56_真实文件写盘闭环实现记录.md`

### 2.4 前端当前已达到的状态

学生端当前已具备：

- 登录
- 文件选择器
- 上传记录 + ingestion + parse job 主流程
- 搜索区
- 图谱概览
- 最近内容列表与详情展示
- 最小 solve 展示区
- 搜索结果与详情联动的最小版本

后台端当前已具备：

- 管理员登录
- 审核任务列表与操作
- 监控总览
- parse jobs 列表
- parse jobs 的最小状态筛选 / 分组 / failed 重试入口

### 2.5 远端已验证通过的事项

远端服务器：`root@146.190.84.189`

已通过 SSH 实测：

- `GET /healthz`
- `POST /v1/auth/login`
- `GET /v1/me`
- `GET /v1/problems`
- `GET /v1/notes`
- `GET /v1/search`
- `GET /v1/graph/overview`
- `GET /v1/graph/weak-tags`
- `POST /v1/files/upload-policy`
- `POST /v1/files/confirm`
- `/uploads/...` 静态路径可访问

### 2.6 smoke 已扩展并通过

当前 `scripts/smoke_check.py` 已覆盖并在远端跑通：

- `/healthz`
- 登录 / `/v1/me`
- `/v1/problems`
- `/v1/notes`
- `/v1/search`
- `/v1/graph/overview`
- `/v1/graph/weak-tags`
- `/v1/files/upload-policy`
- `/v1/files/confirm`
- `/uploads/...` 静态访问

远端执行结果：

```text
smoke-check-ok
```

---

## 3. 已确认的技术前提（不要再重新判断）

### 3.1 存储方向已定死

- 结构化数据：**PostgreSQL**
- 文件本体：**本地磁盘目录**

不要做：

- 把文件二进制存数据库
- 把当前比赛级项目重构成复杂微服务
- 无必要引入重型中间件

### 3.2 AI API 调用前提（已新增确认）

用户已明确说明：

> **AI API 调用格式是 OpenAI 格式，并且使用自定义 base URL。**

这意味着后续“真实 AI 联调”要遵守：

- 继续使用 OpenAI-compatible chat/completions 风格调用
- 通过自定义 `OPENAI_BASE_URL` 指向实际网关
- 不要把实现方向改为其他 SDK 协议

### 3.3 健康检查路径是 `/healthz`

不是 `/health`。

后续任何 smoke、部署探活、反向代理健康检查都应优先使用：

```text
GET /healthz
```

### 3.4 远端当前验证方式以 SSH 为准

本轮已用 `ssh root@146.190.84.189` 直接验证。后续不要再假设远端未配置或不可用，应默认：

- 远端存在项目副本 `/root/note`
- 远端 Python 环境已可用于后端验证
- 远端可继续承担真实联调与部署收口工作

---

## 4. 所有未完成事项总表

下面是当前仍然**没有做完**、或者只做了最小版本、尚未达到计划终态的事项。

---

## 5. P0：必须优先完成（核心功能缺口）

### P0-1 真实 AI 配置联调已完成（本项已从未完成队列移除）

**当前结果**

- 已切换到可达新网关：`http://159.223.81.110:8317/v1`
- 远端后端已能正确读取真实配置
- `/v1/models` → 200
- `/v1/chat/completions` → 200
- 真实 `classifier` 已成功返回 `ClassificationResult`
- 真实 `solve` 已成功返回 `SolveResultData`
- route-level `/v1/solve` 已成功返回 200

**证据来源**

- `docs/58_真实AI联调与Solve兼容修复记录.md`
- `apps/backend/app/services/llm_client.py`
- `apps/backend/app/services/classifier.py`
- `apps/backend/app/services/solver.py`

---

### P0-2 文件“真实写盘”已完成（本项已从未完成队列移除）

**当前结果**

- 已新增 `POST /v1/files/upload-local`
- 学生端已改为：`upload-policy -> upload-local -> confirm -> ingestions`
- 已在远端应用内 `TestClient` 验证：
  - 文件真实写入 `/root/note/data/uploads/...`
  - `/uploads/...` 静态读取成功
  - SHA256 一致

**证据来源**

- `docs/56_真实文件写盘闭环实现记录.md`
- `apps/backend/app/api/routes/files.py`
- `apps/frontend/student/src/App.vue`

---

### P0-3 真实 AI 失败路径与回退路径的端到端验证不足

**当前状态**

本轮已形成主要真实失败路径证据：

- key 缺失 → 已验证
- base URL 错误 / 超时 → 已验证
- 模型名错误 → 已验证
- classifier 不兼容 schema → 已验证
- 返回非 JSON → 已验证

**必须完成的事项**

1. 若有需要，把失败路径验证沉淀成固定脚本
2. 继续确保错误信息对后续调试足够清晰

**当前结果**

已验证：

- 缺 key → `code=5001`
- base URL 错误 / 超时 → `code=5002`
- 模型名错误 → `code=5002`
- classifier schema 不兼容 → `code=5005`
- solver non-JSON → `code=5008`
- classifier non-JSON → `code=5007`

因此 AI 失败路径当前已不再属于核心未完成阻塞。

---

## 6. P1：强影响比赛展示效果（成品感缺口）

### P1-1 学生端仍然不是完整产品页体系

**当前状态**

- 学生端已有单页比赛级界面
- 已补了最小 solve 展示和搜索联动
- 但仍然偏“单页大面板”，不是完整产品流

**尚未做满的点**

1. 更完整详情页路由或独立视图
2. 更成熟的上传交互：
   - 拖拽
   - 进度条
   - 预览
3. solve 展示继续收口成更完整结构
4. 搜索结果跳转/联动更顺滑
5. 图谱页或更完整图谱视图

**当前证据**

- `docs/43_学生端增强计划.md`
- `docs/44_学生端增强实现记录.md`
- `docs/55_前端与Smoke补完实现记录.md`
- `apps/frontend/student/src/App.vue`

**验收标准**

- 学生端可以更清晰地展示：上传 → 解析 → 内容 → 搜索 → 图谱 → solve
- 用户不需要在一个过大的单页里来回找区域

---

### P1-2 后台端仍然缺更成熟的管理能力

**当前状态**

- 已有 parse jobs 列表
- 已有最小筛选 / 分组 / failed 重试入口

**仍未做满的点**

1. 更完整筛选能力（多维度而不是单状态）
2. 更清晰的任务分组和统计
3. 更完整的失败任务排障体验
4. 若有必要，补管理员详情视图或任务详情视图

**当前证据**

- `docs/45_后台任务页计划.md`
- `docs/46_后台任务页实现记录.md`
- `docs/55_前端与Smoke补完实现记录.md`
- `apps/frontend/admin/src/App.vue`

---

### P1-3 前端远端同步 / build 已完成（本项已从未完成队列移除）

**当前结果**

- 已在远端补齐 `apps/frontend/student` 与 `apps/frontend/admin` 目录；
- 最新 student/admin 前端源码已同步到远端；
- 远端无 `node` 命令，因此改用 Docker 验证构建；
- `frontend-student.Dockerfile` 构建通过；
- `frontend-admin.Dockerfile` 在补齐 `index.html` / `public` / `assets` 后构建通过。

**证据来源**

- `docs/57_部署编排本地文件存储收口记录.md`
- 远端 Docker build 日志

---

## 7. P2：部署与运行固定化缺口

### P2-1 `docker-compose.yml` 与当前固定架构已基本一致（本项已从未完成队列移除）

**当前结果**

已完成：

1. `minio` 已从 compose 中移除；
2. `backend` / `worker` 不再依赖 `minio`；
3. `backend` / `worker` 已挂载本地 uploads 目录；
4. 容器内 `DATABASE_URL` 已覆盖为指向 compose `postgres` 服务；
5. 远端 compose 已成功启动 backend/postgres/frontends。

**补充说明**

本轮另修复了一个此前未暴露出的容器化问题：

- `apps/backend/app/core/config.py` 的 uploads 路径解析不兼容容器路径层级，现已修复。

**证据来源**

- `docker-compose.yml`
- `apps/backend/app/core/config.py`
- `docs/57_部署编排本地文件存储收口记录.md`
- `docs/59_远端Compose全链路实跑与容器化修复记录.md`

---

### P2-2 远端 `docker compose up -d` 还没有完整固定化

**当前状态**

这条主线已完成到“可运行”阶段：

1. 远端 `docker compose up -d --build` 已成功执行；
2. backend / postgres / student / admin 已启动；
3. compose 后端 `/healthz` 已通过；
4. compose 后端 smoke 已通过。

**补充进展**

本轮已继续完成：

1. `apps/worker/main.py` 已改为持续轮询；
2. 远端 `stargraph-worker` 已验证保持 `Up`；
3. 已新增 `infra/systemd/stargraph-compose.service`；
4. 远端已安装并启用 `stargraph-compose.service`；
5. systemd 管理下完整栈已恢复并通过 `/healthz`。
6. 远端 PostgreSQL 已从匿名 volume 迁移到命名卷 `note_postgres_data`；
7. `stargraph-compose.service` 已移除匿名 volume ID 依赖；
8. 远端 `:3000` / `:3001` 已再次验证返回 `HTTP 200`。

**仍需完成的事项**

1. 确认远端访问入口稳定并形成固定文档

**验收标准**

- 在远端能稳定重启恢复完整比赛级演示环境

---

### P2-3 长期运行方案尚未固定

**当前状态**

- 首轮固定化已完成为 `systemd + docker compose`
- 远端已不再依赖人工 SSH 手动拉起完整栈

**候选方案**

- `docker compose` 常驻
- `systemd`
- 再补 `nginx` / `caddy` 反向代理

**仍需完成的事项**

1. 明确 backend/student/admin 的固定公网或代理访问入口
2. 若需要，补反向代理与健康检查

**验收标准**

- 重启服务器后，服务可稳定恢复
- 访问入口固定，不依赖手动 SSH 启动

---

### P2-4 worker 常驻化已完成（本项已从未完成队列移除）

**当前结果**

已完成：

1. `apps/worker/main.py` 已改为持续轮询；
2. 无 pending job 时 worker 不再退出；
3. 远端 compose 重建后 `stargraph-worker` 已验证 `Up`。

---

## 8. P3：测试与质量保证缺口

### P3-1 仍然没有完整 E2E 测试体系

**当前状态**

- smoke 已有并且已经扩展到 detail / solve 主路径
- 已新增最小 regression 脚本覆盖 user/admin 主流程
- 但还没有完整浏览器级 E2E

**缺失内容**

1. 学生端真实 UI 流程 E2E
2. 后台端真实 UI 流程 E2E
3. 浏览器级自动化回归体系

**必须完成的事项**

1. 至少补一组学生端主流程 E2E
2. 至少补一组后台端主流程 E2E
3. 把“上传真实文件 -> 解析 -> 列表/搜索/图谱 -> solve”串起来做浏览器级验证

---

### P3-2 smoke 与文档存在时间差，需要继续收口

**当前状态**

- `docs/52_smoke测试实现记录.md` 早期记录里写过旧状态
- 后来已补记扩展 smoke
- 但整个仓库里仍存在一些旧计划/旧实现记录与当前现实不完全同步的情况

**必须完成的事项**

1. 后续每完成一个阶段，继续更新 docs
2. 重要变化要写明“旧状态已过期，以最新文档为准”
3. 尽量避免下一位 AI 被旧记录误导

---

## 9. P4：文档与现实不一致的点（需要特别注意）

### P4-1 某些旧文档已过期，不可当最新事实

例如：

- `docs/32_下一阶段AI构建详细任务清单.md` 中仍写着 `/v1/solve`、`/v1/search`、`/v1/graph/*` 未实现，但这些现在已实现

所以使用文档时应遵守：

1. 早期计划文档用于理解历史意图
2. 最新现实状态以：
   - 当前代码
   - 最新 docs（52/53/54/55）
   - 远端 SSH 验证结果
   为准

### P4-2 `docs/53` 中保留过一次已过时的远端阻塞描述

`docs/53_本地文件存储链路实现记录.md` 里保留了一个阶段性判断：

- “远端部署与 smoke 收口需要先处理 passlib/bcrypt 阻塞”

但后续远端最新验证已证明：

- 当前后端实际已能启动
- 旧日志不应再当作当前主结论

后续 AI 阅读时必须结合：

- `docs/21_远程部署与验证记录.md` 最新章节
- 本轮 SSH 实测结果

### P4-3 远端 docs 并非全部与本地同步

本轮确认：

- `docs/53_本地文件存储链路实现记录.md` 已同步到远端
- 但 `docs/54_当前完成度与未完成项同步说明.md`、`docs/55_前端与Smoke补完实现记录.md` 在一次检查时尚未同步到远端

所以后续若在远端继续工作：

1. 先同步最新 docs
2. 再按最新 docs 开工

---

## 10. 下一位 AI 最推荐的执行顺序

如果下一位 AI 继续施工，建议严格按下面顺序：

### Wave 1：真实 AI 联调

1. 在远端 `.env` 注入真实 OpenAI-compatible 配置
2. 确认 `OPENAI_BASE_URL` 使用自定义 base URL
3. 验证 classifier 真实结果
4. 验证 `/v1/solve` 真实结果
5. 补失败路径验证（key/base_url/model/timeout）

### Wave 2：真实文件写盘闭环

6. 补齐文件实体真实落盘链路
7. 用真实上传文件验证：数据库记录 + 磁盘文件 + `/uploads` 可访问

### Wave 3：远端前端同步与构建

8. 确认远端 student/admin 目录结构
9. 同步本轮本地前端变更到远端正确目录
10. 重新 build 前端
11. 确认远端看到的是最新 student/admin 页面

### Wave 4：部署固定化

12. 固定公网入口/反向代理
13. 规范 PostgreSQL volume 与远端访问入口
14. 补部署恢复与运维文档

### Wave 5：更完整前端成品化 + 更完整测试

15. 补多页面路由/详情页/上传体验
16. 补更强后台任务页能力
17. 建立更完整 E2E / 回归测试

---

## 11. 建议下一位 AI 开工前先读的文件

按优先级建议阅读：

1. `.sisyphus/plans/项目介绍摘要_新执行者必读.md`
2. `.sisyphus/plans/开工清单_下一步执行摘要.md`
3. `.sisyphus/plans/下一步构建指导_本地PostgreSQL与本地文件存储.md`
4. `docs/54_当前完成度与未完成项同步说明.md`
5. `docs/21_远程部署与验证记录.md`
6. `docs/52_smoke测试实现记录.md`
7. `docs/53_本地文件存储链路实现记录.md`
8. `docs/55_前端与Smoke补完实现记录.md`

---

## 12. 一句话结论

> 当前项目主干已经成型，**“本地文件存储语义 + `/uploads` 静态暴露 + 真实文件写盘 + 真实 AI 联调 + 远端 compose 全链路实跑 + worker 常驻化 + systemd 固定化” 已完成**；真正还没做完的核心是 **失败路径回归验证、PostgreSQL volume 规范化、公网入口/反向代理和更完整成品化收口**。
