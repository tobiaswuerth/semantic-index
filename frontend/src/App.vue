<script setup lang="ts">
import Home from './components/Home.vue'
import ErrorOverlay from './components/ErrorOverlay.vue'
</script>

<template>
  <ErrorOverlay />
  <div class="m-5 p-5 rounded-lg" style="background-color: var(--p-stone-50);">
    <div class="flex items-center mb-4 pb-3" style="border-bottom: 1px solid var(--p-stone-200);">
      <img src="/icon.svg" alt="Logo" height="50" class="mr-0 pr-0" />
      <h1 class="text-4xl font-bold text-gray-800 m-0 pl-0">emantic Index</h1>
    </div>
    <Home />
  </div>
</template>

<style scoped></style>
