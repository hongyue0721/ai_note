# Solve 服务计划

## 1. 目标

实现“本地题库未命中时，AI 给参考解析”的真实服务与接口。

## 2. 本阶段最小交付

1. solve prompt
2. solver service
3. `/v1/solve` 接口
4. 风险提示与结构化输出

## 3. 输出要求

至少包含：

- `subject`
- `question_type`
- `final_answer`
- `solution_steps`
- `knowledge_points`
- `confidence`
- `warnings`

## 4. 下一步

完成后继续：

- `/v1/search`
- 图谱接口
