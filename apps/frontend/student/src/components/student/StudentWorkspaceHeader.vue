<script setup lang="ts">
import type { PropType } from 'vue'
import type { UserProfile, WorkspaceTab } from '../../types'

defineProps({
  currentUser: { type: Object as PropType<UserProfile>, required: true },
  noteCount: { type: Number, required: true },
  graphNodeCount: { type: Number, required: true },
  workspaceTabs: { type: Array as PropType<Array<{ key: WorkspaceTab; label: string }>>, required: true },
  activeTab: { type: String as PropType<WorkspaceTab>, required: true },
  onSelectTab: { type: Function as PropType<(tab: WorkspaceTab) => void>, required: true },
})
</script>

<template>
  <div>
    <section class="workspace-topbar">
      <div class="workspace-topbar-user">{{ currentUser.space_key }}</div>
      <div class="workspace-topbar-metrics">
        <div class="topbar-metric">
          <strong>{{ graphNodeCount }}</strong>
          <span>知识点候选</span>
        </div>
        <div class="topbar-metric">
          <strong>{{ noteCount }}</strong>
          <span>我的笔记</span>
        </div>
      </div>
    </section>

    <section class="workspace-tabs">
      <button v-for="tab in workspaceTabs" :key="tab.key" :class="['tab-btn', { active: activeTab === tab.key }]" @click="onSelectTab(tab.key)">{{ tab.label }}</button>
    </section>
  </div>
</template>
