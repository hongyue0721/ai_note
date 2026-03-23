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

const loginForm = reactive({
  username: 'admin',
  password: 'admin123456',
})

const accessToken = ref('')
const adminProfile = ref<{ username: string; display_name: string } | null>(null)
const monitor = ref<MonitorOverview | null>(null)
const runtimeConfig = reactive<RuntimeConfigResponse>({
  solve: { scope: 'solve', vendor: 'openai-compatible', base_url: '', api_key: '', model_name: '' },
  classify: { scope: 'classify', vendor: 'openai-compatible', base_url: '', api_key: '', model_name: '' },
})

const ui = reactive({
  loggingIn: false,
  loading: false,
  error: '',
  lastAction: '',
  lastResponseMs: 0,
  requestCount: 0,
  savingRuntimeConfig: false,
})

const failedRate = computed(() => {
  if (!monitor.value || monitor.value.parse_job_total === 0) return 0
  return Math.round((monitor.value.parse_job_failed / monitor.value.parse_job_total) * 100)
})
const userStats = computed(() => monitor.value?.user_note_stats ?? [])
const adminDisplayName = computed(() => adminProfile.value?.display_name || '管理员')
const adminUsername = computed(() => adminProfile.value?.username || 'admin')

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
      admin: { username: string; display_name: string }
    }>('/v1/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify(loginForm),
    })
    accessToken.value = result.data.access_token
    adminProfile.value = result.data.admin
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
          <span class="eyebrow">StarGraph AI · Admin Console</span>
          <h1>登录、状态、接口指标与 API 管理。</h1>
          <p>后台端收口为单独登录层，以及面向演示与排障的实时观测页：请求数、平均响应、注册用户与笔记规模集中查看。</p>
        </div>
        <div class="admin-hero-card">
          <div class="metric"><strong>{{ monitor?.api_request_count ?? ui.requestCount }}</strong><span>请求数</span></div>
          <div class="metric"><strong>{{ monitor?.api_avg_response_ms ?? ui.lastResponseMs }}ms</strong><span>平均响应</span></div>
          <div class="metric"><strong>{{ monitor?.total_user_count ?? 0 }}</strong><span>注册用户名数</span></div>
          <div class="metric"><strong>{{ monitor?.total_note_count ?? 0 }}</strong><span>笔记总数</span></div>
        </div>
      </section>

      <main class="admin-grid compact-grid-layout">
        <section class="panel profile-panel">
          <div class="section-head">
            <h2>当前管理员</h2>
            <span>{{ monitor?.service_status ?? 'idle' }}</span>
          </div>
          <div class="profile-card">
            <strong>{{ adminDisplayName }}</strong>
            <span>{{ adminUsername }}</span>
          </div>
          <div class="metric-stack">
            <div class="monitor-card">
              <strong>{{ monitor?.parse_job_total ?? 0 }}</strong>
              <span>解析任务总数</span>
            </div>
            <div class="monitor-card">
              <strong>{{ failedRate }}%</strong>
              <span>失败率</span>
            </div>
          </div>
        </section>

        <section class="panel monitor-panel">
          <div class="section-head">
            <h2>状态与接口指标观察</h2>
            <span>{{ ui.lastAction || '仅保留登录、状态与接口指标观察' }}</span>
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

        <section class="panel review-panel observation-panel">
          <div class="section-head">
            <h2>注册用户名与笔记数量</h2>
            <span>展示最近注册/存在的用户名空间与对应笔记总量</span>
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

        <section class="panel review-panel api-management-panel">
          <div class="section-head">
            <h2>API 管理</h2>
            <span>管理员可持久化修改 solve / classify 的供应商、地址、密钥与模型</span>
          </div>
          <div class="runtime-config-grid">
            <div class="runtime-config-card">
              <h3>Solve</h3>
              <label><span>供应商</span><input v-model="runtimeConfig.solve.vendor" type="text" /></label>
              <label><span>Base URL</span><input v-model="runtimeConfig.solve.base_url" type="text" /></label>
              <label><span>API Key</span><input v-model="runtimeConfig.solve.api_key" type="text" /></label>
              <label><span>模型名</span><input v-model="runtimeConfig.solve.model_name" type="text" /></label>
            </div>
            <div class="runtime-config-card">
              <h3>Classify</h3>
              <label><span>供应商</span><input v-model="runtimeConfig.classify.vendor" type="text" /></label>
              <label><span>Base URL</span><input v-model="runtimeConfig.classify.base_url" type="text" /></label>
              <label><span>API Key</span><input v-model="runtimeConfig.classify.api_key" type="text" /></label>
              <label><span>模型名</span><input v-model="runtimeConfig.classify.model_name" type="text" /></label>
            </div>
          </div>
          <div class="action-row">
            <button class="primary-btn" :disabled="ui.savingRuntimeConfig" @click="saveRuntimeConfig">{{ ui.savingRuntimeConfig ? '保存中...' : '保存模型配置' }}</button>
          </div>
        </section>

      </main>
    </template>
  </div>
</template>
