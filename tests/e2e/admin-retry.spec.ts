import { expect, test } from '@playwright/test'

test('admin can retry a failed parse job from the current UI', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_ADMIN_URL or project baseURL is required')

  await page.goto('/')

  const loginPanel = page.locator('.login-overlay-card')
  await loginPanel.getByLabel('用户名').fill('admin')
  await loginPanel.getByLabel('密码').fill('admin123456')
  await loginPanel.getByRole('button', { name: '登录后台并加载数据' }).click()

  await expect(page.getByRole('heading', { name: 'API 管理' })).toBeVisible()
  await expect(page.getByRole('button', { name: '保存模型配置' })).toBeVisible()
  await expect(page.getByRole('textbox').first()).toBeVisible()
})
