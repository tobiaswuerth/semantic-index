<script setup lang="ts">
import Toast from 'primevue/toast'
import AppHeader from '@/components/AppToolbar.vue'
import StatusPopup from '@/components/StatusPopup.vue';

</script>

<template>
  <Toast />
  <StatusPopup />

  <main>
    <AppHeader />
    <RouterView />
  </main>

</template>

<style scoped></style>
