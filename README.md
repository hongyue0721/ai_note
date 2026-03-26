# StarGraph AI（星图智学）

StarGraph AI 是一个面向学习笔记、题目解析与后台运维管理的全栈项目。当前仓库已经包含可运行的 student 用户端、admin 管理端、FastAPI backend、parse-job worker、PostgreSQL 持久化，以及基于 OpenAI 兼容网关的分类与解题能力。

## 文档入口

- `docs/01_system-overview.md`：系统功能、模块职责、数据流说明
- `docs/02_api-spec.md`：当前后端接口规范
- `docs/03_deployment-and-operations.md`：本地与 Docker Compose 部署、运行和运维说明
- `docs/04_tech-stack.md`：技术栈、依赖与架构选型说明

## 当前系统组成

- **backend**：FastAPI 服务，提供用户/管理员鉴权、文件上传、预览分类、ingestion、parse jobs、review、notes、problems、search、graph、solve、dashboard、runtime config 等接口
- **worker**：轮询 pending parse jobs，调用 backend 服务逻辑完成分类/解析，并同步实体 `parse_status`
- **student frontend**：用户通过 `space_key` 进入空间，完成上传笔记、询问问题、笔记管理、搜索、详情查看、标签编辑、下载原文件等操作
- **admin frontend**：管理员登录后查看数据管理页与管理设置页，处理运行时模型配置与管理员登录信息修改
- **postgres**：项目主数据库，持久化用户、管理员、文件、笔记、题目、parse jobs、review tasks、运行时模型配置等数据

## 核心能力

- 用户通过 `/v1/auth/space-enter` 进入专属空间并获得 JWT
- 管理员通过 `/v1/admin/auth/login` 登录，并可修改用户名/密码
- 文件上传采用 `upload-policy -> upload-local -> confirm` 三段式链路
- 上传文件可先走 `/v1/preview/upload-tags` 做预览分类，再确认入库
- `note` / `problem` 实体支持入库、查询、编辑、删除与 parse status 跟踪
- worker 处理 parse jobs，并驱动搜索、图谱概览、弱项标签等能力的数据来源
- `/v1/solve` 提供 AI-only 解题结果，student 端支持 Markdown 渲染与“加入笔记”
- admin 端支持运行时文本模型 / 视觉模型配置

## 目录结构

```text
note/
  apps/
    backend/
    frontend/
      admin/
      student/
    worker/
  docs/
  infra/
  tests/
  scripts/
  docker-compose.yml
```

## 快速启动

```bash
docker compose up -d --build
```

默认端口：

- `8000` backend
- `3000` student frontend
- `3001` admin frontend

PostgreSQL 仅在容器内部网络使用，不再对宿主机公网开放。
