<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
}>()

const searchQuery = ref('');
const loading = ref(false);

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;

  loading.value = true;
  try {
    // Your search logic will go here
    // For demonstration, we'll add a timeout to simulate network request
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Searching for:', searchQuery.value);
    // Additional search logic to be added later
  } catch (error) {
    console.error('Search failed:', error);
  } finally {
    loading.value = false;
  }
};

const handleKeyUp = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleSearch();
  }
};
</script>

<template>
  <div class="flex-1 flex align-items-center">

    <FloatLabel variant="on" class="w-full">
      <InputText id="on_label" v-model="searchQuery" class="w-full p-inputtext-lg" @keyup="handleKeyUp"
        :disabled="loading" />
      <label for=" on_label">Search...</label>
    </FloatLabel>

    <Button icon="pi pi-search" @click="handleSearch" severity="contrast" class="p-button-lg" :loading="loading"
      :disabled="loading || !searchQuery.trim()" raised label="Search">
    </Button>
  </div>
</template>

<style scoped></style>
