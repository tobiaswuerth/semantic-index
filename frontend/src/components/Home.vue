<script setup lang="ts">
import { ref } from 'vue'
import { semanticSearch, KnnSearchResult, Source } from '../services/repository'
import { showError } from '../services/error-handling';

const searchQuery = ref('');
const loading = ref(false);
const searchResults = ref<KnnSearchResult[]>([]);

const handleSearch = () => {
  if (!searchQuery.value.trim()) return;

  loading.value = true;
  searchResults.value = []; // Clear previous results

  semanticSearch(searchQuery.value, 5)
    .then(results => {
      console.log('Semantic search results:', results);
      searchResults.value = results;
    })
    .catch(showError)
    .finally(() => {
      loading.value = false;
    });
};

const handleKeyUp = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleSearch();
  }
};

const getColorClass = (similarity: number): string => {
  if (similarity > 0.75) return 'bg-green-500';
  if (similarity > 0.5) return 'bg-yellow-500';
  return 'bg-red-500';
};

const getFileName = (uri: string): string => {
  try {
    // Extract filename from URI
    return decodeURIComponent(uri.split('/').pop() || uri);
  } catch (e) {
    return uri;
  }
};
</script>

<template>
  <div class="flex flex-column gap-4 w-full">
    <InputGroup>
      <FloatLabel variant="on" class="w-full">
        <InputText id="on_label" v-model="searchQuery" class="w-full p-inputtext-lg" @keyup="handleKeyUp"
          :disabled="loading" />
        <label for="on_label">Search...</label>
      </FloatLabel>

      <Button icon="pi pi-search" @click="handleSearch" severity="contrast" class="p-button-lg" :loading="loading"
        :disabled="loading || !searchQuery.trim()" raised label="Search">
      </Button>
    </InputGroup>

    <!-- Search Results Section -->
    <div v-if="searchResults && searchResults.length > 0" class="search-results w-full">
      <h2>Search Results</h2>
      <div class="results-list">
        <div v-for="(result, index) in searchResults" :key="result?.source?.id || index" class="result-item">
          <div class="flex align-items-center justify-content-between p-3 border-round cursor-pointer hover:surface-200"
            style="border-bottom: 1px solid var(--p-stone-200);">
            <div class="flex-grow-1">
              <small class="text-color-secondary">
                {{ result?.source?.last_modified?.split('T')[0] || '<no date>' }}
              </small>
              <h3 class="m-0 text-lg">{{ result?.source?.uri ? getFileName(result.source.uri) : 'Unknown File' }}</h3>
              <small class="text-color-secondary">
                {{ result?.source?.uri || 'No URI available' }}
              </small>
            </div>

            <div class="flex align-items-center gap-2">
              <div class="progress-container" style="width: 100px;">
                <div class="progress-bar" :class="getColorClass(result?.similarity)"
                  :style="{ width: `${result?.similarity * 100}%` }"></div>
              </div>
              <span>{{ (result?.similarity * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.progress-container {
  background-color: #f0f0f0;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.result-item {
  margin-bottom: 0.5rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
}

.search-results {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
