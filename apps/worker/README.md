# Worker

worker 是独立的后台轮询进程，用于消费 `pending` parse jobs 并调用 backend 共享服务逻辑完成内容分类与解析。

## 职责

- 轮询待处理 parse jobs
- 执行 `process_parse_job(...)`
- 推动任务状态从 `pending -> running -> success/failed`
- 把 `parse_status` 同步到 note / problem 实体
- 在数据库暂时不可用时按固定间隔重试

## 本地运行

```bash
cd apps/worker
python main.py
```

## 说明

- worker 通过 `sys.path` 复用 backend 的 `app/` 目录代码
- worker 与 backend 共用数据库和运行时模型配置
