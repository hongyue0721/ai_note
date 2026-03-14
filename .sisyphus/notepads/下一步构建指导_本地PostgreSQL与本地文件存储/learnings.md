
- 当前上传链路核心位于 `apps/backend/app/api/routes/files.py`。
- 旧逻辑使用 `/dev/...` object_key 与 `http://localhost:9000/...` file_url，和计划中的本地文件存储方案不一致。
- 本次已将默认存储语义改为 `local`，并将公开 URL 统一收敛到 `/uploads/{object_key}`，为后续 FastAPI 静态挂载做准备。
- FastAPI 静态目录挂载应放在 `apps/backend/app/main.py`，并且 uploads 根目录不能简单依赖当前工作目录，需要解析到仓库根目录。
