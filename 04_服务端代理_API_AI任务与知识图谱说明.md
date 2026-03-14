# 服务端代理：API、AI 任务链路与知识图谱工作说明

## 你的角色

你负责项目的大脑与中枢。  
你需要把：

- 用户
- 文件
- 笔记
- 错题
- 标签
- 搜索
- 图谱聚合
- AI 解析
- LLM fallback 解题

这些能力整合成一个清晰、可测试、可交付的服务端系统。

---

## 一、你必须先看的文档

1. `01_项目总体要求_路线图_技术栈_时间计划.md`
2. `11_数据库核心表设计草案.md`
3. `12_API接口契约草案.md`
4. `06_本地题库未命中时_LLM自主解题规划.md`

---

## 二、你的边界

### 你负责

- 鉴权与用户基础逻辑
- 文件记录与业务条目绑定
- 笔记与错题 CRUD
- parse_job 任务状态机
- Gemini 结构化输出调用
- 标签规范化映射
- 标签审核队列
- 搜索接口
- 图谱聚合接口
- AI 解题 fallback 接口
- 统计接口

### 你不负责

- 对象存储底层实现细节（由存储段代理负责）
- 前端页面开发
- 最终部署编排（由运维代理负责）
- 手工验收（由 QA 代理主导）

---

## 三、首月必须实现的能力

## 1. 用户与鉴权

最小要求：

- 用户注册/登录（二选一也可，比赛 demo 可先固定管理员用户）
- JWT 或等效会话机制
- `GET /v1/me`

## 2. 内容录入

支持两类内容：

- 笔记 `note`
- 错题 `problem`

来源支持：

- 文本录入
- 图片上传后解析

## 3. AI 解析任务

必须支持：

- 新建解析任务
- 任务状态查询
- 任务失败重试
- 解析结果持久化
- 人工审核入口

## 4. 标签与知识图

必须支持：

- AI 给出候选标签
- 映射到规范标签 `knowledge_tags`
- 建立 note/problem 与 tag 的多对多关系
- 统计用户在各标签上的薄弱程度
- 输出图谱所需节点和边

## 5. 搜索

首月支持：

- 关键词搜索
- 标签搜索
- 按科目过滤
- 笔记/错题混合搜索

## 6. 本地题库未命中时 AI 解题

必须支持：

- 先搜本地题库
- 若未命中，再请求 LLM
- 返回“参考解析”
- 标明置信度和 AI 生成标记
- 保存结果，便于后续复核

---

## 四、服务端推荐结构

```text
apps/backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
      auth/
      files/
      notes/
      problems/
      tags/
      parse_jobs/
      search/
      graph/
      solve/
      llm/
    workers/
  tests/
```

---

## 五、最重要的 3 个设计原则

## 1. AI 输出不是最终事实

AI 只能输出：

- OCR 文本
- 题目结构
- 候选知识点
- 置信度
- 参考解析

最终进入知识图的数据必须经过：

- 服务端规范化
- 状态控制
- 必要时人工审核

## 2. 图谱不是数据库产品，是接口产物

首月不要被“知识图谱”这个词吓住。  
你只需要：

- 维护标签节点
- 维护节点关系
- 输出前端可画图的数据结构

不需要首月上 Neo4j。

## 3. 所有异步都必须可追踪

任何 AI 调用都必须有任务记录：

- request_payload_json
- result_json
- status
- attempts
- error_message

否则后面无法排障。

---

## 六、AI 打标签核心逻辑（建议实现）

## 1. 输入

输入可能来自：

- 图片 URL
- OCR 文本
- 手工输入文本

## 2. 输出目标

强制模型返回结构化 JSON，建议字段：

```json
{
  "content_type": "problem",
  "subject": "math",
  "title": "一元二次方程求根",
  "raw_text": "题目原文",
  "normalized_text": "清洗后的文本",
  "knowledge_candidates": [
    {
      "name": "一元二次方程",
      "confidence": 0.93
    },
    {
      "name": "求根公式",
      "confidence": 0.86
    }
  ],
  "difficulty": "medium",
  "question_type": "calculation"
}
```

## 3. 规范化流程

建议流程：

1. 先让模型输出候选标签
2. 再对照 `knowledge_tags` 进行名称映射
3. 若高相似命中，则映射到已有规范标签
4. 若未命中，则进入“待审核新标签”
5. 若候选标签置信度低，则进入审核队列

---

## 七、AI 打标签伪代码

```python
def process_parse_job(job_id: str):
    job = load_job(job_id)
    mark_running(job)

    content = load_content(job)
    llm_result = gemini_extract_structured_json(content)

    normalized = normalize_llm_result(llm_result)

    save_raw_parse_result(job, llm_result, normalized)

    tag_links = []
    for item in normalized.knowledge_candidates:
        tag = find_best_canonical_tag(
            subject=normalized.subject,
            candidate_name=item.name
        )

        if tag and item.confidence >= 0.80:
            link = create_tag_link(
                entity_type=job.entity_type,
                entity_id=job.entity_id,
                tag_id=tag.id,
                confidence=item.confidence,
                source="llm",
                status="confirmed"
            )
        else:
            link = create_review_task_for_tag_candidate(
                entity_type=job.entity_type,
                entity_id=job.entity_id,
                candidate_name=item.name,
                confidence=item.confidence
            )

        tag_links.append(link)

    update_entity_parse_status(job.entity_id, "success")
    mark_success(job)
```

---

## 八、图谱聚合最小实现

你不需要做复杂图算法。  
首月只做以下 3 类接口即可：

### 1. 节点接口

返回：

- tag_id
- name
- mastery_score
- wrong_count
- note_count
- problem_count

### 2. 边接口

边来源只需要 2 类：

- 标签共现（同一笔记/错题里一起出现）
- 先修关系（人工维护，可先为空）

### 3. 弱点图接口

返回用户薄弱标签 Top N：

- 最近错误数
- 最近命中次数
- 建议复习优先级

---

## 九、搜索最小实现

首月建议：

1. PostgreSQL 全文搜索
2. 标签过滤
3. 科目过滤
4. 时间排序

不要求首月必须做：

- 复杂语义重排
- 多轮检索
- 多模态向量召回

如果进度超前，再做向量增强。

---

## 十、本地题库未命中时的服务端职责

当题库未命中时，服务端要做 5 件事：

1. 记录这次未命中
2. 调用 LLM 输出参考解析
3. 做二次自检或 verifier 流程
4. 返回给前端“AI 参考解析 + 置信度 + 提示”
5. 记录到 `ai_solution_records`

必须显示提示：

> 以下内容为 AI 生成的参考解析，请以教材/老师标准答案为准。

---

## 十一、你的验收标准

### 验收 1：上传后可产生解析任务

- 创建错题条目
- 触发 parse_job
- 状态可查

### 验收 2：AI 解析结果可落库

- 结果中有 raw_text
- 有 subject
- 有候选标签
- 有 result_json

### 验收 3：标签可建立关联

- 某条错题绑定至少 1 个标签
- 某条笔记绑定至少 1 个标签
- 能查到共享标签下的关联内容

### 验收 4：图谱接口可返回节点与边

- 前端能拿接口结果直接画图
- 即使图为空，也能返回合法 JSON

### 验收 5：本地题库未命中能触发 AI 参考解析

- 检索无结果
- 走 fallback
- 返回解析和说明文案
- 数据库存档

---

## 十二、最重要的一句要求

> 你写的不是“一个大而全的后端”，而是一个能在 30 天内稳定支撑上传、解析、关联、搜索、图谱和 AI 参考解析的可验证中枢。
