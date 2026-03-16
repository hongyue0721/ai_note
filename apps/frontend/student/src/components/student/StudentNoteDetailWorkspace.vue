<script setup lang="ts">
import type { PropType } from 'vue'
import type { NoteItem, RelatedNoteItem } from '../../types'

defineProps({
  note: { type: Object as PropType<NoteItem | null>, required: true },
  relatedNotes: { type: Array as PropType<RelatedNoteItem[]>, required: true },
  tagDraft: { type: String, required: true },
  savingNoteTags: { type: Boolean, required: true },
  deletingNote: { type: Boolean, required: true },
  previewKind: { type: String as PropType<'text' | 'image' | 'pdf' | 'file'>, required: true },
  resolveAssetUrl: { type: Function as PropType<(url: string | null | undefined) => string>, required: true },
  onDownloadOriginalFile: { type: Function as PropType<() => void>, required: true },
  onBack: { type: Function as PropType<() => void>, required: true },
  onOpenRelatedNote: { type: Function as PropType<(noteId: string) => void>, required: true },
  onUpdateTagDraft: { type: Function as PropType<(value: string) => void>, required: true },
  onAddTag: { type: Function as PropType<() => void>, required: true },
  onRemoveTag: { type: Function as PropType<(tagName: string) => void>, required: true },
  onSaveTags: { type: Function as PropType<() => void>, required: true },
  onDeleteNote: { type: Function as PropType<() => void>, required: true },
})
</script>

<template>
  <section class="card workspace-card note-detail-page fade-page">
    <div class="note-detail-page-head">
      <button class="tab-btn" @click="onBack">返回笔记管理</button>
    </div>
    <div v-if="note" class="note-detail-pane standalone-detail-pane">
      <div class="note-detail-head">
        <div>
          <strong>{{ note.title || '未命名笔记' }}</strong>
          <span>{{ note.category }} · {{ note.subject }} · {{ note.parse_status }}</span>
        </div>
        <button class="danger-btn" :disabled="deletingNote" @click="onDeleteNote">{{ deletingNote ? '删除中...' : '删除笔记' }}</button>
      </div>

      <div class="detail-box note-tags-editor">
        <strong>标签编辑</strong>
        <div v-if="note.tags.length" class="note-tag-row editable-note-tag-row">
          <span v-for="tag in note.tags" :key="`${note.id}-${tag.name}`" class="pill tag-pill editable-tag-pill">
            {{ tag.name }}
            <button class="mini-danger-btn" @click="onRemoveTag(tag.name)">×</button>
          </span>
        </div>
        <div class="tag-add-row compact-tag-editor-row">
          <input :value="tagDraft" type="text" placeholder="新增标签，如：数学 / 错题" @input="onUpdateTagDraft(($event.target as HTMLInputElement).value)" />
          <button class="tab-btn" @click="onAddTag">添加标签</button>
          <button class="primary-btn" :disabled="savingNoteTags" @click="onSaveTags">{{ savingNoteTags ? '保存中...' : '保存标签' }}</button>
        </div>
      </div>

      <div v-if="previewKind === 'image' && note.file_url" class="note-preview-card"><img :src="resolveAssetUrl(note.file_url)" alt="note image preview" /></div>
      <div v-else-if="previewKind === 'pdf' && note.file_url" class="note-preview-card pdf-preview"><iframe :src="resolveAssetUrl(note.file_url)" title="pdf preview" /></div>
      <div v-else-if="note.file_url" class="note-preview-card file-preview-link"><strong>{{ note.original_filename || '原文件' }}</strong><a :href="resolveAssetUrl(note.file_url)" target="_blank" rel="noreferrer">打开文件详情</a></div>

      <div class="detail-box note-raw-box">
        <div class="note-raw-box-head">
          <strong>原文</strong>
          <button v-if="note.file_url" class="tab-btn" @click="onDownloadOriginalFile">下载原文件</button>
        </div>
        <p>{{ note.raw_text || '暂无原文内容。' }}</p>
      </div>

      <div class="related-notes-panel">
        <div class="section-head compact"><h3>相关联笔记</h3><span>基于标题、科目和知识点关联推荐。</span></div>
        <div v-if="relatedNotes.length" class="related-note-list">
          <button v-for="item in relatedNotes" :key="item.id" class="search-item search-result-btn" @click="onOpenRelatedNote(item.id)">
            <strong>{{ item.title }}</strong>
            <span>{{ item.subject }} · {{ item.reason }}</span>
          </button>
        </div>
        <div v-else class="empty-card">暂无关联笔记。</div>
      </div>
    </div>
  </section>
</template>
