# 真实 AI 联调与 Solve 兼容修复记录

## 1. 本次目标

在真实 OpenAI-compatible 网关可达的前提下，继续打通真实 AI 联调，优先解决 `/v1/solve` 的模型输出与后端 schema 不兼容问题。

## 2. 当前背景

已确认新的真实配置可达：

- `OPENAI_BASE_URL=http://159.223.81.110:8317/v1`
- `OPENAI_MODEL_CLASSIFY=glm-4.6v`
- `OPENAI_MODEL_SOLVE=LongCat-Flash-Chat`

且远端验证已通过：

- `/v1/models` → 200
- `/v1/chat/completions` → 200

说明当前问题已从“网络不通”转为“真实模型输出与业务 schema 不兼容”。

## 3. 已定位问题

`LongCat-Flash-Chat` 在 solve 场景下返回的 JSON 与当前 `SolveResultData` 不完全一致，已出现：

- `question_type` 缺失
- `final_answer` 缺失
- `solution_steps` 缺失
- `warnings` 返回 string 而不是 list

## 4. 本次修复

本次做的是**最小兼容修复**：

1. 强化 `solve_prompt.txt`，明确要求固定字段与类型；
2. 在 `solver.py` 新增兼容归一化层，把常见变体字段映射为：
   - `question_type`
   - `final_answer`
   - `solution_steps`
   - `knowledge_points`
   - `warnings`
3. 对 `warnings` / `solution_steps` / `knowledge_points` 做 string → list 兼容；
4. 对 `confidence` 做安全归一化。

## 5. 当前仍未完成

这部分旧结论已经过期。

最新状态：

1. `classifier` 真实结果已成功返回；
2. `/v1/solve` 路由级联调已成功；
3. compose 全链路实跑已完成；
4. 长期运行方案首轮固定化（`systemd + docker compose`）已完成；
5. 当前 AI 侧真正仍需继续补的是“失败路径回归验证证据”和更系统的回归文档。

## 6. 失败路径补充验证（新增）

本轮继续完成了真实 AI 失败路径回归验证，已得到明确可读错误：

1. **缺少 API Key**

```text
code=5001
message=OPENAI_API_KEY is not configured
```

2. **错误 base URL / 超时**

```text
code=5002
message=openai request failed: Request timed out.
```

3. **错误模型名**

```text
code=5002
message=openai request failed: Error code: 502 - {'error': {'message': 'unknown provider for model definitely-not-a-real-model', ...}}
```

4. **classifier 返回不兼容 schema**

已在 `classifier.py` 中补充显式捕获 `ValidationError`，当前返回：

```text
code=5005
message=classifier returned incompatible schema: ...
```

说明：

- `solver.py` 因已有归一化兼容层，简单字段缺失不再适合作为失败样例；
- 但 `classifier.py` 的严格 schema 失败路径现在已经有明确错误码与信息，不会再退化成模糊 500。
