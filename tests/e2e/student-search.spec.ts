import { expect, test } from '@playwright/test'

test('student can search and see result list', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  await page.goto('/')

  await page.getByRole('textbox', { name: '用户名' }).fill('demo_user')
  await page.getByRole('textbox', { name: '密码' }).fill('user123456')
  await page.getByRole('button', { name: '登录并拉取资料' }).click()

  await expect(page.getByText('demo@example.com · active')).toBeVisible()

  await expect(page.getByRole('heading', { name: '5. 搜索' })).toBeVisible()
  const searchSection = page.locator('section').filter({ hasText: '5. 搜索' }).first()

  await searchSection.getByRole('textbox', { name: '关键词' }).fill('方程')
  await searchSection.getByRole('button', { name: '执行搜索' }).click()

  const searchResults = searchSection.locator('.search-result-btn')
  await expect(searchResults.first()).toBeVisible({ timeout: 10_000 })
  await expect(searchResults).not.toHaveCount(0)
  await expect(searchResults.first()).toContainText('problem')
  await expect(searchResults.first()).toContainText('这是一道比较难的方程题')
})
