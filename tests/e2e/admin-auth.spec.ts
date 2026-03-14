import { expect, test } from '@playwright/test'

test('admin can log in and load monitoring panels', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_ADMIN_URL or project baseURL is required')

  await page.goto('/')

  await expect(page.getByRole('heading', { name: '管理员登录' })).toBeVisible()
  await expect(page.getByText('独立管理员账号体系')).toBeVisible()

  const loginPanel = page.locator('.login-panel')
  await loginPanel.getByLabel('用户名').fill('admin')
  await loginPanel.getByLabel('密码').fill('admin123456')
  await loginPanel.getByRole('button', { name: '登录后台并加载数据' }).click()

  await expect(loginPanel.locator('.profile-card')).toBeVisible()
  await expect(loginPanel.locator('.profile-card')).toContainText('admin')
  await expect(loginPanel.locator('.error-text')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: '监控总览' })).toBeVisible()
  const monitorPanel = page.locator('.monitor-panel')
  await expect(monitorPanel.getByText('待执行任务', { exact: true })).toBeVisible()
  await expect(monitorPanel.getByText('待审核任务', { exact: true })).toBeVisible()
})
