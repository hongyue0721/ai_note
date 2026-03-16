import { expect, test } from '@playwright/test'

test('student can search and see result list', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  await page.goto('/')
  await page.getByRole('textbox', { name: '空间字符串' }).fill(`pw-search-${Date.now()}`)
  await page.getByRole('button', { name: '进入学习工作台' }).click()

  await page.getByRole('button', { name: '笔记管理' }).click()
  await page.getByRole('button', { name: '搜索笔记' }).click()

  const searchSection = page.locator('.notes-search-panel')
  await searchSection.getByRole('textbox', { name: '关键词' }).fill('方程')

  const searchResults = searchSection.locator('.search-result-btn')
  await expect(searchResults.first()).toBeVisible({ timeout: 15_000 })
  await expect(searchResults).not.toHaveCount(0)
})
