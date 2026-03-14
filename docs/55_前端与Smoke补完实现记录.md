# 前端与 Smoke 补完实现记录

## 1. 本次目标

基于现有比赛级前端与 smoke 基础，补齐一批最小但关键的缺口：

1. 学生端 solve 展示；
2. 搜索结果与详情区域联动；
3. 后台 parse jobs 分组 / 筛选 / 失败任务重试入口；
4. smoke 脚本补充 healthz、上传链路与 `/uploads` 静态访问验证。

## 2. 本次完成内容

### 学生端

已完成：

1. 新增 `/v1/solve` 调用区；
2. 新增 AI 参考解析结果展示区；
3. 搜索结果支持点击后联动 problem / note 详情区。

### 后台端

已完成：

1. parse jobs 状态筛选；
2. pending/running、failed、success 分组展示；
3. failed 任务重试入口，调用 `/v1/parse-jobs/{job_id}/retry`。

### Smoke

已补充：

1. `GET /healthz`
2. `POST /v1/files/upload-policy`
3. `POST /v1/files/confirm`
4. `/uploads/...` 静态访问验证

## 3. 当前效果

这一轮补完后，前端已更接近计划中的“比赛级可演示成品”：

- 学生端从上传 -> 解析 -> 搜索 -> 图谱 -> solve 的主路径更完整；
- 后台端对 parse jobs 的观察与失败重试更接近真实管理页；
- smoke 已覆盖文件存储主链路，不再只停留在读接口层。

## 4. 尚未做满的地方

当前仍未完全做满：

1. 学生端多页面路由体系；
2. 更丰富的上传进度 / 拖拽 / 预览；
3. 后台更复杂的筛选组合；
4. 真实 OpenAI 场景下的 solve/classifier 端到端 smoke。
