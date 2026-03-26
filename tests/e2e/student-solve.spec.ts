import { expect, test } from '@playwright/test'

test('student can ask a question and see structured answer', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  await page.goto('/')
  await page.getByRole('textbox', { name: '空间字符串' }).fill(`pw-solve-${Date.now()}`)
  await page.getByRole('button', { name: '进入学习工作台' }).click()

  await page.getByRole('button', { name: '询问问题' }).click()
  await expect(page.locator('main.workspace-main').getByRole('heading', { name: '询问问题' })).toBeVisible()
  const askSection = page.locator('main.workspace-main section.workspace-card').first()
  await askSection.getByRole('textbox', { name: '问题文本' }).fill('解方程：x^2 - 5x + 6 = 0')
  await askSection.getByRole('button', { name: '提交问题并生成答案' }).click()

  await expect(askSection.getByText('最终答案')).toBeVisible({ timeout: 30_000 })
  await expect(askSection.getByRole('button', { name: '加入笔记' })).toBeVisible()
})
