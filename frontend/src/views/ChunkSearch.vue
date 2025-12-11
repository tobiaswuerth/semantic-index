<script setup lang="ts">
import { searchKnnChunksByQuery } from '@/composables/useAPI'
import SearchResultList from '@/components/SearchResultList.vue'
</script>

<template>
  <SearchResultList title="Search Chunks" :search-fn="searchKnnChunksByQuery" />
</template>
