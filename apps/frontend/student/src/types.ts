export type UserProfile = { id: string; space_key: string; username: string; email?: string | null; status: string }
export type ApiResponse<T> = { code: number; message: string; data: T }
export type TagItem = { name: string; confidence: number }
export type NotesPageState = { page: number; pageSize: number; total: number; totalPages: number }

export type NoteItem = {
  id: string
  title?: string | null
  subject: string
  category: string
  parse_status: string
  raw_text?: string | null
  file_url?: string | null
  original_filename?: string | null
  mime_type?: string | null
  file_kind?: string | null
  tags: TagItem[]
  created_at: string
}

export type SearchItem = {
  type: string
  id: string
  title: string
  snippet: string
  subject: string
  category: string
  parse_status: string
}

export type GraphOverview = {
  nodes: Array<{ name: string; weight: number }>
  total_problems: number
  total_notes: number
}

export type SolveResult = {
  subject: string
  question_type: string
  final_answer: string
  solution_steps: string[]
  knowledge_points: string[]
  confidence: number
  warnings: string[]
  model: string
}

export type UploadPreview = {
  entity_type: string
  content_category: string
  subject: string
  title: string
  summary: string
  normalized_text: string
  knowledge_candidates: TagItem[]
  confidence: number
  needs_review: boolean
  review_reason?: string | null
}

export type WorkspaceTab = 'upload' | 'ask' | 'notes' | 'note-detail' | 'note-edit'
export type UploadStep = 'form' | 'confirm'

export type AskAnalysisState = {
  pickedFileName: string
  pickedFilePreviewUrl: string
  preview: UploadPreview | null
  solveResult: SolveResult | null
  streamedMarkdown: string
   resultTags: TagItem[]
  questionError: string
  solvingQuestion: boolean
  savingQuestionNote: boolean
  uploadButtonDisabled: boolean
}

export type NotesSearchState = {
  visible: boolean
  query: string
  results: SearchItem[]
}

export type RelatedNoteItem = {
  id: string
  title: string
  subject: string
  reason: string
}
