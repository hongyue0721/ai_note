# 浏览器级 E2E 最小落地计划

## 1. 目标

在不重构前端架构、不引入域名/反代工作的前提下，为 `note` 项目补齐首批真实浏览器级 E2E，覆盖当前最关键且最稳定的 UI 主链路：

1. student 登录成功并进入已登录状态；
2. admin 登录成功并进入已登录状态；
3. 测试可直接对接已运行的本地/远端环境，不强绑定 dev server 启动。

## 2. 范围

本轮只做最小可运行落地：

1. 在仓库根新增 Playwright 测试基础设施；
2. 使用环境变量配置 student/admin/base API 地址；
3. 增加两个 spec：
   - `student-auth.spec.ts`
   - `admin-auth.spec.ts`
4. 增加 README/文档说明运行方式与当前覆盖范围。

## 3. 明确不做

本轮不做：

1. 上传/解析任务浏览器级 E2E；
2. 图谱、搜索、solve 的浏览器级 E2E；
3. 前端 router 化或大规模分层重构；
4. CI/CD 接入；
5. 域名、反向代理、公网入口治理。

## 4. 实施步骤

1. 在仓库根新增 `package.json`，安装 `@playwright/test`；
2. 新增 `playwright.config.ts`，从环境变量读取：
   - `PLAYWRIGHT_STUDENT_URL`
   - `PLAYWRIGHT_ADMIN_URL`
3. 新增 `tests/e2e/student-auth.spec.ts`：
   - 打开 student 页面；
   - 填写默认 demo 用户；
   - 点击登录；
   - 断言页面出现登录后的用户信息或成功状态；
4. 新增 `tests/e2e/admin-auth.spec.ts`：
   - 打开 admin 页面；
   - 填写默认 admin 用户；
   - 点击登录；
   - 断言页面出现管理员信息或后台监控内容；
5. 在 docs 中更新“浏览器级 E2E 已有最小落地，但覆盖仍有限”；
6. 运行 Playwright、前端构建，并记录验证结果。

## 5. 验证标准

以下条件同时满足才算完成：

1. Playwright 测试可执行；
2. student/admin 登录 happy path 测试通过；
3. 受影响文件 diagnostics 干净；
4. 文档说明已同步更新。

## 6. 风险与约束

1. 当前前端没有稳定的测试选择器，因此优先使用页面上稳定可见的文本与表单顺序；
2. 当前远端环境依赖真实后端与真实账号，因此测试默认使用现有 demo/admin 凭据；
3. 若页面文案后续频繁变化，需要补充更稳定的 `data-testid`，但本轮先不额外重构页面。
