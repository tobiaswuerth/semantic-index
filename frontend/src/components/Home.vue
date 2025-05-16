<script setup lang="ts">
import { ref, inject } from 'vue'
import { semanticSearch } from '../services/repository'

const showError = inject('showError')
console.log(showError)

const searchQuery = ref('');
const loading = ref(false);

const handleSearch = () => {
  if (!searchQuery.value.trim()) return;

  loading.value = true;
  semanticSearch(searchQuery.value, 5)
    .then(results => {
      console.log('Semantic search results:', results);
    })
    .catch(error => {
      showError(`Error during search: ${error.message}`);
    })
    .finally(() => {
      loading.value = false;
    });
};

const handleKeyUp = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleSearch();
  }
};
</script>

<template>
  <InputGroup>
    <FloatLabel variant="on" class="w-full">
      <InputText id="on_label" v-model="searchQuery" class="w-full p-inputtext-lg" @keyup="handleKeyUp"
        :disabled="loading" />
      <label for=" on_label">Search...</label>
    </FloatLabel>

    <Button icon="pi pi-search" @click="handleSearch" severity="contrast" class="p-button-lg" :loading="loading"
      :disabled="loading || !searchQuery.trim()" raised label="Search">
    </Button>
  </InputGroup>
</template>

<style scoped></style>
