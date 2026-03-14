# Worker

当前 worker 负责未来的解析任务轮询与 AI 调用。

## 本轮已完成

- 建立独立 worker 目录
- 提供可启动的占位入口
- 明确后续会接入 parse_jobs 任务轮询

## 当前未完成

- 数据库轮询
- 任务状态机
- Gemini 调用
- 失败重试与日志打点

## 本地运行

```bash
python main.py
```
