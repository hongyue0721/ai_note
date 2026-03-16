import { expect, test } from '@playwright/test'

test('student can log in and enter workspace', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  await page.goto('/')

  await expect(page.getByRole('heading', { name: '输入任意字符串，进入对应学习空间。' })).toBeVisible()
  await page.getByRole('textbox', { name: '空间字符串' }).fill(`pw-auth-${Date.now()}`)
  await page.getByRole('button', { name: '进入学习工作台' }).click()

  await expect(page.getByRole('heading', { name: '智能笔记工作台' })).toBeVisible()
  await expect(page.getByRole('button', { name: '上传笔记' })).toBeVisible()
  await expect(page.getByRole('button', { name: '询问问题' })).toBeVisible()
  await expect(page.getByRole('button', { name: '笔记管理' })).toBeVisible()
})
