# 阶段 7：worker 与任务执行计划

## 1. 目标

把当前只会“创建 parse_job”的系统，推进到“worker 真正执行 parse_job”的状态。

## 2. 本阶段最小交付

1. worker 可轮询 `parse_jobs`；
2. worker 可把 `pending` 任务推进到 `running`；
3. worker 可生成模拟解析结果；
4. worker 可把任务推进到 `success`；
5. 当置信度偏低时，可自动创建 `review_task`。

## 3. 当前策略

比赛级阶段先做**可运行的模拟解析执行器**，暂不强行接入真实 Gemini：

- 若有文本，则直接基于文本生成结构化占位结果；
- 若只有文件，则生成占位解析结果；
- 生成知识点候选、置信度与结果 JSON；
- 低置信度自动入审核队列。

## 4. 验收标准

1. 创建 ingestion 后 parse job 不再永远停留在 pending；
2. worker 运行后能把任务推进到 success；
3. 可看到 `result_json`；
4. 必要时能创建 review task。
