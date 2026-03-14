# API 接口契约草案（MVP 版）

## 一、设计原则

1. 接口先满足 MVP，不追求过度完备
2. 返回结构尽量统一
3. 所有异步任务必须可查询状态
4. 前端只依赖这里定义的字段，不自行猜测

---

## 二、统一返回结构建议

### 成功

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### 失败

```json
{
  "code": 4001,
  "message": "invalid file type",
  "data": null
}
```

---

## 三、鉴权接口

## 1. 登录

`POST /v1/auth/login`

请求：

```json
{
  "username": "demo",
  "password": "123456"
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "jwt-token",
    "token_type": "bearer",
    "user": {
      "id": "u_001",
      "username": "demo"
    }
  }
}
```

## 2. 当前用户

`GET /v1/me`

---

## 四、文件接口

## 1. 申请上传策略

`POST /v1/files/upload-policy`

请求：

```json
{
  "filename": "math.png",
  "mime_type": "image/png",
  "content_type": "problem"
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "file_id": "f_001",
    "object_key": "/dev/u_001/problem/2026/03/abc.png",
    "upload_url": "https://upload.example.com",
    "upload_token": "token-or-policy",
    "max_size_bytes": 10485760
  }
}
```

## 2. 确认上传

`POST /v1/files/confirm`

请求：

```json
{
  "file_id": "f_001",
  "object_key": "/dev/u_001/problem/2026/03/abc.png",
  "size_bytes": 123456,
  "mime_type": "image/png",
  "sha256": "hash"
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "file_id": "f_001",
    "file_url": "https://cdn.example.com/abc.png",
    "upload_status": "confirmed"
  }
}
```

---

## 五、内容录入接口

## 1. 创建采集任务（推荐统一入口）

`POST /v1/ingestions`

请求：

```json
{
  "entity_type": "problem",
  "file_id": "f_001",
  "text_content": null,
  "subject": "math",
  "source_type": "upload",
  "auto_parse": true
}
```

说明：

- `entity_type`: `problem` / `note`
- `file_id` 和 `text_content` 至少提供一个

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "entity_type": "problem",
    "entity_id": "p_001",
    "parse_job_id": "j_001",
    "parse_status": "pending"
  }
}
```

---

## 六、解析任务接口

## 1. 查询解析任务

`GET /v1/parse-jobs/{job_id}`

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "j_001",
    "status": "success",
    "entity_type": "problem",
    "entity_id": "p_001",
    "result": {
      "subject": "math",
      "knowledge_candidates": [
        {
          "name": "一元二次方程",
          "confidence": 0.93
        }
      ]
    }
  }
}
```

## 2. 重试解析任务

`POST /v1/parse-jobs/{job_id}/retry`

---

## 七、错题接口

## 1. 错题列表

`GET /v1/problems`

支持查询参数：

- `q`
- `subject`
- `tag_id`
- `parse_status`
- `page`
- `page_size`

## 2. 错题详情

`GET /v1/problems/{problem_id}`

返回至少包含：

- 基础信息
- 标签
- 相关笔记
- 解析状态
- 本地题库命中信息
- AI 参考解析（如果有）

## 3. 更新错题

`PATCH /v1/problems/{problem_id}`

---

## 八、笔记接口

## 1. 笔记列表

`GET /v1/notes`

## 2. 笔记详情

`GET /v1/notes/{note_id}`

返回至少包含：

- 基础信息
- 标签
- 相关错题
- 解析状态

## 3. 更新笔记

`PATCH /v1/notes/{note_id}`

---

## 九、审核接口

## 1. 审核任务列表

`GET /v1/review/tasks`

支持参数：

- `task_type`
- `status`
- `entity_type`

## 2. 提交审核结果

`POST /v1/review/tasks/{task_id}/decision`

请求：

```json
{
  "action": "approve",
  "edited_tags": [
    {
      "tag_id": "t_001"
    }
  ]
}
```

动作建议：

- `approve`
- `reject`
- `replace`

---

## 十、搜索接口

`GET /v1/search`

参数：

- `q`
- `subject`
- `entity_type`
- `tag_id`
- `page`
- `page_size`

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [
      {
        "entity_type": "problem",
        "entity_id": "p_001",
        "title": "一元二次方程求解",
        "subject": "math",
        "matched_tags": ["一元二次方程"]
      }
    ],
    "total": 1
  }
}
```

---

## 十一、图谱接口

## 1. 图谱总览

`GET /v1/graph/overview`

返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "nodes": [
      {
        "id": "t_001",
        "name": "一元二次方程",
        "mastery_score": 45,
        "wrong_count": 5,
        "note_count": 2,
        "problem_count": 6
      }
    ],
    "edges": [
      {
        "source": "t_001",
        "target": "t_002",
        "weight": 3,
        "relation_type": "cooccur"
      }
    ]
  }
}
```

## 2. 薄弱知识点

`GET /v1/graph/weak-tags`

---

## 十二、本地题库命中与 AI 解题接口

## 1. 触发解题

`POST /v1/solve`

请求：

```json
{
  "problem_id": "p_001"
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "search_status": "local_miss",
    "solution_source": "llm",
    "final_answer": "x=2 或 x=-3",
    "solution_steps": [
      "整理方程",
      "使用求根公式"
    ],
    "knowledge_points": [
      "一元二次方程",
      "求根公式"
    ],
    "confidence": 0.78,
    "warning_text": "以下为 AI 参考解析，请以教材/老师标准答案为准。"
  }
}
```

## 2. 查询 AI 解题记录

`GET /v1/solve/history`

---

## 十三、Dashboard 接口

`GET /v1/dashboard`

建议返回：

- 今日新增错题数
- 今日新增笔记数
- 待审核数
- 弱点 Top 5
- 最近上传记录

---

## 十四、状态码建议

业务错误码可自定义，但建议至少区分：

- 4001 参数错误
- 4002 文件类型不支持
- 4003 文件过大
- 4010 未登录
- 4030 无权限
- 4040 资源不存在
- 4090 状态冲突
- 5000 内部错误
- 5001 AI 调用失败

---

## 十五、最终要求

> 这份接口契约是前端、服务端、存储段代理协作的共同边界。  
> 如果字段、状态、路径需要修改，必须先修改这份文档，再改代码。
