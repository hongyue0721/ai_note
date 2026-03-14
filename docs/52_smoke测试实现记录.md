# Smoke 测试实现记录

## 1. 本次目标

补充自动化最小回归脚本。

## 2. 当前状态

当前已完成：

1. 增加 smoke 脚本；
2. 准备远端执行。

## 3. 本次新增文件

- `scripts/smoke_check.py`

## 4. 远端执行结果

已在远端执行通过：

- 登录
- `/v1/me`
- `/v1/problems`
- `/v1/notes`
- `/v1/search`
- `/v1/graph/overview`
- `/v1/graph/weak-tags`

终端输出：`smoke-check-ok`

## 5. 2026-03-13 补充验证

本轮继续在远端通过 SSH 做了补充验证，确认：

1. `GET /healthz` 正常；
2. 现有主干接口在当前远端数据库状态下可正常访问；
3. 新增上传链路的本地文件存储语义已可用：
   - `POST /v1/files/upload-policy`
   - `POST /v1/files/confirm`
4. `/uploads/...` 静态文件路径已在远端实测可访问。

## 6. 当前 smoke 缺口

现有 `scripts/smoke_check.py` 还未覆盖：

1. `/healthz`
2. `POST /v1/files/upload-policy`
3. `POST /v1/files/confirm`
4. `/uploads/...` 本地静态文件访问

下一步应在 smoke 脚本中把这些链路补进去。

## 7. 2026-03-13 扩展 smoke 实测结果

本轮已继续扩展 `scripts/smoke_check.py`，并在远端通过以下方式执行：

```text
SMOKE_BASE_URL=http://127.0.0.1:8000
SMOKE_UPLOADS_ROOT=/root/note/data/uploads
python3 scripts/smoke_check.py
```

远端输出结果：

```text
smoke-check-ok
```

说明当前 smoke 已覆盖并通过：

1. `GET /healthz`
2. 用户登录与 `/v1/me`
3. `/v1/problems`
4. `/v1/notes`
5. `/v1/search`
6. `/v1/graph/overview`
7. `/v1/graph/weak-tags`
8. `POST /v1/files/upload-policy`
9. `POST /v1/files/confirm`
10. `/uploads/...` 静态文件访问验证
