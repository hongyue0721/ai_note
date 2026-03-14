import { expect, test } from '@playwright/test'

test('student can request AI solve and see structured result', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  await page.goto('/')

  await page.getByRole('textbox', { name: '用户名' }).fill('demo_user')
  await page.getByRole('textbox', { name: '密码' }).fill('user123456')
  await page.getByRole('button', { name: '登录并拉取资料' }).click()

  await expect(page.getByText('demo@example.com · active')).toBeVisible()

  await expect(page.getByRole('heading', { name: '6. AI 参考解析' })).toBeVisible()
  const solveSection = page.locator('section').filter({ hasText: '6. AI 参考解析' }).first()

  await solveSection.getByRole('textbox', { name: '题目文本' }).fill('解方程：x^2 - 5x + 6 = 0')
  await solveSection.getByRole('textbox', { name: '科目' }).fill('math')
  await solveSection.getByRole('button', { name: '生成 AI 参考解析' }).click()

  await expect(solveSection.getByText('最终答案：')).toBeVisible({ timeout: 15_000 })
  await expect(solveSection.getByText('模型：')).toBeVisible()
  await expect(solveSection.getByText('解题步骤')).toBeVisible()
  await expect(solveSection.getByText('知识点')).toBeVisible()
})
