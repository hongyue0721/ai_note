import { defineConfig } from '@playwright/test'

const studentBaseURL = process.env.PLAYWRIGHT_STUDENT_URL || 'http://146.190.84.189:3000'
const adminBaseURL = process.env.PLAYWRIGHT_ADMIN_URL || 'http://146.190.84.189:3001'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list']],
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'student',
      testMatch: /student-(auth|upload|search|solve)\.spec\.ts/,
      use: {
        baseURL: studentBaseURL,
      },
    },
    {
      name: 'admin',
      testMatch: /admin-(auth|review|retry)\.spec\.ts/,
      use: {
        baseURL: adminBaseURL,
      },
    },
  ],
})
