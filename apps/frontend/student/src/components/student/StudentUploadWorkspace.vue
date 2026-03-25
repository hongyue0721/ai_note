<script setup lang="ts">
import type { PropType } from 'vue'
import type { UploadPreview, UploadStep } from '../../types'

const props = defineProps({
  uploadStep: { type: String as PropType<UploadStep>, required: true },
  noteUploadForm: { type: Object as PropType<{ filename: string; mimeType: string; fileKind: string; contentType: string; textContent: string }>, required: true },
  noteFileInputKey: { type: Number, required: true },
  pickedNoteFileName: { type: String, required: true },
  pickedNoteFilePreviewUrl: { type: String, required: true },
  uploadPreview: { type: Object as PropType<UploadPreview | null>, required: true },
  newTagDraft: { type: String, required: true },
  previewingUpload: { type: Boolean, required: true },
  confirmingUpload: { type: Boolean, required: true },
  uploadError: { type: String, required: true },
  uploadSuccess: { type: String, required: true },
  onNoteFilePicked: { type: Function as PropType<(event: Event) => void>, required: true },
  onNoteFileDropped: { type: Function as PropType<(file: File) => void>, required: true },
  onPreviewNoteTags: { type: Function as PropType<() => void>, required: true },
  onUpdatePreviewTag: { type: Function as PropType<(index: number, value: string) => void>, required: true },
  onRemovePreviewTag: { type: Function as PropType<(index: number) => void>, required: true },
  onAddPreviewTag: { type: Function as PropType<() => void>, required: true },
  onReturnUploadResultToForm: { type: Function as PropType<() => void>, required: true },
  onConfirmNoteRecord: { type: Function as PropType<() => void>, required: true },
  onUpdateNewTagDraft: { type: Function as PropType<(value: string) => void>, required: true },
  uploadButtonDisabled: { type: Boolean, required: true },
})

function extractDroppedFile(event: DragEvent) {
  const items = event.dataTransfer?.items
  if (items?.length) {
    for (const item of Array.from(items)) {
      if (item.kind !== 'file') continue
      const file = item.getAsFile()
      if (file) return file
    }
  }
  return event.dataTransfer?.files?.[0] ?? null
}

function handleNoteDrop(event: DragEvent) {
  const file = extractDroppedFile(event)
  if (file) props.onNoteFileDropped(file)
}
</script>

<template>
  <section class="card workspace-card">
    <div class="section-head"><h2>上传笔记</h2><span>支持图片与文件；用户先选笔记/资料/错题，再交给 AI 分类。</span></div>

    <template v-if="uploadStep === 'form'">
      <div class="composer-card upload-composer-card">
        <div class="composer-toolbar">
          <label class="inline-select-field">
            <span>内容类型</span>
            <select v-model="noteUploadForm.contentType">
              <option value="note">笔记</option>
              <option value="document">资料</option>
              <option value="problem">错题</option>
            </select>
          </label>
        </div>
        <label class="composer-textarea-wrap drop-textarea-wrap" @dragover.prevent @drop.prevent="handleNoteDrop">
          <span>文本内容</span>
          <textarea v-model="noteUploadForm.textContent" rows="8" placeholder="可直接粘贴笔记内容，或把文件拖到这里。" />
          <label class="composer-upload-icon-btn" :class="{ disabled: uploadButtonDisabled }" :title="uploadButtonDisabled ? '上传文件不可用' : (pickedNoteFileName ? '更换文件' : '上传文件')">
            <input :key="noteFileInputKey" :disabled="uploadButtonDisabled" type="file" @change="onNoteFilePicked" />
            <span>⤴</span>
          </label>
        </label>
        <div class="composer-support-row">
          <label class="support-input-field grow-field">
            <span>文件名 / 标题</span>
            <input v-model="noteUploadForm.filename" type="text" placeholder="可选；不填则默认使用上传文件名" />
          </label>
          <div v-if="pickedNoteFileName" class="picked-file-pill">已附加：{{ pickedNoteFileName }}</div>
        </div>
        <div v-if="pickedNoteFilePreviewUrl" class="file-preview-media compact-preview"><img :src="pickedNoteFilePreviewUrl" alt="note preview" /></div>
      </div>
      <button class="primary-btn" :disabled="previewingUpload" @click="onPreviewNoteTags">{{ previewingUpload ? '识别中...' : '开始识别并展示分类结果' }}</button>
    </template>

    <template v-else-if="uploadPreview">
      <div class="upload-confirm-page fade-page">
        <div class="section-head compact"><h3>分类结果确认页</h3><span>可修改标题、大类、小标签和摘要后再保存。</span></div>
        <div class="dual-grid">
          <label><span>题目 / 原文件名</span><input v-model="uploadPreview.title" type="text" /></label>
          <label><span>大类（科目）</span><input v-model="uploadPreview.subject" type="text" /></label>
        </div>
        <label><span>AI摘要</span><textarea v-model="uploadPreview.summary" rows="3" /></label>
        <label><span>正文 / 概括</span><textarea v-model="noteUploadForm.textContent" rows="6" /></label>

        <div class="section-head compact"><h3>小标签</h3><span>每个标签可单独删除，也可新增。</span></div>
        <div class="editable-tag-grid">
          <div v-for="(tag, index) in uploadPreview.knowledge_candidates" :key="`${index}-${tag.name}`" class="editable-tag-item">
            <input :value="tag.name" type="text" @input="onUpdatePreviewTag(index, ($event.target as HTMLInputElement).value)" />
            <small>{{ Math.round(tag.confidence * 100) }}%</small>
            <button class="mini-danger-btn" @click="onRemovePreviewTag(index)">×</button>
          </div>
        </div>
        <div class="tag-add-row">
          <input :value="newTagDraft" type="text" placeholder="新增小标签" @input="onUpdateNewTagDraft(($event.target as HTMLInputElement).value)" />
          <button class="tab-btn" @click="onAddPreviewTag">添加标签</button>
        </div>

        <div class="result-actions">
          <button class="tab-btn" @click="onReturnUploadResultToForm">返回重新识别</button>
          <button class="primary-btn" :disabled="confirmingUpload" @click="onConfirmNoteRecord">{{ confirmingUpload ? '确认中...' : '确认保存到笔记' }}</button>
        </div>
      </div>
    </template>

    <p v-if="uploadError" class="error-text">{{ uploadError }}</p>
    <p v-if="uploadSuccess" class="success-text">{{ uploadSuccess }}</p>
  </section>
</template>
