import { expect, test } from '@playwright/test'

test('student can log in and see authenticated state', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  await page.goto('/')

  await expect(page.getByRole('heading', { name: '1. 登录学生端' })).toBeVisible()
  await expect(page.getByText('真实对接 `/v1/auth/login` 与 `/v1/me`')).toBeVisible()

  await page.getByRole('textbox', { name: '用户名' }).fill('demo_user')
  await page.getByRole('textbox', { name: '密码' }).fill('user123456')
  await page.getByRole('button', { name: '登录并拉取资料' }).click()

  await expect(page.getByText('demo@example.com · active')).toBeVisible()
  await expect(page.locator('#student-login .error-text')).toHaveCount(0)
  await expect(page.locator('.stat-grid').first().getByText('demo_user')).toBeVisible()
  await expect(page.getByRole('heading', { name: '4. 知识点可视化' })).toBeVisible()
})
