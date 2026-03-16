<script setup lang="ts">
import type { PropType } from 'vue'

defineProps({
  loginForm: { type: Object as PropType<{ spaceKey: string }>, required: true },
  loggingIn: { type: Boolean, required: true },
  loginError: { type: String, required: true },
  onLogin: { type: Function as PropType<() => void>, required: true },
})
</script>

<template>
  <section class="auth-layer">
    <div class="auth-card">
      <p>输入输入任意字符串，进入属于你的空间。</p>
      <label><span>鉴权密钥</span><input v-model="loginForm.spaceKey" type="text" placeholder="" /></label>
      <button class="primary-btn" :disabled="loggingIn" @click="onLogin">{{ loggingIn ? '进入中...' : '进入学习工作台' }}</button>
      <p v-if="loginError" class="error-text">{{ loginError }}</p>
    </div>
  </section>
</template>
