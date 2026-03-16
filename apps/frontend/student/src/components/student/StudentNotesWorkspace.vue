<script setup lang="ts">
import type { PropType } from 'vue'
import type { NoteItem, NotesPageState, NotesSearchState, SearchItem } from '../../types'

defineProps({
  subjectNodes: { type: Array as PropType<Array<{ name: string; count: number; active: boolean }>>, required: true },
  selectedSubjectFilter: { type: String, required: true },
  selectedContentTypeFilter: { type: String, required: true },
  selectedKnowledgeTagFilters: { type: Array as PropType<string[]>, required: true },
  contentTypeNodes: { type: Array as PropType<Array<{ name: string; linked: boolean }>>, required: true },
  visibleTagNodes: { type: Array as PropType<Array<{ name: string; weight: number; linked: boolean }>>, required: true },
  notesSearchState: { type: Object as PropType<NotesSearchState>, required: true },
  filteredNotes: { type: Array as PropType<NoteItem[]>, required: true },
  notesPageState: { type: Object as PropType<NotesPageState>, required: true },
  onApplySubjectFilter: { type: Function as PropType<(subjectName: string) => void>, required: true },
  onApplyContentTypeFilter: { type: Function as PropType<(tagName: string) => void>, required: true },
  onToggleKnowledgeTagFilter: { type: Function as PropType<(tagName: string) => void>, required: true },
  onClearTagFilter: { type: Function as PropType<() => void>, required: true },
  onToggleSearch: { type: Function as PropType<() => void>, required: true },
  onUpdateSearchQuery: { type: Function as PropType<(value: string) => void>, required: true },
  onPickSearchResult: { type: Function as PropType<(item: SearchItem) => void>, required: true },
  onSelectNote: { type: Function as PropType<(note: NoteItem) => void>, required: true },
  onPrevPage: { type: Function as PropType<() => void>, required: true },
  onNextPage: { type: Function as PropType<() => void>, required: true },
})
</script>

<template>
  <section class="card workspace-card notes-management-card">
    <div class="section-head"><h2>笔记管理</h2><span>仅筛选区标签可点击，笔记标题点击后进入详情页。</span></div>
    <div class="notes-search-trigger-row">
      <button class="tab-btn" @click="onToggleSearch">{{ notesSearchState.visible ? '收起搜索' : '搜索笔记' }}</button>
    </div>
    <div v-if="notesSearchState.visible" class="notes-search-panel">
      <div class="section-head compact"><h3>搜索笔记</h3><span>输入后自动模糊检索并定位结果。</span></div>
      <label><span>关键词</span><input :value="notesSearchState.query" type="text" placeholder="输入内容后自动搜索" @input="onUpdateSearchQuery(($event.target as HTMLInputElement).value)" /></label>
      <div v-if="notesSearchState.results.length" class="search-list embedded-search-list">
        <button v-for="item in notesSearchState.results" :key="`${item.type}-${item.id}`" class="search-item search-result-btn" @click="onPickSearchResult(item)"><strong>{{ item.type }} · {{ item.category }} · {{ item.subject }}</strong><p>{{ item.title }}</p><span>{{ item.snippet }}</span></button>
      </div>
    </div>
    <div class="notes-graph-strip">
      <button v-for="node in subjectNodes" :key="node.name" :class="['graph-link-chip', { linked: node.active }]" @click="onApplySubjectFilter(node.name)">{{ node.name }} · {{ node.count }}</button>
      <button v-if="selectedSubjectFilter || selectedContentTypeFilter || selectedKnowledgeTagFilters.length" class="tab-btn" @click="onClearTagFilter">清空筛选</button>
    </div>
    <div v-if="contentTypeNodes.length" class="notes-graph-strip subtag-strip">
      <button v-for="node in contentTypeNodes" :key="node.name" :class="['graph-link-chip', { linked: node.linked }]" @click="onApplyContentTypeFilter(node.name)">{{ node.name }}</button>
    </div>
    <div v-if="selectedSubjectFilter && visibleTagNodes.length" class="notes-graph-strip subtag-strip">
      <button v-for="node in visibleTagNodes" :key="node.name" :class="['graph-link-chip', { linked: node.linked }]" @click="onToggleKnowledgeTagFilter(node.name)">{{ node.name }} · {{ node.weight }}</button>
    </div>
    <div class="notes-management-grid">
      <div class="note-list-pane">
        <article v-for="item in filteredNotes" :key="item.id" class="note-node-card">
          <button class="note-title-btn" @click="onSelectNote(item)">{{ item.title || item.category }}</button>
          <span>{{ item.category }} · {{ item.subject }} · {{ item.parse_status }}</span>
          <div v-if="item.tags.length" class="note-tag-row">
            <span v-for="tag in item.tags" :key="`${item.id}-${tag.name}`" class="pill tag-pill note-static-tag" @click.stop>{{ tag.name }}</span>
          </div>
        </article>
        <div v-if="notesPageState.totalPages > 1" class="notes-pagination-row">
          <button class="tab-btn" :disabled="notesPageState.page <= 1" @click="onPrevPage">上一组</button>
          <span>第 {{ notesPageState.page }} / {{ notesPageState.totalPages }} 组 · 共 {{ notesPageState.total }} 条</span>
          <button class="tab-btn" :disabled="notesPageState.page >= notesPageState.totalPages" @click="onNextPage">下一组</button>
        </div>
      </div>
    </div>
  </section>
</template>
