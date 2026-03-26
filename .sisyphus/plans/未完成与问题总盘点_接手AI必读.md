# 未完成与问题总盘点（接手 AI 必读）

## TL;DR
> **Summary**: 本文档汇总 `D:\vibe_coding\note` 当前所有**未完成事项**与**已定位但尚未修复的问题**，并明确哪些工作已经完成、哪些仍阻塞、哪些文档已经过期。下一位 AI 应以本文档和最新代码/远端状态为准，不要再从旧计划重新判断主线。
> **Project Goal**: 比赛级 AI 学习整理系统，目标是“能运行、能演示、能验收”的完整成品。
> **Fixed Architecture**: **本地 PostgreSQL + 本地文件存储**。不要改回 MinIO 主路径，不要把文件二进制存数据库。
> **Most Important Remaining Work**: 真实 AI 联调修通 → PostgreSQL 配置不一致修复 → 远端 `docker compose up -d` 全链路实跑 → 长期运行方案 → 更完整前端成品化与 E2E。

---

## 1. 当前哪些已经完成（不要重做）

### 1.1 后端主干已完成

已存在并可用的主干接口/能力：

- 用户/管理员鉴权
- ingestion / parse jobs / worker 框架
- review / dashboard / monitor
- problems / notes 列表、详情、patch
- `GET /v1/search`
- `GET /v1/graph/overview`
- `GET /v1/graph/weak-tags`
- `POST /v1/solve`
- `GET /v1/admin/parse-jobs`
- `GET /healthz`

### 1.2 本地文件存储主线已完成

已完成：

- `STORAGE_PROVIDER=local`
- `object_key` 相对路径规则
- `file_url=/uploads/{object_key}`
- FastAPI 挂载 `/uploads`
- `POST /v1/files/upload-local`
- 真实文件内容落盘

### 1.3 真实文件写盘闭环已完成

已在远端完成验证：

- `upload-policy -> upload-local -> confirm -> ingestions`
- 文件真实写入 `/root/note/data/uploads/...`
- `/uploads/...` 可读回真实内容
- SHA256 一致

### 1.4 smoke 已扩展并通过

当前已覆盖：

- `/healthz`
- `/v1/me`
- `/v1/problems`
- `/v1/notes`
- `/v1/search`
- `/v1/graph/overview`
- `/v1/graph/weak-tags`
- `/v1/files/upload-policy`
- `/v1/files/confirm`
- `/uploads/...` 静态访问

### 1.5 compose 去 MinIO 收口已完成

已完成：

- 从 `docker-compose.yml` 移除 `minio`
- 去掉 backend/worker 对 MinIO 的依赖
- 为 backend / worker 挂载 `./data/uploads:/app/data/uploads`

### 1.6 远端前端同步与构建验证已完成

已完成：

- 远端补齐 `apps/frontend/student` 与 `apps/frontend/admin`
- 最新 student/admin 源码已同步到远端
- 远端无 `node`，改用 Docker 验证
- `frontend-student.Dockerfile` 构建通过
- `frontend-admin.Dockerfile` 构建通过

---

## 2. 当前仍未完成的事项（按优先级）

## P0：最高优先级 / 主阻塞

### P0-1 真实 AI 主链路联调已完成，剩余工作转为失败路径回归验证

#### 当前状态

最新真实配置已写入远端 backend 工作目录环境：

- `OPENAI_BASE_URL=http://159.223.81.110:8317/v1`
- `OPENAI_MODEL_CLASSIFY=glm-4.6v`
- `OPENAI_MODEL_SOLVE=LongCat-Flash-Chat`
- `OPENAI_API_KEY` 已设置

后端配置层已确认能正确读取这些值。

并且从远端直接验证通过：

- TCP 到 `159.223.81.110:8317` 可达
- `GET /v1/models` → `200`
- `POST /v1/chat/completions` → `200`

#### 当前状态补充

业务主链路已完成：

1. `solver.py` 已通过 prompt + 兼容归一化层修通；
2. `classifier` 真实调用已成功；
3. `/v1/solve` route-level 已成功；
4. 当前 AI 侧剩余重点已不再是主链路或主要失败路径，而是更完整回归测试沉淀。

#### 本轮新增验证结果

已验证并形成证据的失败路径：

1. 缺少 `OPENAI_API_KEY` → `code=5001`
2. 错误 `OPENAI_BASE_URL` / 超时 → `code=5002`
3. 错误模型名 → `code=5002`
4. classifier 返回不兼容 schema → `code=5005`
5. solver 返回 non-JSON → `code=5008`
6. classifier 返回 non-JSON → `code=5007`

#### 涉及文件

- `apps/backend/app/services/llm_client.py`
- `apps/backend/app/services/solver.py`
- `apps/backend/app/schemas/solve.py`
- `apps/backend/app/prompts/solve_prompt.txt`
- `apps/backend/app/services/classifier.py`
- `apps/backend/app/prompts/classify_prompt.txt`

#### 下一步应该做什么

1. 如有需要，把失败路径验证沉淀为脚本或回归用例
2. 把最新失败路径结论同步到更多旧文档
3. 继续把精力转向 volume / 代理 / E2E / 前端成品化

#### 当前验收结论

- `solve_with_ai()` 成功返回 `SolveResultData`
- `/v1/solve` 返回 `200` 且结构正确
- classifier 返回 `ClassificationResult`
- 关键失败路径已有明确错误码与消息，不再是模糊 500

---

### P0-2 PostgreSQL 配置不一致 / 某些上下文密码错误

#### 当前状态

在某次路由级 `TestClient` 验证 `/v1/solve` 时，出现：

```text
password authentication failed for user "postgres"
```

这说明当前存在一个独立问题：

> 某些 backend 运行上下文读取到的 PostgreSQL 连接配置与实际数据库密码不一致。

#### 重要说明

这个问题和 AI 网关不是一回事：

- AI 网关现在可达
- DB 密码不一致是另外一个配置问题

#### 涉及文件

- `apps/backend/app/core/config.py`
- `/root/note/apps/backend/.env`
- 远端 PostgreSQL 实际用户/密码配置

#### 需要检查的点

1. backend 工作目录真实读取的是哪份 `.env`
2. PostgreSQL 实际密码是什么
3. `database_url` 是否和实际密码一致
4. 为什么某些路径可登录，某些 TestClient 上下文失败

#### 验收标准

- 在所有 backend 启动与测试上下文中都能稳定连接同一数据库
- 不再出现 `password authentication failed for user "postgres"`

---

## P1：强影响比赛展示效果（产品成品感缺口）

### P1-1 学生端仍然只是最小可演示版本，不是完整产品页体系

#### 当前状态

学生端已经有：

- 登录
- 上传
- 解析任务
- 搜索
- 图谱概览
- solve 最小展示
- 搜索结果联动详情

#### 仍未完成的点

1. 更完整详情页或独立路由
2. 更成熟上传交互：
   - 拖拽
   - 上传进度
   - 文件预览
3. 更完整图谱页
4. solve 结果展示进一步产品化
5. 页面结构仍偏“大单页”，信息密度高、导航不够清晰

#### 涉及文件

- `apps/frontend/student/src/App.vue`
- `apps/frontend/student/src/style.css`
- `docs/43_学生端增强计划.md`
- `docs/44_学生端增强实现记录.md`
- `docs/55_前端与Smoke补完实现记录.md`

---

### P1-2 后台端仍缺更成熟的管理体验

#### 当前状态

后台端已经具备：

- 登录
- 审核任务
- 监控总览
- parse jobs 状态筛选 / 分组 / failed 重试入口

#### 仍未完成的点

1. 更复杂筛选组合
2. 更丰富任务详情 / 错误排障视图
3. 更完整统计与失败原因聚合
4. 管理页仍偏“最小功能可用”，不是成熟比赛终态

#### 涉及文件

- `apps/frontend/admin/src/App.vue`
- `apps/frontend/admin/src/style.css`
- `docs/45_后台任务页计划.md`
- `docs/46_后台任务页实现记录.md`

---

## P2：部署与运行固定化缺口

### P2-1 远端 `docker compose up -d` 全链路实跑已完成（本项已从主阻塞移除）

#### 当前状态

已在远端完成实测：

1. `docker compose up -d --build` 已执行；
2. `postgres` / `backend` / `student-frontend` / `admin-frontend` 已启动；
3. `GET /healthz` 已通过；
4. `scripts/smoke_check.py` 已在 compose 后端上返回 `smoke-check-ok`；
5. `/root/note` 当前已经具备可运行的 compose 演示环境。

#### 本轮修复的真实问题

1. 宿主机旧 `uvicorn` 进程占用 `8000`，导致 backend 容器首次无法绑定；
2. `resolved_uploads_root_dir` 对固定路径层级的假设在容器内失效，已修复；
3. `backend` / `worker` 容器内数据库连接已改为使用 compose 服务名 `postgres`。

#### 涉及文件

- `docker-compose.yml`
- `infra/docker/backend.Dockerfile`
- `infra/docker/worker.Dockerfile`
- `infra/docker/frontend-student.Dockerfile`
- `infra/docker/frontend-admin.Dockerfile`
- `docs/57_部署编排本地文件存储收口记录.md`

#### 证据来源

- `docs/59_远端Compose全链路实跑与容器化修复记录.md`
- `docs/57_部署编排本地文件存储收口记录.md`
- `docker-compose.yml`
- `apps/backend/app/core/config.py`

#### 当前新的结论

`docker compose up -d` 已不再是主阻塞；worker 常驻化与 Postgres 命名卷迁移也已完成。部署侧真正剩余的是“公网入口/反向代理”。

---

### P2-2 长期运行方案已完成首轮固定化（systemd + docker compose）

#### 当前状态

本轮已完成：

1. 新增 `infra/systemd/stargraph-compose.service`；
2. 远端已安装并 `enable` 该 unit；
3. `systemctl restart stargraph-compose.service` 后完整栈可恢复；
4. systemd 状态为 `active (exited)`，符合 `oneshot + RemainAfterExit=yes` 预期。
5. 远端 PostgreSQL 已迁移到命名卷 `note_postgres_data`；
6. `stargraph-compose.service` 已移除旧匿名 volume ID 依赖。

#### 当前仍未完成的点

1. 固定 backend / student / admin 的公网或统一反向代理入口
2. 是否增加 nginx / caddy 统一外部入口

#### 证据

- `infra/systemd/stargraph-compose.service`
- 远端 `systemctl status stargraph-compose.service`
- 远端 compose 后端 `GET /healthz` 成功

---

### P2-3 worker 常驻化已完成（本项已从未完成队列移除）

#### 当前状态

`apps/worker/main.py` 已改为持续轮询模式：

1. 无 pending job 时不会退出；
2. 远端重建后 `stargraph-worker` 保持 `Up`；
3. 该项已不再是部署阻塞。

---

## P3：测试与质量保证缺口

### P3-1 浏览器级 E2E 仍未建立

#### 当前状态

smoke 已扩展，`scripts/regression_check.py` 也已补齐，但完整浏览器级 E2E 仍然没有。

#### 缺失项

1. 学生端 UI 主流程 E2E
2. 后台端 UI 主流程 E2E
3. 浏览器级自动化回归用例

#### 验收标准

- 至少一条学生端主流程 E2E
- 至少一条后台端主流程 E2E
- AI 联调成功后补一条真实 AI 回归链路

---

### P3-2 smoke 虽然已经扩展，但 docs 里仍有时间差

#### 当前状态

最新 smoke 已通过，但部分旧文档仍保留旧表述。

#### 当前风险

下一位 AI 若误读早期文档，可能重复做已完成工作。

---

## P4：已定位但尚未修复的问题（问题清单）

### Q1. 已从“solve schema 不兼容”转为“失败路径验证仍可继续补充”

**严重级别**：Critical

**当前结论**：

- `solve` 主链路已通过 `_normalize_solve_payload()` 修通；
- `classifier.py` 与 `solver.py` 已补充更明确的 schema 失败错误；
- 剩余可继续补的是“非 JSON 返回”等更完整失败样例覆盖。

---

### Q2. PostgreSQL 密码配置在不同运行上下文不一致（主问题已缓解，但仍建议继续收口）

**严重级别**：High

**现象**：

- 某些验证能正常走通
- 某些 `TestClient` 路由验证报：`password authentication failed for user "postgres"`

**当前补充结论**：

- 容器化链路已通过覆盖 `DATABASE_URL` 指向 `postgres:5432` 跑通；
- 路由级 solve 之前的密码错误已通过重设 postgres 密码缓解；
- 但宿主机直跑、容器内运行、远端既有数据卷复用三条路径仍建议继续统一文档与环境来源。

---

### Q3. 旧文档包含已过时结论

**严重级别**：Medium

典型例子：

- `docs/53_本地文件存储链路实现记录.md` 中保留过时的远端阻塞描述
- `docs/32_下一阶段AI构建详细任务清单.md` 里某些接口实现状态已过期

**结论**：

- 接手时优先看最新：`54/56/57 + .sisyphus/plans/未完成事项总清单_下一步AI构建.md`

---

## 3. 仍然推荐的接手顺序

### Wave 1：先修最关键阻塞

1. 补齐剩余真实 AI 失败路径验证（尤其非 JSON）
2. 继续收口 PostgreSQL 环境来源与 volume 规范化
3. 重跑真实 classifier 与 `/v1/solve` 回归

### Wave 2：再做部署完善

4. 固定外部访问入口与反向代理
5. 规范 PostgreSQL volume 与环境来源
6. 继续补部署恢复文档

### Wave 3：最后做产品感与测试增强

7. 学生端更完整详情页 / 上传 UX / 图谱页
8. 后台更完整筛选 / 排障视图
9. E2E / 回归测试

---

## 4. 接手前建议必读文件

1. `.sisyphus/plans/项目介绍摘要_新执行者必读.md`
2. `.sisyphus/plans/开工清单_下一步执行摘要.md`
3. `.sisyphus/plans/未完成事项总清单_下一步AI构建.md`
4. `docs/54_当前完成度与未完成项同步说明.md`
5. `docs/56_真实文件写盘闭环实现记录.md`
6. `docs/57_部署编排本地文件存储收口记录.md`

---

## 5. 一句话结论

> 当前项目已经完成了本地文件存储、真实文件落盘、真实 AI 主链路联调、远端前端同步与 Docker 构建、compose 去 MinIO 收口、远端 compose 全链路实跑、worker 常驻化、systemd 固定化；真正还没做完且最关键的，是 **剩余 AI 失败路径覆盖（尤其非 JSON）+ PostgreSQL volume/环境规范化 + 公网入口/反向代理 + 更完整产品化/E2E**。
