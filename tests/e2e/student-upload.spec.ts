import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'

const currentFilePath = fileURLToPath(import.meta.url)
const currentDir = path.dirname(currentFilePath)

test('student can upload a file and see parse job status', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  const uploadFixture = path.resolve(currentDir, '../fixtures/upload-note.txt')

  await page.goto('/')

  await page.getByRole('textbox', { name: '用户名' }).fill('demo_user')
  await page.getByRole('textbox', { name: '密码' }).fill('user123456')
  await page.getByRole('button', { name: '登录并拉取资料' }).click()

  await expect(page.getByText('demo@example.com · active')).toBeVisible()

  await expect(page.getByRole('heading', { name: '2. 上传并创建解析任务' })).toBeVisible()
  const uploadSection = page.locator('section').filter({ hasText: '2. 上传并创建解析任务' }).first()

  await uploadSection.locator('input[type="file"]').setInputFiles(uploadFixture)
  await expect(uploadSection.getByRole('textbox', { name: '文件名' })).toHaveValue('upload-note.txt')
  await expect(uploadSection.getByRole('textbox', { name: 'Mime Type' })).toHaveValue('text/plain')

  await uploadSection.getByRole('textbox', { name: '文件名' }).fill('upload-note.txt')
  await uploadSection.getByRole('textbox', { name: 'Mime Type' }).fill('text/plain')
  await uploadSection.getByRole('combobox', { name: '文件种类' }).selectOption('document')
  await uploadSection.getByRole('combobox', { name: '内容类型' }).selectOption('document')
  await uploadSection.getByRole('textbox', { name: '科目' }).fill('biology')
  await uploadSection.getByRole('textbox', { name: '文本内容' }).fill('这是用于浏览器级上传验证的文档内容。')

  await uploadSection.getByRole('button', { name: '创建上传记录并发起解析' }).click()

  await expect(uploadSection.locator('.error-text')).toHaveCount(0)
  await expect(uploadSection.getByText('任务已创建，正在刷新解析状态…')).toBeVisible()

  await expect(page.getByRole('heading', { name: '3. 最近任务' })).toBeVisible()
  const latestJobSection = page.locator('section').filter({ hasText: '3. 最近任务' }).first()
  await expect(latestJobSection.locator('.job-block')).toBeVisible({ timeout: 15_000 })
  await expect(latestJobSection.getByText('任务 ID')).toBeVisible()
  await expect(latestJobSection.getByText('尝试次数')).toBeVisible()
  await expect(page.locator('.stat-grid').first().getByText('已生成')).toBeVisible()
})
