import { expect, test } from '@playwright/test'

test('admin can log in and load monitoring panels', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_ADMIN_URL or project baseURL is required')

  await page.goto('/')

  await expect(page.getByRole('heading', { name: '管理员登录' })).toBeVisible()
  const loginPanel = page.locator('.login-overlay-card')
  await loginPanel.getByLabel('用户名').fill('admin')
  await loginPanel.getByLabel('密码').fill('admin123456')
  await loginPanel.getByRole('button', { name: '登录后台并加载数据' }).click()

  await expect(page.getByRole('heading', { name: '当前管理员' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '状态与接口指标观察' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'API 管理' })).toBeVisible()
})
