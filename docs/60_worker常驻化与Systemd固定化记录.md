# worker 常驻化与 Systemd 固定化记录

## 1. 本次目标

在已经跑通远端 compose 的基础上，继续完成两件仍然真实未完的事情：

1. 把 worker 从“一次性批处理后退出”改成常驻后台进程；
2. 把远端启动方式固定为 `systemd + docker compose`，避免依赖人工 SSH 拉起。

## 2. worker 常驻化修改

修改文件：

- `apps/worker/main.py`

修改前：

1. 最多轮询 10 次；
2. 没有 pending job 就退出；
3. 导致 compose 中 `stargraph-worker` 很快 `Exited (0)`。

修改后：

1. 改为 `while True` 持续轮询；
2. 每次 poll 使用新的 `SessionLocal()`，避免长期复用同一 DB session；
3. 没有 pending job 时 sleep 后继续，不再退出；
4. 处理完单个任务后继续下一轮轮询。

## 3. compose 固定化补充

修改文件：

- `docker-compose.yml`

新增内容：

1. `postgres` / `backend` / `worker` / `student-frontend` / `admin-frontend`
2. 全部增加：

```yaml
restart: unless-stopped
```

这样即使 Docker daemon 或机器重启，容器也具备更稳定的恢复行为。

## 4. systemd 固定化

新增文件：

- `infra/systemd/stargraph-compose.service`

内容采用：

- `Type=oneshot`
- `RemainAfterExit=yes`
- `WorkingDirectory=/root/note`
- `ExecStart=/usr/bin/docker compose up -d --remove-orphans`
- `ExecStop=/usr/bin/docker compose down`

当时为了复用远端历史 PostgreSQL 数据，曾临时通过 `POSTGRES_VOLUME_NAME` 指向既有匿名 volume。

该做法现已过期：

- 远端数据已迁移到命名卷 `note_postgres_data`
- `stargraph-compose.service` 也已移除匿名 volume ID 依赖

## 5. 远端安装与验证结果

在 `root@146.190.84.189` 上已完成：

1. 创建 `/root/note/infra/systemd/`
2. 同步 `stargraph-compose.service`
3. 安装到 `/etc/systemd/system/stargraph-compose.service`
4. 执行：

```bash
systemctl daemon-reload
systemctl enable stargraph-compose.service
systemctl restart stargraph-compose.service
```

### 5.1 systemd 状态

已验证：

```text
Active: active (exited)
```

这对 `oneshot + RemainAfterExit=yes` 来说是正确状态，不是失败。

### 5.2 容器状态

已验证远端：

- `stargraph-postgres`：Up
- `stargraph-backend`：Up
- `stargraph-worker`：Up
- `stargraph-student-frontend`：Up
- `stargraph-admin-frontend`：Up

### 5.3 backend 健康检查

已验证：

```text
GET http://127.0.0.1:8000/healthz
=> {"code":0,"message":"ok","data":{"status":"ok"}}
```

### 5.4 worker 常驻验证

重新 build worker 后，已验证：

```text
stargraph-worker|Up ...
```

说明 worker 不再是以前的 `Exited (0)` 状态。

## 6. 这次完成后，哪些事项已从未完成队列移除

本轮可以从未完成队列移除：

1. worker 常驻化；
2. 远端长期运行方案的首轮固定化（systemd + compose）。

## 7. 当前仍未完成的部署事项

部署相关仍未完成的，只剩这些更后期的收尾项：

1. Nginx/Caddy/域名/公网入口；
2. 更清晰的访问路径与演示入口文档；
3. 更系统的 E2E / 回归测试沉淀。

## 8. 对下一位 AI 的提醒

不要再重复做：

1. “worker 为什么退出” 这条线；
2. “systemd 能不能拉起 compose” 这条线。

这两项现在都已经有代码、远端验证与文档证据。

下一步应优先去做：

1. 公网入口 / 反向代理；
2. E2E 与产品化收尾。
