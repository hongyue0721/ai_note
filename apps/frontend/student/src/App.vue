<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import StudentAskWorkspace from './components/student/StudentAskWorkspace.vue'
import StudentAuthCard from './components/student/StudentAuthCard.vue'
import StudentNoteEditWorkspace from './components/student/StudentNoteEditWorkspace.vue'
import StudentNoteDetailWorkspace from './components/student/StudentNoteDetailWorkspace.vue'
import StudentNotesWorkspace from './components/student/StudentNotesWorkspace.vue'
import StudentUploadWorkspace from './components/student/StudentUploadWorkspace.vue'
import StudentWorkspaceHeader from './components/student/StudentWorkspaceHeader.vue'
import { apiBase } from './config'
import type { ApiResponse, AskAnalysisState, GraphOverview, NoteItem, NotesPageState, NotesSearchState, RelatedNoteItem, SearchItem, SolveResult, TagItem, UploadPreview, WorkspaceTab, UploadStep, UserProfile } from './types'

const loginForm = reactive({ spaceKey: 'default' })
const noteUploadForm = reactive({ filename: '', mimeType: 'text/plain', fileKind: 'document', contentType: 'note', textContent: '' })
const askForm = reactive({ questionText: '' })
const searchForm = reactive({ q: '方程' })
const ui = reactive({ loggingIn: false, loginError: '', previewingUpload: false, confirmingUpload: false, uploadError: '', uploadSuccess: '', solvingQuestion: false, questionError: '', deletingNoteId: '', savingQuestionNote: false, savingNoteTags: false })

const accessToken = ref('')
const currentUser = ref<UserProfile | null>(null)
const activeTab = ref<WorkspaceTab>('upload')
const uploadStep = ref<UploadStep>('form')
const notes = ref<NoteItem[]>([])
const selectedNote = ref<NoteItem | null>(null)
const selectedSubjectFilter = ref('')
const selectedContentTypeFilter = ref('')
const selectedKnowledgeTagFilters = ref<string[]>([])
const searchResults = ref<SearchItem[]>([])
const graphOverview = ref<GraphOverview | null>(null)
const uploadPreview = ref<UploadPreview | null>(null)
const questionPreview = ref<UploadPreview | null>(null)
const solveResult = ref<SolveResult | null>(null)
const createdFileUrl = ref('')
const newTagDraft = ref('')
const pickedNoteFile = ref<File | null>(null)
const pickedNoteFilePreviewUrl = ref('')
const pickedQuestionFile = ref<File | null>(null)
const pickedQuestionFilePreviewUrl = ref('')
const uploadedNoteFileId = ref<string | null>(null)
const uploadedQuestionFileId = ref<string | null>(null)
const noteFileInputKey = ref(0)
const questionFileInputKey = ref(0)
const notesSearchVisible = ref(false)
const notesPage = ref(1)
const noteTagDraft = ref('')
const askResultTagDraft = ref('')
const askResultTags = ref<TagItem[]>([])
let searchRequestToken = 0
let askStreamTimer: number | null = null

const subjectLabelMap: Record<string, string> = { math: '数学', chinese: '语文', english: '英语', physics: '物理', chemistry: '化学', biology: '生物', history: '历史', geography: '地理', politics: '政治', general: '通用' }
const contentTypeLabelMap: Record<string, string> = { note: '笔记', document: '资料', problem: '错题' }

function normalizeSubjectLabel(subject: string) {
  const key = subject.trim().toLowerCase()
  return subjectLabelMap[key] || subject || '通用'
}

function normalizeContentTypeLabel(category: string) {
  const key = category.trim().toLowerCase()
  return contentTypeLabelMap[key] || category
}

function decorateNoteItem(note: NoteItem): NoteItem {
  const typeTag = normalizeContentTypeLabel(note.category)
  const tags = [...note.tags]
  if (!tags.some((tag) => tag.name === typeTag)) tags.unshift({ name: typeTag, confidence: 1 })
  return {
    ...note,
    subject: normalizeSubjectLabel(note.subject),
    category: typeTag,
    tags,
  }
}

const workspaceTabs: Array<{ key: WorkspaceTab; label: string }> = [
  { key: 'upload', label: '上传笔记' },
  { key: 'ask', label: '询问问题' },
  { key: 'notes', label: '笔记管理' },
]

const graphNodes = computed(() => graphOverview.value?.nodes ?? [])
const subjectNodes = computed(() => {
  const counts = new Map<string, number>()
  for (const note of notes.value) counts.set(note.subject, (counts.get(note.subject) ?? 0) + 1)
  return Array.from(counts.entries()).map(([name, count]) => ({ name, count, active: selectedSubjectFilter.value === name })).sort((a, b) => b.count - a.count)
})
const contentTypeTagNames = Object.values(contentTypeLabelMap)
const allFilteredNotes = computed(() => notes.value.filter((note) => {
  const subjectMatch = !selectedSubjectFilter.value || note.subject === selectedSubjectFilter.value
  const contentTypeMatch = !selectedContentTypeFilter.value || note.tags.some((tag) => tag.name === selectedContentTypeFilter.value)
  const knowledgeMatch = !selectedKnowledgeTagFilters.value.length || selectedKnowledgeTagFilters.value.every((tagName) => note.tags.some((tag) => tag.name === tagName))
  return subjectMatch && contentTypeMatch && knowledgeMatch
}))
const notesPageState = computed<NotesPageState>(() => {
  const total = allFilteredNotes.value.length
  const pageSize = 5
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const page = Math.min(notesPage.value, totalPages)
  return { page, pageSize, total, totalPages }
})
const filteredNotes = computed(() => {
  const start = (notesPageState.value.page - 1) * notesPageState.value.pageSize
  return allFilteredNotes.value.slice(start, start + notesPageState.value.pageSize)
})
const visibleTagNodes = computed(() => {
  const scopedNotes = notes.value.filter((note) => !selectedSubjectFilter.value || note.subject === selectedSubjectFilter.value)
  const weights = new Map<string, number>()
  for (const note of scopedNotes) {
    for (const tag of note.tags) {
      if (contentTypeTagNames.includes(tag.name)) continue
      weights.set(tag.name, (weights.get(tag.name) ?? 0) + (Number(tag.confidence) || 0))
    }
  }
  return Array.from(weights.entries()).map(([name, weight]) => ({ name, weight: Number(weight.toFixed(2)), linked: selectedKnowledgeTagFilters.value.includes(name) })).sort((a, b) => b.weight - a.weight)
})
const contentTypeNodes = computed(() => contentTypeTagNames.map((name) => ({ name, linked: selectedContentTypeFilter.value === name })))
const pickedNoteFileName = computed(() => pickedNoteFile.value?.name || '')
const selectedNotePreviewKind = computed(() => {
  const note = selectedNote.value
  if (!note?.file_url || !note.mime_type) return 'text'
  if (note.mime_type.startsWith('image/')) return 'image'
  if (note.mime_type === 'application/pdf') return 'pdf'
  return 'file'
})
const pickedQuestionFileName = computed(() => pickedQuestionFile.value?.name || '')
const relatedNotes = computed<RelatedNoteItem[]>(() => {
  const note = selectedNote.value
  if (!note) return []
  const noteTags = new Set(note.tags.map((tag) => tag.name))
  return notes.value
    .filter((item) => item.id !== note.id)
    .map((item) => {
      let score = 0
      if (item.subject === note.subject) score += 3
      const titleWords = (note.title || '').split(/\s+/).filter(Boolean)
      if (titleWords.some((word) => word && (item.title || '').includes(word))) score += 2
      const sharedTags = item.tags.filter((tag) => noteTags.has(tag.name)).length
      score += sharedTags
      return { item, score, reason: sharedTags ? '共享知识点' : item.subject === note.subject ? '同科目' : '标题相关' }
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
    .map(({ item, reason }) => ({ id: item.id, title: item.title || item.category, subject: item.subject, reason }))
})
const askAnalysisState = computed<AskAnalysisState>(() => ({
  pickedFileName: pickedQuestionFileName.value,
  pickedFilePreviewUrl: pickedQuestionFilePreviewUrl.value,
  preview: questionPreview.value,
  solveResult: solveResult.value,
  streamedMarkdown: streamedSolveMarkdown.value,
  resultTags: askResultTags.value,
  questionError: ui.questionError,
  solvingQuestion: ui.solvingQuestion,
  savingQuestionNote: ui.savingQuestionNote,
  uploadButtonDisabled: false,
}))
const notesSearchState = computed<NotesSearchState>(() => ({
  visible: notesSearchVisible.value,
  query: searchForm.q,
  results: searchResults.value,
}))
const streamedSolveMarkdown = ref('')

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
  if (!response.ok || payload.code !== 0) throw new Error(payload.message || 'request failed')
  return payload
}

async function login() {
  ui.loggingIn = true
  ui.loginError = ''
  try {
    const result = await request<{ access_token: string; user: UserProfile }>('/v1/auth/space-enter', {
      method: 'POST',
      body: JSON.stringify({ space_key: loginForm.spaceKey }),
    })
    accessToken.value = result.data.access_token
    currentUser.value = result.data.user
    await refreshWorkspace()
  } catch (error) {
    ui.loginError = error instanceof Error ? error.message : '登录失败'
  } finally {
    ui.loggingIn = false
  }
}

async function refreshWorkspace() {
  if (!accessToken.value) return
  const [noteRes, graphRes] = await Promise.all([request<NoteItem[]>('/v1/notes'), request<GraphOverview>('/v1/graph/overview')])
  notes.value = noteRes.data.map(decorateNoteItem)
  selectedNote.value = notes.value.find((item) => item.id === selectedNote.value?.id) ?? notes.value[0] ?? null
  graphOverview.value = graphRes.data
  if (selectedSubjectFilter.value && !notes.value.some((note) => note.subject === selectedSubjectFilter.value)) selectedSubjectFilter.value = ''
  if (selectedContentTypeFilter.value && !notes.value.some((note) => note.tags.some((tag) => tag.name === selectedContentTypeFilter.value))) selectedContentTypeFilter.value = ''
  selectedKnowledgeTagFilters.value = selectedKnowledgeTagFilters.value.filter((tagName) => notes.value.some((note) => note.tags.some((tag) => tag.name === tagName)))
  if (notesPage.value > Math.max(1, Math.ceil(notes.value.length / 5))) notesPage.value = 1
}

function resolveAssetUrl(url: string | null | undefined) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  if (url.startsWith('/')) return `${apiBase}${url}`
  return `${apiBase}/${url}`
}

async function downloadSelectedNoteOriginalFile() {
  if (!selectedNote.value?.file_url) return
  const response = await fetch(resolveAssetUrl(selectedNote.value.file_url))
  if (!response.ok) throw new Error('下载原文件失败')
  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = selectedNote.value.original_filename || `${selectedNote.value.title || '原文件'}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(objectUrl)
}

function setPreviewUrl(target: 'note' | 'question', file: File | null) {
  if (target === 'note' && pickedNoteFilePreviewUrl.value) { URL.revokeObjectURL(pickedNoteFilePreviewUrl.value); pickedNoteFilePreviewUrl.value = '' }
  if (target === 'question' && pickedQuestionFilePreviewUrl.value) { URL.revokeObjectURL(pickedQuestionFilePreviewUrl.value); pickedQuestionFilePreviewUrl.value = '' }
  if (!file || !file.type.startsWith('image/')) return
  const nextUrl = URL.createObjectURL(file)
  if (target === 'note') pickedNoteFilePreviewUrl.value = nextUrl
  else pickedQuestionFilePreviewUrl.value = nextUrl
}

function applyNoteFile(file: File | null) {
  pickedNoteFile.value = file
  uploadPreview.value = null
  uploadStep.value = 'form'
  uploadedNoteFileId.value = null
  if (file) {
    noteUploadForm.filename = file.name
    noteUploadForm.mimeType = file.type || 'application/octet-stream'
    noteUploadForm.fileKind = file.type.startsWith('image/') ? 'image' : 'document'
  }
  setPreviewUrl('note', file)
}

function onNoteFilePicked(event: Event) {
  const input = event.target as HTMLInputElement
  applyNoteFile(input.files?.[0] ?? null)
}

function onNoteFileDropped(file: File) {
  applyNoteFile(file)
}

async function applyQuestionFile(file: File | null) {
  pickedQuestionFile.value = file
  questionPreview.value = null
  uploadedQuestionFileId.value = null
  setPreviewUrl('question', file)
}

async function onQuestionFilePicked(event: Event) {
  const input = event.target as HTMLInputElement
  await applyQuestionFile(input.files?.[0] ?? null)
}

async function onQuestionFileDropped(file: File) {
  await applyQuestionFile(file)
}

async function uploadFileToLocalStorage(fileId: string, objectKey: string, file: File) {
  const formData = new FormData()
  formData.append('file_id', fileId)
  formData.append('object_key', objectKey)
  formData.append('upload_file', file)
  const response = await fetch(`${apiBase}/v1/files/upload-local`, { method: 'POST', headers: { ...(accessToken.value ? { Authorization: `Bearer ${accessToken.value}` } : {}) }, body: formData })
  const payload = (await response.json()) as ApiResponse<{ bytes_written: number }>
  if (!response.ok || payload.code !== 0) throw new Error(payload.message || 'local upload failed')
  return payload.data
}

async function createAndUploadFile(file: File, contentType: string, fileKind: string, mimeType: string) {
  const policy = await request<{ file_id: string; object_key: string }>('/v1/files/upload-policy', { method: 'POST', body: JSON.stringify({ filename: file.name, mime_type: mimeType, content_type: contentType, file_kind: fileKind }) })
  const localUpload = await uploadFileToLocalStorage(policy.data.file_id, policy.data.object_key, file)
  const confirm = await request<{ file_url: string }>('/v1/files/confirm', { method: 'POST', body: JSON.stringify({ file_id: policy.data.file_id, object_key: policy.data.object_key, size_bytes: localUpload.bytes_written, mime_type: mimeType, sha256: `demo-${Date.now()}` }) })
  createdFileUrl.value = confirm.data.file_url
  return policy.data.file_id
}

async function previewNoteTags() {
  if (!accessToken.value) return
  ui.previewingUpload = true
  ui.uploadError = ''
  ui.uploadSuccess = ''
  try {
    let fileId = uploadedNoteFileId.value
    if (pickedNoteFile.value && !fileId) {
      fileId = await createAndUploadFile(pickedNoteFile.value, noteUploadForm.contentType, noteUploadForm.fileKind, noteUploadForm.mimeType)
      uploadedNoteFileId.value = fileId
    }
    const preview = await request<UploadPreview>('/v1/preview/upload-tags', {
      method: 'POST',
      body: JSON.stringify({ filename: noteUploadForm.filename || (pickedNoteFile.value?.name ?? 'upload-note'), mime_type: noteUploadForm.mimeType, file_kind: noteUploadForm.fileKind, content_type: noteUploadForm.contentType, subject: noteUploadForm.contentType === 'problem' ? '数学' : '通用', text_content: noteUploadForm.textContent, file_id: fileId }),
    })
    uploadPreview.value = preview.data
    uploadPreview.value.subject = normalizeSubjectLabel(uploadPreview.value.subject)
    const typeTag = normalizeContentTypeLabel(noteUploadForm.contentType)
    if (!uploadPreview.value.knowledge_candidates.some((tag) => tag.name === typeTag)) uploadPreview.value.knowledge_candidates.unshift({ name: typeTag, confidence: 1 })
    noteUploadForm.textContent = preview.data.normalized_text
    uploadStep.value = 'confirm'
  } catch (error) {
    ui.uploadError = error instanceof Error ? error.message : '标签预览失败'
  } finally {
    ui.previewingUpload = false
  }
}

function updatePreviewTag(index: number, value: string) {
  if (!uploadPreview.value) return
  uploadPreview.value.knowledge_candidates[index].name = value
}

function removePreviewTag(index: number) {
  if (!uploadPreview.value) return
  uploadPreview.value.knowledge_candidates.splice(index, 1)
}

function addPreviewTag() {
  if (!uploadPreview.value || !newTagDraft.value.trim()) return
  uploadPreview.value.knowledge_candidates.push({ name: newTagDraft.value.trim(), confidence: 1 })
  newTagDraft.value = ''
}

function returnUploadResultToForm() {
  uploadPreview.value = null
  uploadStep.value = 'form'
  uploadedNoteFileId.value = null
  newTagDraft.value = ''
  createdFileUrl.value = ''
}

function resetUploadComposer() {
  uploadPreview.value = null
  uploadStep.value = 'form'
  uploadedNoteFileId.value = null
  newTagDraft.value = ''
  createdFileUrl.value = ''
  pickedNoteFile.value = null
  if (pickedNoteFilePreviewUrl.value) {
    URL.revokeObjectURL(pickedNoteFilePreviewUrl.value)
    pickedNoteFilePreviewUrl.value = ''
  }
  noteUploadForm.filename = ''
  noteUploadForm.mimeType = 'text/plain'
  noteUploadForm.fileKind = 'document'
  noteUploadForm.contentType = 'note'
  noteUploadForm.textContent = ''
  noteFileInputKey.value += 1
}

function resetQuestionComposer() {
  if (askStreamTimer) window.clearInterval(askStreamTimer)
  questionPreview.value = null
  solveResult.value = null
  streamedSolveMarkdown.value = ''
  uploadedQuestionFileId.value = null
  pickedQuestionFile.value = null
  askResultTags.value = []
  askResultTagDraft.value = ''
  if (pickedQuestionFilePreviewUrl.value) {
    URL.revokeObjectURL(pickedQuestionFilePreviewUrl.value)
    pickedQuestionFilePreviewUrl.value = ''
  }
  askForm.questionText = ''
  questionFileInputKey.value += 1
}

async function confirmNoteRecord() {
  if (!accessToken.value || !uploadPreview.value) return
  ui.confirmingUpload = true
  ui.uploadError = ''
  try {
    const result = await request<NoteItem>('/v1/notes/confirm', {
      method: 'POST',
      body: JSON.stringify({
        ...uploadPreview.value,
        file_id: uploadedNoteFileId.value,
        title: uploadPreview.value.title,
        summary: uploadPreview.value.summary,
        subject: uploadPreview.value.subject,
        content_category: noteUploadForm.contentType,
        normalized_text: noteUploadForm.textContent,
      }),
    })
    ui.uploadSuccess = `已确认并入库：${normalizeContentTypeLabel(result.data.category)} · ${normalizeSubjectLabel(result.data.subject)}`
    resetUploadComposer()
    await refreshWorkspace()
    activeTab.value = 'notes'
  } catch (error) {
    ui.uploadError = error instanceof Error ? error.message : '确认入库失败'
  } finally {
    ui.confirmingUpload = false
  }
}

async function previewQuestionFileAnalysis() {
  if (!accessToken.value || !pickedQuestionFile.value) return
  ui.questionError = ''
  try {
    let fileId = uploadedQuestionFileId.value
    if (!fileId) {
      fileId = await createAndUploadFile(
        pickedQuestionFile.value,
        'problem',
        pickedQuestionFile.value.type.startsWith('image/') ? 'image' : 'document',
        pickedQuestionFile.value.type || 'application/octet-stream',
      )
      uploadedQuestionFileId.value = fileId
    }
    const preview = await request<UploadPreview>('/v1/preview/upload-tags', {
      method: 'POST',
      body: JSON.stringify({
        filename: pickedQuestionFile.value.name,
        mime_type: pickedQuestionFile.value.type || 'application/octet-stream',
        file_kind: pickedQuestionFile.value.type.startsWith('image/') ? 'image' : 'document',
        content_type: 'problem',
        subject: 'general',
        text_content: askForm.questionText,
        file_id: fileId,
      }),
    })
    questionPreview.value = preview.data
    return preview.data
  } catch (error) {
    ui.questionError = error instanceof Error ? error.message : '题目文件分析失败'
    questionPreview.value = null
    return null
  }
}

function buildQuestionPayloadText() {
  const manualText = askForm.questionText.trim()
  const analyzedText = questionPreview.value?.normalized_text?.trim() || ''
  if (manualText && analyzedText) {
    return `用户补充说明：\n${manualText}\n\n上传文件/图片解析内容：\n${analyzedText}`
  }
  return analyzedText || manualText
}

async function askQuestion() {
  if (!accessToken.value || (!askForm.questionText.trim() && !pickedQuestionFile.value)) return
  ui.solvingQuestion = true
  ui.questionError = ''
  streamedSolveMarkdown.value = ''
  try {
    if (pickedQuestionFile.value && !questionPreview.value) await previewQuestionFileAnalysis()
    const questionText = buildQuestionPayloadText()
    if (!questionText.trim()) throw new Error('请先输入问题文本或上传题目文件')
    const response = await request<SolveResult>('/v1/solve', { method: 'POST', body: JSON.stringify({ question_text: questionText, subject: normalizeSubjectLabel(questionPreview.value?.subject?.trim() || '数学'), allow_ai_fallback: true }) })
    solveResult.value = response.data
    askResultTags.value = response.data.knowledge_points.map((name) => ({ name, confidence: 1 }))
    const markdown = [`# ${response.data.subject} · ${response.data.question_type}`, '', `**最终答案**`, '', response.data.final_answer, '', '**解题步骤**', '', ...response.data.solution_steps.map((step, index) => `${index + 1}. ${step}`), '', '**知识点**', '', ...response.data.knowledge_points.map((item) => `- ${item}`)].join('\n')
    let cursor = 0
    if (askStreamTimer) window.clearInterval(askStreamTimer)
    askStreamTimer = window.setInterval(() => {
      cursor += Math.max(6, Math.ceil(markdown.length / 40))
      streamedSolveMarkdown.value = markdown.slice(0, cursor)
      if (cursor >= markdown.length && askStreamTimer) {
        window.clearInterval(askStreamTimer)
        askStreamTimer = null
      }
    }, 45)
    activeTab.value = 'ask'
  } catch (error) {
    ui.questionError = error instanceof Error ? error.message : '提问失败'
  } finally {
    ui.solvingQuestion = false
  }
}

async function saveQuestionAsNote() {
  if (!accessToken.value) return
  ui.savingQuestionNote = true
  ui.questionError = ''
  try {
    const ensuredPreview = questionPreview.value || (pickedQuestionFile.value ? await previewQuestionFileAnalysis() : null)
    const fallbackPreview = !ensuredPreview ? {
      entity_type: 'note',
      content_category: 'problem',
      subject: solveResult.value?.subject || '数学',
      title: askForm.questionText.trim().slice(0, 48) || '错题笔记',
      summary: solveResult.value?.final_answer || '',
      normalized_text: buildQuestionPayloadText() || askForm.questionText,
      knowledge_candidates: askResultTags.value,
      confidence: solveResult.value?.confidence || 1,
      needs_review: false,
      review_reason: null,
    } : null
    const noteSource = ensuredPreview || fallbackPreview
    if (!noteSource) throw new Error('请先输入问题或生成答案')
    const result = await request<NoteItem>('/v1/notes/confirm', {
      method: 'POST',
      body: JSON.stringify({
        ...noteSource,
        file_id: uploadedQuestionFileId.value,
        title: noteSource.title || pickedQuestionFile.value?.name || '错题笔记',
        summary: noteSource.summary,
        subject: noteSource.subject,
        content_category: 'problem',
        normalized_text: [
          noteSource.normalized_text || askForm.questionText,
          solveResult.value?.final_answer ? `\n\n【最终答案】\n${solveResult.value.final_answer}` : '',
          solveResult.value?.solution_steps?.length ? `\n\n【解题步骤】\n${solveResult.value.solution_steps.map((step: string, i: number) => `${i + 1}. ${step}`).join('\n')}` : '',
          solveResult.value?.knowledge_points?.length ? `\n\n【涉及知识点】\n${solveResult.value.knowledge_points.join('、')}` : '',
        ].filter(Boolean).join(''),
        knowledge_candidates: askResultTags.value.length ? askResultTags.value : noteSource.knowledge_candidates,
      }),
    })
    await refreshWorkspace()
    selectedNote.value = result.data
    resetQuestionComposer()
    activeTab.value = 'ask'
  } catch (error) {
    ui.questionError = error instanceof Error ? error.message : '加入笔记失败'
  } finally {
    ui.savingQuestionNote = false
  }
}

function updateAskResultTag(index: number, value: string) {
  if (!askResultTags.value[index]) return
  askResultTags.value[index].name = value
}

function removeAskResultTag(index: number) {
  askResultTags.value.splice(index, 1)
}

function addAskResultTag() {
  if (!askResultTagDraft.value.trim()) return
  askResultTags.value.push({ name: askResultTagDraft.value.trim(), confidence: 1 })
  askResultTagDraft.value = ''
}

function returnToAskStep() {
  solveResult.value = null
  streamedSolveMarkdown.value = ''
}

async function runSearch() {
  const keyword = searchForm.q.trim()
  const currentToken = ++searchRequestToken
  if (!accessToken.value || !keyword) {
    searchResults.value = []
    return
  }
  const response = await request<{ items: SearchItem[] }>(`/v1/search?q=${encodeURIComponent(keyword)}`)
  if (currentToken === searchRequestToken) searchResults.value = response.data.items.map((item) => ({ ...item, subject: normalizeSubjectLabel(item.subject), category: normalizeContentTypeLabel(item.category) }))
}

function pickSearchResult(item: SearchItem) {
  const target = notes.value.find((note) => note.id === item.id)
  if (target) { selectedNote.value = target; activeTab.value = 'note-detail' }
}

function toggleNotesSearch() {
  notesSearchVisible.value = !notesSearchVisible.value
  if (!notesSearchVisible.value) {
    searchForm.q = ''
    searchResults.value = []
  }
}

function updateSearchQuery(value: string) {
  searchForm.q = value
}

function applySubjectFilter(subjectName: string) {
  selectedSubjectFilter.value = selectedSubjectFilter.value === subjectName ? '' : subjectName
  activeTab.value = 'notes'
}

function applyContentTypeFilter(tagName: string) {
  selectedContentTypeFilter.value = selectedContentTypeFilter.value === tagName ? '' : tagName
  activeTab.value = 'notes'
}

function toggleKnowledgeTagFilter(tagName: string) {
  selectedKnowledgeTagFilters.value = selectedKnowledgeTagFilters.value.includes(tagName)
    ? selectedKnowledgeTagFilters.value.filter((item) => item !== tagName)
    : [...selectedKnowledgeTagFilters.value, tagName]
  activeTab.value = 'notes'
}

function clearTagFilter() {
  selectedSubjectFilter.value = ''
  selectedContentTypeFilter.value = ''
  selectedKnowledgeTagFilters.value = []
  notesPage.value = 1
}

function prevNotesPage() {
  notesPage.value = Math.max(1, notesPage.value - 1)
}

function nextNotesPage() {
  notesPage.value = Math.min(notesPageState.value.totalPages, notesPage.value + 1)
}

function addNoteDetailTag() {
  if (!selectedNote.value || !noteTagDraft.value.trim()) return
  const nextName = noteTagDraft.value.trim()
  if (selectedNote.value.tags.some((tag) => tag.name === nextName)) {
    noteTagDraft.value = ''
    return
  }
  selectedNote.value = { ...selectedNote.value, tags: [...selectedNote.value.tags, { name: nextName, confidence: 1 }] }
  noteTagDraft.value = ''
}

function removeNoteDetailTag(tagName: string) {
  if (!selectedNote.value) return
  selectedNote.value = { ...selectedNote.value, tags: selectedNote.value.tags.filter((tag) => tag.name !== tagName) }
}

async function saveSelectedNoteTags() {
  if (!accessToken.value || !selectedNote.value) return
  ui.savingNoteTags = true
  try {
    const result = await request<NoteItem>(`/v1/notes/${selectedNote.value.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ tags: selectedNote.value.tags as TagItem[] }),
    })
    const nextNote = decorateNoteItem(result.data)
    selectedNote.value = nextNote
    notes.value = notes.value.map((item) => item.id === nextNote.id ? nextNote : item)
  } finally {
    ui.savingNoteTags = false
  }
}

async function deleteSelectedNote() {
  if (!accessToken.value || !selectedNote.value) return
  ui.deletingNoteId = selectedNote.value.id
  try {
    await request<{ id: string; status: string }>(`/v1/notes/${selectedNote.value.id}`, { method: 'DELETE' })
    const deletedId = selectedNote.value.id
    notes.value = notes.value.filter((item) => item.id !== deletedId)
    selectedNote.value = notes.value[0] ?? null
    activeTab.value = 'notes'
  } finally {
    ui.deletingNoteId = ''
  }
}

watch(() => searchForm.q, () => {
  if (!notesSearchVisible.value) return
  void runSearch()
})

function openNoteDetail(note: NoteItem) {
  selectedNote.value = note
  activeTab.value = 'note-detail'
}

function returnToNotes() {
  activeTab.value = 'notes'
}

function openNoteEdit() {
  activeTab.value = 'note-edit'
}

function returnToNoteDetail() {
  activeTab.value = 'note-detail'
}

function openRelatedNote(noteId: string) {
  const target = notes.value.find((item) => item.id === noteId)
  if (target) openNoteDetail(target)
}

onBeforeUnmount(() => {
  if (askStreamTimer) window.clearInterval(askStreamTimer)
  if (pickedNoteFilePreviewUrl.value) URL.revokeObjectURL(pickedNoteFilePreviewUrl.value)
  if (pickedQuestionFilePreviewUrl.value) URL.revokeObjectURL(pickedQuestionFilePreviewUrl.value)
})
</script>

<template>
  <div class="student-layer-shell">
    <StudentAuthCard v-if="!currentUser" :login-form="loginForm" :logging-in="ui.loggingIn" :login-error="ui.loginError" :on-login="login" />

    <template v-else>
      <StudentWorkspaceHeader :current-user="currentUser" :note-count="notes.length" :graph-node-count="graphNodes.length" :workspace-tabs="workspaceTabs" :active-tab="activeTab" :on-select-tab="(tab) => activeTab = tab" />

      <main class="workspace-main">
        <transition name="fade-scale" mode="out-in">
          <StudentUploadWorkspace v-if="activeTab === 'upload'" :upload-step="uploadStep" :note-upload-form="noteUploadForm" :note-file-input-key="noteFileInputKey" :picked-note-file-name="pickedNoteFileName" :picked-note-file-preview-url="pickedNoteFilePreviewUrl" :upload-preview="uploadPreview" :new-tag-draft="newTagDraft" :previewing-upload="ui.previewingUpload" :confirming-upload="ui.confirmingUpload" :upload-error="ui.uploadError" :upload-success="ui.uploadSuccess" :upload-button-disabled="false" :on-note-file-picked="onNoteFilePicked" :on-note-file-dropped="onNoteFileDropped" :on-preview-note-tags="previewNoteTags" :on-update-preview-tag="updatePreviewTag" :on-remove-preview-tag="removePreviewTag" :on-add-preview-tag="addPreviewTag" :on-return-upload-result-to-form="returnUploadResultToForm" :on-confirm-note-record="confirmNoteRecord" :on-update-new-tag-draft="(value) => newTagDraft = value" />

          <StudentAskWorkspace v-else-if="activeTab === 'ask'" :ask-form="askForm" :ask-state="askAnalysisState" :question-file-input-key="questionFileInputKey" :new-result-tag-draft="askResultTagDraft" :on-question-file-picked="onQuestionFilePicked" :on-question-file-dropped="onQuestionFileDropped" :on-preview-question-file-analysis="previewQuestionFileAnalysis" :on-reset-question-composer="resetQuestionComposer" :on-ask-question="askQuestion" :on-save-question-as-note="saveQuestionAsNote" :on-return-to-ask-step="returnToAskStep" :on-update-result-tag="updateAskResultTag" :on-remove-result-tag="removeAskResultTag" :on-add-result-tag="addAskResultTag" :on-update-new-result-tag-draft="(value) => askResultTagDraft = value" />

          <StudentNotesWorkspace v-else-if="activeTab === 'notes'" :subject-nodes="subjectNodes" :selected-subject-filter="selectedSubjectFilter" :selected-content-type-filter="selectedContentTypeFilter" :selected-knowledge-tag-filters="selectedKnowledgeTagFilters" :content-type-nodes="contentTypeNodes" :visible-tag-nodes="visibleTagNodes" :notes-search-state="notesSearchState" :filtered-notes="filteredNotes" :notes-page-state="notesPageState" :selected-note="selectedNote" :on-apply-subject-filter="applySubjectFilter" :on-apply-content-type-filter="applyContentTypeFilter" :on-toggle-knowledge-tag-filter="toggleKnowledgeTagFilter" :on-clear-tag-filter="clearTagFilter" :on-toggle-search="toggleNotesSearch" :on-update-search-query="updateSearchQuery" :on-pick-search-result="pickSearchResult" :on-select-note="openNoteDetail" :on-prev-page="prevNotesPage" :on-next-page="nextNotesPage" />

          <StudentNoteDetailWorkspace v-else-if="activeTab === 'note-detail'" :note="selectedNote" :related-notes="relatedNotes" :preview-kind="selectedNotePreviewKind" :resolve-asset-url="resolveAssetUrl" :on-download-original-file="downloadSelectedNoteOriginalFile" :on-back="returnToNotes" :on-edit="openNoteEdit" :on-open-related-note="openRelatedNote" />

          <StudentNoteEditWorkspace v-else :note="selectedNote" :tag-draft="noteTagDraft" :saving-note-tags="ui.savingNoteTags" :deleting-note="ui.deletingNoteId === selectedNote?.id" :on-back="returnToNoteDetail" :on-update-tag-draft="(value) => noteTagDraft = value" :on-add-tag="addNoteDetailTag" :on-remove-tag="removeNoteDetailTag" :on-save-tags="saveSelectedNoteTags" :on-delete-note="deleteSelectedNote" />
        </transition>
      </main>
    </template>
  </div>
</template>
