
- 决定保留 `storage_provider`、`object_key`、`file_url` 字段，不做 schema 推翻，以便后续从本地磁盘迁移到对象存储时保持业务兼容。
- 决定让 `object_key` 只表达相对路径，真实磁盘根目录交由配置 `UPLOADS_ROOT_DIR` 管理。
- 决定让 `file_url` 先统一生成 `/uploads/{object_key}`，静态挂载在下一步实现，而不是继续沿用 MinIO URL。
- 决定将 `UPLOADS_ROOT_DIR=data/uploads` 解释为仓库根目录相对路径，而不是 backend 工作目录相对路径，避免本地/远端启动方式不一致时目录漂移。
