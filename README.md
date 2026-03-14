# StarGraph AI（星图智学）

比赛演示版 MVP 仓库。

当前仓库从方案文档起步，正在逐步落成可运行代码。首轮目标不是一次性做完整系统，而是先把以下最小骨架搭起来：

- 后端 API 服务壳（FastAPI）
- Worker 任务进程壳
- 前端 Web/H5 演示壳
- 共享契约与存储适配层目录
- Docker Compose 本地启动骨架
- 持续更新的开发进度交接文档

## 项目结构

```text
smartnote/
  apps/
    backend/
    frontend/
    worker/
  docs/
  infra/
    docker/
  libs/
    shared_schemas/
    storage_adapter/
  README.md
  .env.example
  docker-compose.yml
```

## 当前阶段

当前阶段：**比赛演示版 MVP 骨架初始化**

优先级：

1. 跑通后端基础服务
2. 明确环境变量与本地启动方式
3. 为登录 / 上传 / 解析任务 / 图谱展示预留结构
4. 后续再补真实业务接口与前端页面

## 必读文档

- `docs/00_开发进度与交接记录.md`
- `01_项目总体要求_路线图_技术栈_时间计划.md`
- `11_数据库核心表设计草案.md`
- `12_API接口契约草案.md`

## 当前可见进展

- 已建立项目代码骨架
- 已建立后端最小 FastAPI 应用入口
- 已建立 worker 占位入口
- 已建立本地环境变量模板与 Docker Compose 骨架

## 当前未完成

- 数据库模型与迁移
- 登录与 JWT
- 上传策略与文件确认
- ingestion / parse_jobs 业务链路
- 前端真实页面与接口联调
- MinIO / Gemini / PostgreSQL 接入

## 开发原则

- 只做比赛演示版 MVP 必需内容
- 先接口、再链路、后体验优化
- 每次改动必须同步写入 md 进度文档
