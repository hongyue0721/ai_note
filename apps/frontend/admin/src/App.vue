<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { apiBase } from './config'

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type ReviewTask = {
  id: string
  task_type: string
  entity_type: string
  entity_id: string
  status: string
  payload_json?: Record<string, unknown>
}

type MonitorOverview = {
  service_status: string
  parse_job_total: number
  parse_job_pending: number
  parse_job_failed: number
  review_task_pending: number
  latest_error_messages: string[]
}

type ParseJobItem = {
  id: string
  status: string
  entity_type: string
  entity_id: string
  content_category?: string | null
  attempt_count: number
  error_message?: string | null
  created_at: string
}

const loginForm = reactive({
  username: 'admin',
  password: 'admin123456',
})

const accessToken = ref('')
const adminProfile = ref<{ username: string; display_name: string } | null>(null)
const reviewTasks = ref<ReviewTask[]>([])
const monitor = ref<MonitorOverview | null>(null)
const parseJobs = ref<ParseJobItem[]>([])

const parseJobFilter = reactive({
  status: 'all',
  entityType: 'all',
})

const groupedParseJobs = computed(() => {
  const filtered = parseJobs.value.filter((job) =>
    (parseJobFilter.status === 'all' ? true : job.status === parseJobFilter.status) &&
    (parseJobFilter.entityType === 'all' ? true : job.entity_type === parseJobFilter.entityType),
  )

  return {
    pending: filtered.filter((job) => job.status === 'pending' || job.status === 'running'),
    failed: filtered.filter((job) => job.status === 'failed'),
    success: filtered.filter((job) => job.status === 'success'),
  }
})

const ui = reactive({
  loggingIn: false,
  loading: false,
  error: '',
  lastAction: '',
})

const failedRate = computed(() => {
  if (!monitor.value || monitor.value.parse_job_total === 0) return 0
  return Math.round((monitor.value.parse_job_failed / monitor.value.parse_job_total) * 100)
})

async function request<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken.value ? { Authorization: `Bearer ${accessToken.value}` } : {}),
      ...(init?.headers ?? {}),
    },
  })
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
    const [reviewRes, monitorRes, parseJobRes] = await Promise.all([
      request<ReviewTask[]>('/v1/review/tasks?status=pending'),
      request<MonitorOverview>('/v1/admin/monitor/overview'),
      request<ParseJobItem[]>('/v1/admin/parse-jobs'),
    ])

    reviewTasks.value = reviewRes.data
    monitor.value = monitorRes.data
    parseJobs.value = parseJobRes.data
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '后台数据加载失败'
  } finally {
    ui.loading = false
  }
}

async function retryParseJob(jobId: string) {
  try {
    await request(`/v1/parse-jobs/${jobId}/retry`, {
      method: 'POST',
    })
    ui.lastAction = `已重试任务 · ${jobId.slice(0, 8)}`
    await refreshAdminData()
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '任务重试失败'
  }
}

async function decide(taskId: string, action: 'approve' | 'reject' | 'replace') {
  try {
    await request(`/v1/review/tasks/${taskId}/decision`, {
      method: 'POST',
      body: JSON.stringify({ action, edited_tags: action === 'replace' ? [{ tag_id: 'manual-tag' }] : [] }),
    })
    ui.lastAction = `已执行 ${action} · ${taskId.slice(0, 8)}`
    await refreshAdminData()
  } catch (error) {
    ui.error = error instanceof Error ? error.message : '审核操作失败'
  }
}
</script>

<template>
  <div class="admin-shell">
    <section class="admin-hero">
      <div>
        <span class="eyebrow">StarGraph AI · Admin Console</span>
        <h1>审核、任务状态与监控，集中在一块看清楚。</h1>
        <p>后台端重点服务比赛演示与运维排障：登录、审核任务处理、任务状态观察、错误快速定位。</p>
      </div>
      <div class="admin-hero-card">
        <div class="metric"><strong>{{ monitor?.parse_job_total ?? 0 }}</strong><span>任务总数</span></div>
        <div class="metric"><strong>{{ monitor?.review_task_pending ?? 0 }}</strong><span>待审核</span></div>
        <div class="metric"><strong>{{ failedRate }}%</strong><span>失败率</span></div>
      </div>
    </section>

    <main class="admin-grid">
      <section class="panel login-panel">
        <div class="section-head">
          <h2>管理员登录</h2>
          <span>独立管理员账号体系</span>
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
        <div v-if="adminProfile" class="profile-card">
          <strong>{{ adminProfile.display_name }}</strong>
          <span>{{ adminProfile.username }}</span>
        </div>
      </section>

      <section class="panel monitor-panel">
        <div class="section-head">
          <h2>监控总览</h2>
          <span>{{ monitor?.service_status ?? 'idle' }}</span>
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
            <strong>{{ monitor?.review_task_pending ?? 0 }}</strong>
            <span>待审核任务</span>
          </div>
        </div>
        <div class="log-box">
          <h3>最近错误</h3>
          <ul>
            <li v-for="msg in monitor?.latest_error_messages ?? ['当前无错误日志']" :key="msg">{{ msg }}</li>
          </ul>
        </div>
      </section>

      <section class="panel review-panel">
        <div class="section-head">
          <h2>审核任务</h2>
          <span>{{ ui.lastAction || '支持 approve / reject / replace' }}</span>
        </div>
        <div v-if="reviewTasks.length" class="review-list">
          <article v-for="task in reviewTasks" :key="task.id" class="review-item">
            <div>
              <h3>{{ task.task_type }} · {{ task.entity_type }}</h3>
              <p>{{ task.id }}</p>
            </div>
            <pre>{{ JSON.stringify(task.payload_json, null, 2) }}</pre>
            <div class="action-row">
              <button class="ghost-btn" @click="decide(task.id, 'approve')">Approve</button>
              <button class="ghost-btn danger" @click="decide(task.id, 'reject')">Reject</button>
              <button class="ghost-btn" @click="decide(task.id, 'replace')">Replace</button>
            </div>
          </article>
        </div>
        <div v-else class="empty-card">当前没有待审核任务。</div>
      </section>

      <section class="panel review-panel">
        <div class="section-head">
          <h2>解析任务</h2>
          <span>查看 pending / failed / success 的任务流</span>
        </div>
        <label>
          <span>状态筛选</span>
          <select v-model="parseJobFilter.status">
            <option value="all">全部</option>
            <option value="pending">pending</option>
            <option value="running">running</option>
            <option value="failed">failed</option>
            <option value="success">success</option>
          </select>
        </label>
        <label>
          <span>实体类型筛选</span>
          <select v-model="parseJobFilter.entityType">
            <option value="all">全部</option>
            <option value="problem">problem</option>
            <option value="note">note</option>
            <option value="document">document</option>
          </select>
        </label>
        <div v-if="parseJobs.length" class="job-group-list">
          <section class="job-group">
            <h3>Pending / Running · {{ groupedParseJobs.pending.length }}</h3>
            <div v-if="groupedParseJobs.pending.length" class="review-list">
              <article v-for="job in groupedParseJobs.pending" :key="job.id" class="review-item">
                <div>
                  <h3>{{ job.entity_type }} · {{ job.content_category ?? 'uncategorized' }}</h3>
                  <p>{{ job.id }}</p>
                </div>
                <pre>{{ JSON.stringify(job, null, 2) }}</pre>
              </article>
            </div>
            <div v-else class="empty-card">当前没有 pending/running 任务。</div>
          </section>

          <section class="job-group">
            <h3>Failed · {{ groupedParseJobs.failed.length }}</h3>
            <div v-if="groupedParseJobs.failed.length" class="review-list">
              <article v-for="job in groupedParseJobs.failed" :key="job.id" class="review-item">
                <div>
                  <h3>{{ job.entity_type }} · {{ job.content_category ?? 'uncategorized' }}</h3>
                  <p>{{ job.id }}</p>
                </div>
                <div v-if="job.error_message" class="inline-error-box">
                  <strong>失败原因</strong>
                  <span>{{ job.error_message }}</span>
                </div>
                <pre>{{ JSON.stringify(job, null, 2) }}</pre>
                <div class="action-row">
                  <button class="ghost-btn" @click="retryParseJob(job.id)">重试任务</button>
                </div>
              </article>
            </div>
            <div v-else class="empty-card">当前没有 failed 任务。</div>
          </section>

          <section class="job-group">
            <h3>Success · {{ groupedParseJobs.success.length }}</h3>
            <div v-if="groupedParseJobs.success.length" class="review-list">
              <article v-for="job in groupedParseJobs.success" :key="job.id" class="review-item">
                <div>
                  <h3>{{ job.entity_type }} · {{ job.content_category ?? 'uncategorized' }}</h3>
                  <p>{{ job.id }}</p>
                </div>
                <pre>{{ JSON.stringify(job, null, 2) }}</pre>
              </article>
            </div>
            <div v-else class="empty-card">当前没有 success 任务。</div>
          </section>
        </div>
        <div v-else class="empty-card">当前没有解析任务。</div>
      </section>
    </main>
  </div>
</template>
