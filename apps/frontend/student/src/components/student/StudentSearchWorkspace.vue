<script setup lang="ts">
import type { PropType } from 'vue'
import type { SearchItem } from '../../types'

defineProps({
  searchForm: { type: Object as PropType<{ q: string }>, required: true },
  searchResults: { type: Array as PropType<SearchItem[]>, required: true },
  onRunSearch: { type: Function as PropType<() => void>, required: true },
  onPickSearchResult: { type: Function as PropType<(item: SearchItem) => void>, required: true },
})
</script>

<template>
  <section class="card workspace-card">
    <div class="section-head"><h2>搜索</h2><span>搜索结果会直接联动到笔记管理面板。</span></div>
    <div class="dual-grid">
      <label><span>关键词</span><input v-model="searchForm.q" type="text" /></label>
      <div class="search-action-wrap"><button class="primary-btn" @click="onRunSearch">执行搜索</button></div>
    </div>
    <div v-if="searchResults.length" class="search-list">
      <button v-for="item in searchResults" :key="`${item.type}-${item.id}`" class="search-item search-result-btn" @click="onPickSearchResult(item)"><strong>{{ item.type }} · {{ item.category }} · {{ item.subject }}</strong><p>{{ item.title }}</p><span>{{ item.snippet }}</span></button>
    </div>
    <div v-else class="empty-card">先输入关键词执行搜索。</div>
  </section>
</template>
