<script setup lang="ts">
import type { PropType } from 'vue'
import type { NoteItem } from '../../types'

defineProps({
  note: { type: Object as PropType<NoteItem | null>, required: true },
  tagDraft: { type: String, required: true },
  savingNoteTags: { type: Boolean, required: true },
  deletingNote: { type: Boolean, required: true },
  onBack: { type: Function as PropType<() => void>, required: true },
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
      <button class="tab-btn" @click="onBack">返回笔记详情</button>
    </div>

    <div v-if="note" class="note-detail-pane standalone-detail-pane">
      <div class="note-detail-head">
        <div>
          <strong>编辑 {{ note.title || '未命名笔记' }}</strong>
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
    </div>
  </section>
</template>
