<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { apiBase } from './config'

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type MonitorOverview = {
  service_status: string
  parse_job_total: number
  parse_job_pending: number
  parse_job_failed: number
  latest_error_messages: string[]
  api_request_count: number
  api_avg_response_ms: number
  total_user_count: number
  total_note_count: number
  user_note_stats: Array<{ username: string; space_key: string; note_count: number }>
}

type RuntimeConfigItem = {
  scope: 'solve' | 'classify'
  vendor: string
  base_url: string
  api_key: string
  model_name: string
}

type RuntimeConfigResponse = {
  solve: RuntimeConfigItem
  classify: RuntimeConfigItem
}

type AdminProfile = {
  id: string
  username: string
  display_name: string
  status: string
}

const loginForm = reactive({
  username: 'admin',
  password: '',
})

const accessToken = ref('')
const adminProfile = ref<AdminProfile | null>(null)
const monitor = ref<MonitorOverview | null>(null)
const runtimeConfig = reactive<RuntimeConfigResponse>({
  solve: { scope: 'solve', vendor: 'openai-compatible', base_url: '', api_key: '', model_name: '' },
  classify: { scope: 'classify', vendor: 'openai-compatible', base_url: '', api_key: '', model_name: '' },
})
const currentPage = ref<'data' | 'settings'>('data')
const credentialForm = reactive({
  username: '',
  currentPassword: '',
  newPassword: '',
})

const ui = reactive({
  loggingIn: false,
  loading: false,
  error: '',
  lastAction: '',
  lastResponseMs: 0,
  requestCount: 0,
  savingRuntimeConfig: false,
  savingCredentials: false,
})

const userStats = computed(() => monitor.value?.user_note_stats ?? [])

async function request<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const startedAt = performance.now()
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken.value ? { Authorization: `Bearer ${accessToken.value}` } : {}),
      ...(init?.headers ?? {}),
    },
  })
  ui.lastResponseMs = Number((performance.now() - startedAt).toFixed(1))
  ui.requestCount += 1
  const payload = (await response.json()) as ApiResponse<T>
  if (!response.ok || payload.code !== 0) {
    throw new Error(payload.message || 'request failed')
  }
  return payload
}

async function login() {
  ui.loggingIn = true
  ui.error = ''
  try {
    const result = await request<{
      access_token: string
      admin: AdminProfile
    }>('/v1/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify(loginForm),
    })
    accessToken.value = result.data.access_token
    adminProfile.value = result.data.admin
    credentialForm.username = result.data.admin.username
    credentialForm.currentPassword = ''
    credentialForm.newPassword = ''
    await refreshAdminData()
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '管理员登录失败'
  } finally {
    ui.loggingIn = false
  }
}

async function refreshAdminData() {
  if (!accessToken.value) return
  ui.loading = true
  ui.error = ''
  try {
    const adminRes = await request<AdminProfile>('/v1/admin/me')
    adminProfile.value = adminRes.data
    credentialForm.username = adminRes.data.username
    const monitorRes = await request<MonitorOverview>('/v1/admin/monitor/overview')
    monitor.value = monitorRes.data
    const runtimeRes = await request<RuntimeConfigResponse>('/v1/admin/runtime-config/models')
    runtimeConfig.solve = { ...runtimeRes.data.solve }
    runtimeConfig.classify = { ...runtimeRes.data.classify }
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '后台数据加载失败'
  } finally {
    ui.loading = false
  }
}

async function saveRuntimeConfig() {
  ui.savingRuntimeConfig = true
  ui.error = ''
  try {
    const result = await request<RuntimeConfigResponse>('/v1/admin/runtime-config/models', {
      method: 'PUT',
      body: JSON.stringify({
        solve: {
          vendor: runtimeConfig.solve.vendor,
          base_url: runtimeConfig.solve.base_url,
          api_key: runtimeConfig.solve.api_key,
          model_name: runtimeConfig.solve.model_name,
        },
        classify: {
          vendor: runtimeConfig.classify.vendor,
          base_url: runtimeConfig.classify.base_url,
          api_key: runtimeConfig.classify.api_key,
          model_name: runtimeConfig.classify.model_name,
        },
      }),
    })
    runtimeConfig.solve = { ...result.data.solve }
    runtimeConfig.classify = { ...result.data.classify }
    ui.lastAction = '已保存运行时模型配置'
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '模型配置保存失败'
  } finally {
    ui.savingRuntimeConfig = false
  }
}

async function saveAdminCredentials() {
  if (!credentialForm.currentPassword) {
    ui.error = '请输入当前密码'
    return
  }
  if (!credentialForm.username.trim() && !credentialForm.newPassword.trim()) {
    ui.error = '请至少修改用户名或新密码'
    return
  }

  ui.savingCredentials = true
  ui.error = ''
  try {
    const result = await request<AdminProfile>('/v1/admin/me', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: credentialForm.currentPassword,
        username: credentialForm.username.trim(),
        new_password: credentialForm.newPassword.trim() || undefined,
      }),
    })
    adminProfile.value = result.data
    loginForm.username = result.data.username
    loginForm.password = credentialForm.newPassword.trim() || credentialForm.currentPassword
    credentialForm.username = result.data.username
    credentialForm.currentPassword = ''
    credentialForm.newPassword = ''
    ui.lastAction = '已更新管理员用户名/密码'
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '管理员信息更新失败'
  } finally {
    ui.savingCredentials = false
  }
}
</script>

<template>
  <div class="admin-shell">
    <section v-if="!adminProfile" class="login-overlay">
      <div class="login-overlay-card panel">
        <div class="section-head">
          <h2>管理员登录</h2>
          <span>登录后进入状态与接口指标观察页</span>
        </div>
        <label>
          <span>用户名</span>
          <input v-model="loginForm.username" type="text" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="loginForm.password" type="password" />
        </label>
        <button class="primary-btn" :disabled="ui.loggingIn" @click="login">
          {{ ui.loggingIn ? '登录中...' : '登录后台并加载数据' }}
        </button>
        <p v-if="ui.error" class="error-text">{{ ui.error }}</p>
      </div>
    </section>

    <template v-else>
      <section class="admin-hero">
        <div>
          <h1>管理页面</h1>
        </div>
      </section>

      <section class="page-switcher">
        <button class="page-tab" :class="{ active: currentPage === 'data' }" @click="currentPage = 'data'">数据管理</button>
        <button class="page-tab" :class="{ active: currentPage === 'settings' }" @click="currentPage = 'settings'">管理设置</button>
      </section>

      <main class="admin-grid compact-grid-layout">
        <section v-if="currentPage === 'data'" class="panel section-group-panel data-management-panel">
          <div class="section-head">
            <h2>数据管理</h2>
          </div>
          <div class="group-grid data-management-grid">
            <section class="panel monitor-panel inner-panel">
              <div class="section-head">
                <h2>状态与接口指标观察</h2>
              </div>
              <div class="monitor-grid">
                <div class="monitor-card">
                  <strong>{{ monitor?.parse_job_pending ?? 0 }}</strong>
                  <span>待执行任务</span>
                </div>
                <div class="monitor-card failure">
                  <strong>{{ monitor?.parse_job_failed ?? 0 }}</strong>
                  <span>失败任务</span>
                </div>
                <div class="monitor-card success">
                  <strong>{{ monitor?.api_avg_response_ms ?? ui.lastResponseMs }}ms</strong>
                  <span>平均响应时间</span>
                </div>
              </div>
              <div class="monitor-grid compact-grid">
                <div class="monitor-card">
                  <strong>{{ monitor?.api_request_count ?? ui.requestCount }}</strong>
                  <span>API 调用次数</span>
                </div>
                <div class="monitor-card">
                  <strong>{{ ui.lastResponseMs }}ms</strong>
                  <span>最近响应时间</span>
                </div>
              </div>
              <div class="log-box">
                <h3>最近错误</h3>
                <ul>
                  <li v-for="msg in monitor?.latest_error_messages ?? ['当前无错误日志']" :key="msg">{{ msg }}</li>
                </ul>
              </div>
            </section>

            <section class="panel review-panel observation-panel inner-panel">
              <div class="section-head">
                <h2>用户笔记数量详情</h2>
              </div>
              <div v-if="userStats.length" class="review-list user-stat-list">
                <article v-for="item in userStats" :key="`${item.space_key}-${item.username}`" class="review-item user-stat-item">
                  <div>
                    <h3>{{ item.username }}</h3>
                    <p>{{ item.space_key }}</p>
                  </div>
                  <strong>{{ item.note_count }}</strong>
                </article>
              </div>
              <div v-else class="empty-card">当前暂无可展示的用户名统计。</div>
            </section>
          </div>
        </section>

        <section v-if="currentPage === 'settings'" class="panel section-group-panel management-settings-panel">
          <div class="section-head">
            <h2>管理设置</h2>
          </div>
          <div class="group-grid management-settings-grid">
            <section class="panel profile-panel inner-panel">
              <div class="section-head">
                <h2>修改登录信息</h2>
              </div>
              <div class="runtime-config-card credential-card">
                <label><span>用户名</span><input v-model="credentialForm.username" type="text" /></label>
                <label><span>当前密码</span><input v-model="credentialForm.currentPassword" type="password" /></label>
                <label><span>新密码</span><input v-model="credentialForm.newPassword" type="password" placeholder="留空则不修改密码" /></label>
                <div class="action-row">
                  <button class="primary-btn" :disabled="ui.savingCredentials" @click="saveAdminCredentials">{{ ui.savingCredentials ? '保存中...' : '保存登录信息' }}</button>
                </div>
              </div>
            </section>

            <section class="panel review-panel api-management-panel inner-panel">
              <div class="section-head">
                <h2>API 管理</h2>
              </div>
              <div class="runtime-config-grid">
                <div class="runtime-config-card">
                  <h3>文本模型</h3>
                  <label><span>Base URL</span><input v-model="runtimeConfig.solve.base_url" type="text" /></label>
                  <label><span>API Key</span><input v-model="runtimeConfig.solve.api_key" type="text" /></label>
                  <label><span>模型名</span><input v-model="runtimeConfig.solve.model_name" type="text" /></label>
                </div>
                <div class="runtime-config-card">
                  <h3>视觉模型</h3>
                  <label><span>Base URL</span><input v-model="runtimeConfig.classify.base_url" type="text" /></label>
                  <label><span>API Key</span><input v-model="runtimeConfig.classify.api_key" type="text" /></label>
                  <label><span>模型名</span><input v-model="runtimeConfig.classify.model_name" type="text" /></label>
                </div>
              </div>
              <div class="action-row">
                <button class="primary-btn" :disabled="ui.savingRuntimeConfig" @click="saveRuntimeConfig">{{ ui.savingRuntimeConfig ? '保存中...' : '保存模型配置' }}</button>
              </div>
            </section>
          </div>
        </section>

      </main>
    </template>
  </div>
</template>
