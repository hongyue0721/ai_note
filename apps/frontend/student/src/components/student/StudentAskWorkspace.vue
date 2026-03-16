<script setup lang="ts">
import type { PropType } from 'vue'
import type { AskAnalysisState } from '../../types'

const props = defineProps({
  askForm: { type: Object as PropType<{ questionText: string }>, required: true },
  askState: { type: Object as PropType<AskAnalysisState>, required: true },
  questionFileInputKey: { type: Number, required: true },
  onQuestionFilePicked: { type: Function as PropType<(event: Event) => void>, required: true },
  onQuestionFileDropped: { type: Function as PropType<(file: File) => void>, required: true },
  onPreviewQuestionFileAnalysis: { type: Function as PropType<() => void>, required: true },
  onResetQuestionComposer: { type: Function as PropType<() => void>, required: true },
  onAskQuestion: { type: Function as PropType<() => void>, required: true },
  onSaveQuestionAsNote: { type: Function as PropType<() => void>, required: true },
  onReturnToAskStep: { type: Function as PropType<() => void>, required: true },
  onUpdateResultTag: { type: Function as PropType<(index: number, value: string) => void>, required: true },
  onRemoveResultTag: { type: Function as PropType<(index: number) => void>, required: true },
  onAddResultTag: { type: Function as PropType<() => void>, required: true },
  newResultTagDraft: { type: String, required: true },
  onUpdateNewResultTagDraft: { type: Function as PropType<(value: string) => void>, required: true },
})

function handleQuestionDrop(event: DragEvent) {
  const file = event.dataTransfer?.files?.[0]
  if (file) props.onQuestionFileDropped(file)
}
</script>

<template>
  <section class="card workspace-card">
    <div class="section-head"><h2>询问问题</h2><span>支持文本提问，也支持上传图片或文档，将文本与文件解析结果合并后生成答案。</span></div>
    <div class="composer-card ask-composer-card">
      <div class="composer-toolbar ask-toolbar">
        <span class="composer-badge">统一提问框</span>
      </div>
      <label class="composer-textarea-wrap drop-textarea-wrap" @dragover.prevent @drop.prevent="handleQuestionDrop">
        <span>问题文本</span>
        <textarea v-model="askForm.questionText" rows="5" placeholder="请输入问题" />
        <label class="composer-upload-icon-btn" :class="{ disabled: askState.uploadButtonDisabled }" :title="askState.uploadButtonDisabled ? '上传文件不可用' : (askState.pickedFileName ? '更换文件' : '上传文件')">
          <input :key="questionFileInputKey" :disabled="askState.uploadButtonDisabled" type="file" accept="image/*,.pdf,.txt,.doc,.docx,application/pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" @change="onQuestionFilePicked" />
          <span>⤴</span>
        </label>
      </label>
      <div v-if="askState.pickedFileName" class="picked-file-pill">已附加：{{ askState.pickedFileName }}</div>
    </div>
    <div v-if="askState.pickedFilePreviewUrl" class="file-preview-media compact-preview"><img :src="askState.pickedFilePreviewUrl" alt="question preview" /></div>
    <div v-else-if="askState.pickedFileName" class="detail-box"><strong>已选择文件</strong><p>{{ askState.pickedFileName }}</p></div>
    <div v-if="askState.preview && !askState.streamedMarkdown" class="question-tag-strip"><span v-for="tag in askState.preview.knowledge_candidates" :key="tag.name" class="pill">{{ tag.name }}</span></div>
    <div v-if="askState.preview" class="detail-box"><strong>文件解析摘要</strong><p>{{ askState.preview.summary || askState.preview.normalized_text || '暂无摘要' }}</p></div>
    <div v-if="!askState.streamedMarkdown" class="result-actions">
      <button class="tab-btn" @click="onResetQuestionComposer">清空当前提问</button>
      <button class="primary-btn" :disabled="askState.solvingQuestion" @click="onAskQuestion">{{ askState.solvingQuestion ? '生成中...' : '提交问题并生成答案' }}</button>
    </div>
    <p v-if="askState.questionError" class="error-text">{{ askState.questionError }}</p>
    <div v-if="askState.streamedMarkdown" class="detail-box solve-box markdown-answer-box fade-page">
      <pre>{{ askState.streamedMarkdown }}</pre>
    </div>
    <div v-if="askState.streamedMarkdown" class="detail-box note-tags-editor">
      <strong>结果标签</strong>
      <div v-if="askState.resultTags.length" class="note-tag-row editable-note-tag-row">
        <span v-for="(tag, index) in askState.resultTags" :key="`${tag.name}-${index}`" class="pill tag-pill editable-tag-pill">
          <input :value="tag.name" type="text" @input="onUpdateResultTag(index, ($event.target as HTMLInputElement).value)" />
          <button class="mini-danger-btn" @click="onRemoveResultTag(index)">×</button>
        </span>
      </div>
      <div class="tag-add-row compact-tag-editor-row">
        <input :value="newResultTagDraft" type="text" placeholder="新增结果标签" @input="onUpdateNewResultTagDraft(($event.target as HTMLInputElement).value)" />
        <button class="tab-btn" @click="onAddResultTag">添加标签</button>
      </div>
    </div>
    <div v-if="askState.streamedMarkdown" class="result-actions">
      <button class="tab-btn" @click="onReturnToAskStep">返回上一级继续询问问题</button>
      <button class="primary-btn" :disabled="askState.savingQuestionNote" @click="onSaveQuestionAsNote">{{ askState.savingQuestionNote ? '加入中...' : '加入笔记' }}</button>
    </div>
  </section>
</template>
