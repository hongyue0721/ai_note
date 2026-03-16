import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'

const currentFilePath = fileURLToPath(import.meta.url)
const currentDir = path.dirname(currentFilePath)

test('student can upload a file, review tags, and confirm note creation', async ({ page, baseURL }) => {
  test.skip(!baseURL, 'PLAYWRIGHT_STUDENT_URL or project baseURL is required')

  const uploadFixture = path.resolve(currentDir, '../fixtures/upload-note.txt')

  await page.goto('/')
  await page.getByRole('textbox', { name: '空间字符串' }).fill(`pw-upload-${Date.now()}`)
  await page.getByRole('button', { name: '进入学习工作台' }).click()

  await expect(page.getByRole('heading', { name: '上传笔记' })).toBeVisible()
  const uploadSection = page.locator('main.workspace-main section.workspace-card').first()
  await uploadSection.locator('input[type="file"]').setInputFiles(uploadFixture)
  await uploadSection.getByRole('textbox', { name: '文件名 / 标题' }).fill('upload-note.txt')
  await uploadSection.getByRole('textbox', { name: '文本内容' }).fill('这是用于浏览器级上传验证的文档内容。')
  await uploadSection.getByRole('button', { name: '开始识别并展示分类结果' }).click()

  await expect(page.locator('main.workspace-main').getByRole('heading', { name: '分类结果确认页' })).toBeVisible({ timeout: 90_000 })
  await page.locator('main.workspace-main').getByRole('button', { name: '确认保存到笔记' }).click()

  await expect(page.locator('main.workspace-main').getByRole('heading', { name: '笔记管理' })).toBeVisible()
})
