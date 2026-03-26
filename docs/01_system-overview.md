# 系统总览

## 1. 项目目标

StarGraph AI 是一个面向学习内容管理与题目解析的全栈系统。它支持用户按空间进入工作台、上传/整理笔记、向 AI 提问并将结果沉淀为笔记，同时提供管理员页面查看系统状态并修改运行时模型配置。

## 2. 系统组成

### student frontend

学生端是 Vue 3 单页应用，当前包含以下主流程：

- 空间登录：通过 `space_key` 进入专属空间
- 上传笔记：拖拽或选择文件，预览标签后确认入库
- 询问问题：输入文本，可附带文件内容，调用 AI 解题
- 笔记管理：浏览、搜索、查看详情、编辑、删除、下载原文件
- 图谱/标签视图：基于历史 parse result 展示知识点概览

### admin frontend

管理员端是 Vue 3 单页应用，当前分为两页：

- 数据管理：状态与接口指标观察、用户笔记数量详情
- 管理设置：修改管理员登录信息、修改运行时文本模型/视觉模型配置

### backend

backend 基于 FastAPI，负责：

- 用户与管理员鉴权
- 文件上传策略、本地写盘与上传确认
- 上传预览分类
- 内容入库（notes / problems）
- parse jobs 管理与查询
- review tasks 管理
- 搜索、图谱、仪表盘、AI 解题
- 管理员运行时模型配置

### worker

worker 独立轮询 parse jobs，将待处理内容执行分类/解析流程，并回写任务与实体状态。

### postgres

PostgreSQL 负责持久化用户、管理员、文件、笔记、题目、parse jobs、review tasks、runtime config 等数据。

## 3. 关键业务流

### 上传笔记

1. student 请求 `/v1/files/upload-policy`
2. student 调用 `/v1/files/upload-local` 写入本地文件目录
3. student 调用 `/v1/files/confirm` 确认文件元数据
4. student 调用 `/v1/preview/upload-tags` 获取标题/标签/摘要预览
5. student 调用 `/v1/notes/confirm` 或 `/v1/ingestions` 完成入库

### 询问问题

1. 用户输入问题文本（可带文件内容）
2. frontend 调用 `/v1/solve`
3. backend 调用 AI 求解服务返回结构化结果
4. frontend 渲染 Markdown 结果，并支持“加入笔记”

### parse-job 处理

1. backend 创建 parse job
2. worker 轮询读取 pending job
3. worker 调用解析/分类逻辑
4. 成功后回写 `result_json` 与实体 `parse_status`
5. 管理员可在后台查看 parse jobs 并重试

## 4. 当前实现边界

- 搜索与图谱为轻量实现，不是完整知识图谱平台
- solve 链路当前是 AI-only
- `/uploads` 通过静态目录挂载提供访问
- review replace 支持回写标签，但审核工作流仍是最小可用实现
