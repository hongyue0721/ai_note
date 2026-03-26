# 接口规范

本文档仅描述当前代码中真实存在的后端接口。

## 1. 通用返回格式

所有接口统一返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误时 `code` 为非 0，`message` 为错误说明。

## 2. 健康与元信息

### `GET /healthz`
- 用途：健康检查

### `GET /v1/meta/app`
- 用途：获取应用名称与环境

## 3. 鉴权接口

### 用户

### `POST /v1/auth/register`
- 用途：在指定空间注册用户

### `POST /v1/auth/login`
- 用途：用户登录

### `POST /v1/auth/space-enter`
- 用途：按 `space_key` 进入空间；若空间用户不存在则自动创建 `space::{space_key}` 用户

### `GET /v1/me`
- 用途：获取当前用户资料

### 管理员

### `POST /v1/admin/auth/login`
- 用途：管理员登录

### `GET /v1/admin/me`
- 用途：获取当前管理员资料

### `PUT /v1/admin/me`
- 用途：修改当前管理员用户名和/或密码
- 请求体：
  - `current_password` 必填
  - `username` 选填
  - `new_password` 选填

## 4. 文件与预览接口

### `POST /v1/files/upload-policy`
- 用途：创建文件上传策略与 file record

### `POST /v1/files/upload-local`
- 用途：实际上传文件到本地存储目录

### `POST /v1/files/confirm`
- 用途：确认上传后的文件元数据

### `POST /v1/preview/upload-tags`
- 用途：根据文本或图片内容进行预览分类，返回标题、摘要、标签、学科等

## 5. 入库与任务接口

### `POST /v1/ingestions`
- 用途：创建 note/problem 实体，并按需创建 parse job

### `GET /v1/parse-jobs/{job_id}`
- 用途：用户查看自己的 parse job 结果

### `GET /v1/admin/parse-jobs`
- 用途：管理员查看所有 parse jobs

### `POST /v1/parse-jobs/{job_id}/retry`
- 用途：管理员重试 failed 或 pending job

## 6. 笔记与题目接口

### `GET /v1/notes`
- 用途：按用户列出笔记
- 查询参数：`subject`、`category`

### `GET /v1/notes/{note_id}`
- 用途：查看笔记详情

### `PATCH /v1/notes/{note_id}`
- 用途：更新笔记字段与标签

### `DELETE /v1/notes/{note_id}`
- 用途：删除笔记及关联 parse jobs / review tasks

### `POST /v1/notes/confirm`
- 用途：根据预览结果直接创建 note 并同步 parse 结果

### `GET /v1/problems`
- 用途：按用户列出题目

### `GET /v1/problems/{problem_id}`
- 用途：查看题目详情

### `PATCH /v1/problems/{problem_id}`
- 用途：更新题目内容

## 7. 搜索、图谱、解题接口

### `GET /v1/search`
- 用途：搜索 notes 与 problems
- 查询参数：
  - `q` 必填
  - `limit`、`offset`
  - `type`、`subject`、`category`

### `GET /v1/graph/overview`
- 用途：返回知识点权重概览、总题目数、总笔记数

### `GET /v1/graph/weak-tags`
- 用途：返回弱项标签列表

### `POST /v1/solve`
- 用途：调用 AI 求解问题
- 说明：当前仅支持 AI-only 链路

## 8. 仪表盘与管理接口

### `GET /v1/dashboard`
- 用途：用户侧当日题目数、笔记数、待审核数、待处理 parse job 数等统计

### `GET /v1/admin/monitor/overview`
- 用途：管理员查看系统状态、任务数、错误、用户笔记统计、API 请求指标

### `GET /v1/review/tasks`
- 用途：管理员查看审核任务

### `POST /v1/review/tasks/{task_id}/decision`
- 用途：管理员提交审核决策（approve / reject / replace）

### `GET /v1/admin/runtime-config/models`
- 用途：读取运行时文本模型 / 视觉模型配置

### `PUT /v1/admin/runtime-config/models`
- 用途：更新运行时模型配置
