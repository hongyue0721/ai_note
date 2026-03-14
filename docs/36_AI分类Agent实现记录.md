# AI 分类 Agent 实现记录

## 1. 本次目标

让 parse job 的分类结果由真实 AI 输出，而不是 mock 生成。

## 2. 当前状态

当前已完成：

1. 增加分类 prompt；
2. 增加分类 schema；
3. 增加 classifier service；
4. 改造 parse_jobs 对接 classifier。

## 3. 本次新增文件

- `apps/backend/app/prompts/classify_prompt.txt`
- `apps/backend/app/schemas/classifier.py`
- `apps/backend/app/services/classifier.py`

## 4. 本次修改文件

- `apps/backend/app/services/parse_jobs.py`

## 5. 当前行为

当前 worker 行为变为：

1. 若存在 `OPENAI_API_KEY`，优先走真实 AI 分类；
2. 若不存在 `OPENAI_API_KEY`，回退到 mock 分类；
3. 低置信度或 `needs_review=true` 自动创建 review task。

## 6. 下一步

下一步进入：

- solve prompt
- solver service
- `/v1/solve`

## 7. 当前结果

当前分类 agent 已完成代码接入，并在无 OpenAI 配置时保持向下兼容 mock 模式。
