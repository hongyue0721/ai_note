# AI 分类 Agent 计划

## 1. 目标

把当前 worker 中的 mock 分类结果替换为真实 AI 分类结果。

## 2. 本阶段最小交付

1. 分类 prompt 文件
2. 分类输出 schema
3. classifier service
4. worker / parse_jobs 对接 classifier
5. 低置信度自动送审

## 3. 输出要求

至少输出：

- `entity_type`
- `content_category`
- `subject`
- `title`
- `normalized_text`
- `knowledge_candidates`
- `confidence`
- `needs_review`
- `review_reason`

## 4. 下一步

完成本阶段后，直接进入 solve service。
