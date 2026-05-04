<template>
  <div class="login-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.login-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
</style>