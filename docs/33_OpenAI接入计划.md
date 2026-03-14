# OpenAI 接入计划

## 1. 目标

让当前后端具备统一、可复用、可配置的 OpenAI 调用能力，为：

- AI 分类 agent
- AI solve 接口

提供共同底座。

## 2. 本阶段最小交付

1. 增加 OpenAI 配置项；
2. 增加统一 `llm_client`；
3. 支持 chat completion 文本调用；
4. 支持 JSON 输出模式；
5. 对超时、空响应、异常响应做统一处理。

## 3. 设计原则

1. 不把 OpenAI SDK 依赖散落在业务逻辑中；
2. 所有调用先经过统一 client；
3. 所有业务 service 只依赖统一 client；
4. 没有配置 key 时，错误必须清晰；
5. 后续允许替换 `base_url` 兼容代理网关。

## 4. 产出文件

- `apps/backend/app/core/config.py`
- `apps/backend/.env.example`
- `apps/backend/requirements.txt`
- `apps/backend/app/services/llm_client.py`

## 5. 下一步

完成 OpenAI 配置与 client 后，直接进入：

- 分类 prompt
- classifier service
- worker 真接入
