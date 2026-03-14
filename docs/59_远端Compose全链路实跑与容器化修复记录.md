# 远端 Compose 全链路实跑与容器化修复记录

## 1. 本次目标

完成 `root@146.190.84.189` 上的 `docker compose up -d` 全链路实跑，并确认容器化后的 backend / postgres / frontends 能真正启动，而不是只停留在 Docker build 成功。

## 2. 本次远端环境结论

远端机器当前已确认：

1. 项目目录存在：`/root/note`
2. Docker 已安装：`28.2.2`
3. Docker Compose plugin 已安装：`v2.29.7`
4. Python 3 已可用

## 3. 首次 compose 实跑遇到的问题

### 3.1 既有 PostgreSQL 容器名冲突

首次执行 `docker compose up -d --build` 时失败，错误为：

- `stargraph-postgres` 容器名已被现有容器占用

进一步检查后确认：

1. 既有 `stargraph-postgres` 不是无关容器，而是当前项目正在使用的数据库；
2. 数据库里已有核心表：
   - `users`
   - `admin_users`
   - `files`
   - `parse_jobs`
   - `problems`
   - `notes`
   - `review_tasks`
3. 其数据存放在一个匿名 Docker volume 中。

因此不能粗暴删除数据卷重建，否则会破坏当前远端数据状态。

### 3.2 compose 内部数据库连接地址错误

远端 `/root/note/.env` 里的：

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/stargraph
```

对宿主机直跑 backend 是成立的，但对容器内的 `backend` / `worker` 不成立，因为容器内的 `localhost` 指向容器自身，而不是 compose 的 `postgres` 服务。

### 3.3 旧宿主机 uvicorn 占用 8000

在解决 PostgreSQL 复用后，compose 第二次启动时又被阻塞：

- `0.0.0.0:8000` 已被占用

定位发现是之前用于 smoke 验证的宿主机 `uvicorn` 进程仍在运行，而不是新的容器问题。

### 3.4 backend 容器路径解析 bug

即便端口占用解除后，backend 容器仍启动失败。日志显示：

```text
IndexError: 4
```

根因在于：

- `apps/backend/app/core/config.py`
- `resolved_uploads_root_dir`

原逻辑使用：

```python
Path(__file__).resolve().parents[4]
```

这在本地仓库路径下凑巧可用，但在容器内文件路径 `/app/app/core/config.py` 下层级不够，直接触发 `IndexError`。

## 4. 本次修改内容

### 4.1 `docker-compose.yml`

已补充/调整：

1. 为 `backend` / `worker` 覆盖容器内 `DATABASE_URL`，改为使用 compose 服务名 `postgres`；
2. 移除废弃的 `version` 顶层字段；
3. 为 `postgres_data` 增加 `POSTGRES_VOLUME_NAME` 可配置名称，以便在远端复用现有 volume。

### 4.2 `apps/backend/app/core/config.py`

已修复 `resolved_uploads_root_dir`：

1. 不再依赖固定 `parents[4]`；
2. 改为以 backend 应用根目录为基准解析相对路径；
3. 同时兼容宿主机运行与 Docker 容器运行。

## 5. 远端最终实跑结果

在远端设置：

```bash
export POSTGRES_VOLUME_NAME=506caac6050782847dca21d46723de7164252edc6893ffaf3b526527adde696c
```

后，已完成：

1. 复用旧 PostgreSQL 数据卷；
2. 清理旧宿主机 `uvicorn` 进程；
3. 重新执行 compose 启动；
4. backend 重新 build 并成功启动。

最终验证结果：

### 5.1 容器状态

- `stargraph-postgres`：Up
- `stargraph-backend`：Up
- `stargraph-student-frontend`：Up
- `stargraph-admin-frontend`：Up

### 5.2 后端健康检查

```text
GET http://127.0.0.1:8000/healthz
=> {"code":0,"message":"ok","data":{"status":"ok"}}
```

### 5.3 smoke 验证

在 compose 后端上执行：

```bash
SMOKE_BASE_URL=http://127.0.0.1:8000 \
SMOKE_UPLOADS_ROOT=/root/note/data/uploads \
python3 scripts/smoke_check.py
```

结果：

```text
smoke-check-ok
```

### 5.4 前端入口验证

- `http://127.0.0.1:3000/` → `HTTP 200`
- `http://127.0.0.1:3001/` → `HTTP 200`

## 6. 当前仍未完成 / 新的精确结论

### 6.1 `docker compose up -d` 主目标已完成

这项不再属于未完成阻塞。

### 6.2 worker 常驻化已完成

本轮已将 `apps/worker/main.py` 从“一次性批处理”改为持续轮询：

1. 无 pending job 时不退出；
2. 会按固定 polling interval 持续查询；
3. 远端重新 build 后，`stargraph-worker` 已验证保持 `Up`。

因此 worker 常驻化不再属于未完成项。

### 6.3 PostgreSQL volume 仍依赖远端已有匿名卷

当前虽已跑通，但远端数据库数据卷仍是：

- 历史匿名卷复用

后续若要更规范化，需要决定是否：

1. 把它收口为明确命名的 external volume；
2. 或做一次可控数据迁移，再切回标准 compose volume 名。

### 6.4 对外访问与长期运行方案已部分收口，但公网入口仍未最终完成

当前验证是服务器本机访问：

- backend: `127.0.0.1:8000`
- student: `127.0.0.1:3000`
- admin: `127.0.0.1:3001`

本轮已完成：

1. 新增 `infra/systemd/stargraph-compose.service`；
2. 已在远端安装并启用 `stargraph-compose.service`；
3. `systemctl status stargraph-compose.service` 已验证为 `active (exited)`；
4. 通过 systemd 重启 compose 后，backend / worker / frontends / postgres 均恢复并通过健康检查。

仍未做：

1. Nginx/Caddy 反向代理；
2. 域名/公网入口；
3. 更清晰的生产/演示访问路径。

## 7. 对下一位 AI 的建议

下一步不要再重复“compose 能不能跑起来”这条线，而应直接继续：

1. 继续补真实 AI 失败路径回归；
2. 规范 PostgreSQL volume 策略；
3. 更新 `.sisyphus/plans` 中仍保留旧阻塞描述的段落；
4. 继续补产品化与 E2E。
