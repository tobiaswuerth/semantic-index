<script setup lang="ts">
import { searchKnnDocsByQuery } from '@/composables/useAPI'
import SearchResultList from '@/components/SearchResultList.vue'
</script>

<template>
  <SearchResultList title="Search Documents" :search-fn="searchKnnDocsByQuery" />
</template>
