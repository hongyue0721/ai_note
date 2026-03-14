# Solve 服务实现记录

## 1. 本次目标

实现真实 AI 解题服务与 `/v1/solve`。

## 2. 当前状态

当前已完成：

1. 增加 solve prompt；
2. 增加 solver service；
3. 增加 solve schema；
4. 增加 `/v1/solve` 路由。

## 3. 本次新增文件

- `apps/backend/app/prompts/solve_prompt.txt`
- `apps/backend/app/schemas/solve.py`
- `apps/backend/app/services/solver.py`
- `apps/backend/app/api/routes/solve.py`

## 4. 本次修改文件

- `apps/backend/app/api/router.py`

## 5. 当前结果

当前 `/v1/solve` 已挂载到后端路由中，并通过远端导入级校验。
