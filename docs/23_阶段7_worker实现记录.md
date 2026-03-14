# 阶段 7：worker 实现记录

## 1. 本次目标

把 parse job 从“只会创建”推进到“worker 真正处理”。

## 2. 本次已完成

### 2.1 新增 parse job 服务层

已新增：

- 读取下一个 pending 任务
- 处理 parse job
- 生成 mock 解析结果
- 低置信度时自动创建审核任务

### 2.2 worker 主循环升级

原先 worker 只是打印占位信息。

现在已升级为：

1. 连接数据库；
2. 轮询 pending parse jobs；
3. 推进任务执行；
4. 输出处理结果。

## 3. 当前实现策略

当前仍是比赛级阶段，因此先采用：

- mock 解析逻辑；
- mock 标签候选；
- 低置信度自动入审核队列。

这能先把：

- 学生端上传
- parse job 处理
- 后台审核

三者串起来。

## 4. 下一步

下一步用远端创建新 parse job，执行 worker，并验证：

1. job 状态变化；
2. result_json 写入；
3. review task 自动生成。
