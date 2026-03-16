import { expect, test } from '@playwright/test'

test('admin can replace review tags from the current UI', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_ADMIN_URL or project baseURL is required')

  await page.goto('/')

  const loginPanel = page.locator('.login-overlay-card')
  await loginPanel.getByLabel('用户名').fill('admin')
  await loginPanel.getByLabel('密码').fill('admin123456')
  await loginPanel.getByRole('button', { name: '登录后台并加载数据' }).click()

  await expect(page.getByRole('heading', { name: '注册用户名与笔记数量' })).toBeVisible()
  await expect(page.locator('.user-stat-item').first()).toBeVisible({ timeout: 15_000 })
})
