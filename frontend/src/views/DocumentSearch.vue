<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePopup } from '@/composables/usePopup'
import { searchKnnDocsByQuery, getContentByEmbeddingId } from '@/composables/useAPI'
import type { KnnSearchResult } from '@/composables/useAPI'
import { useRouter } from 'vue-router'

const { showLoading, closePopup, showError } = usePopup()
const router = useRouter()

const searchQuery = ref('')
const isSearching = ref(false)
const searchResults = ref<KnnSearchResult[]>([])
const collapsedState = reactive<Record<number, boolean>>({})
const loadingState = reactive<Record<number, boolean>>({})
const contentCache = reactive<Record<number, string>>({})

const handleSearch = async () => {
  if (!searchQuery.value.trim() || isSearching.value) {
    return;
  }

  isSearching.value = true
  showLoading('Searching...')
  router.replace({ query: { q: searchQuery.value } })

  searchKnnDocsByQuery(searchQuery.value, 20)
    .then(results => {
      searchResults.value = results

      results.forEach(result => {
        if (collapsedState[result.embedding_id] === undefined) {
          collapsedState[result.embedding_id] = true
        }
      })
      closePopup()
    })
    .catch(err => {
      searchResults.value = []
      const msg = err instanceof Error ? err.message : String(err)
      showError('Search failed', msg, true)
    })
    .finally(() => {
      isSearching.value = false
    })
}

const onPanelToggle = (isCollapsed: boolean, embeddingId: number) => {
  if (isCollapsed || contentCache[embeddingId] !== undefined || loadingState[embeddingId]) {
    return;
  }

  loadingState[embeddingId] = true
  getContentByEmbeddingId(embeddingId)
    .then(content => {
      contentCache[embeddingId] = content.section || '<N/A>'
    })
    .catch(err => {
      const msg = err instanceof Error ? err.message : String(err)
      showError('Load content failed', msg, true)
      contentCache[embeddingId] = '<Error: Could not load content>'
    })
    .finally(() => {
      loadingState[embeddingId] = false
    })

}

const getFileName = (uri: string = '') => {
  try {
    return decodeURIComponent(uri.split('/').pop() || uri)
  } catch {
    return uri
  }
}

const formatDate = (dateString?: string) => {
  if (!dateString) return 'No date'
  return dateString.split('T')[0]
}

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const q = params.get('q')
  if (q) {
    searchQuery.value = q
    handleSearch()
  }
})
</script>

<template>
  <div style="text-align: center; margin-bottom: 1rem;">
    <h3>Search Documents</h3>
  </div>
  <div class="input-group">
    <div class="p-inputgroup p-inputgroup-lg">
      <InputText v-model="searchQuery" placeholder="Enter your search query..." :disabled="isSearching"
        @keyup.enter="handleSearch" />
      <Button icon="pi pi-search" label="Search" :loading="isSearching" :disabled="isSearching || !searchQuery.trim()"
        @click="handleSearch" />
    </div>
  </div>

  <div v-if="searchResults.length > 0">
    <Panel class="result-item" v-for="result in searchResults" :key="result.embedding_id"
      v-model:collapsed="collapsedState[result.embedding_id]" toggleable
      @update:collapsed="isCollapsed => onPanelToggle(isCollapsed, result.embedding_id)">
      <template #header>
        <div class="header-content">
          {{ getFileName(result.source?.uri) }}
        </div>
        <div class="similarity-container">
          <small>{{ (result.similarity * 100).toFixed(1) }}% Match</small>
          <ProgressBar :value="result.similarity * 100" :show-value="false" style="height: 6px;"></ProgressBar>
          <small>{{ formatDate(result.source?.last_modified) }}</small>
        </div>
      </template>

      <div v-if="loadingState[result.embedding_id]" class="loading-container">
        <ProgressSpinner style="width: 30px; height: 30px" strokeWidth="6" />
      </div>
      <div v-else class="content-preview">
        {{ contentCache[result.embedding_id] }}
      </div>
    </Panel>
  </div>
  <div v-else-if="!isSearching">
    <div style="text-align: center;">
      <i>No results to display</i>
    </div>
  </div>
</template>

<style scoped>
.input-group {
  display: flex;
  justify-content: center;
}

.result-item {
  margin-bottom: 0.2rem;
  border: 0;
}

.p-inputgroup.p-inputgroup-lg {
  display: flex;
  justify-content: center;
  width: 100%;
  max-width: 700px;
  margin-bottom: 1rem;
}

.p-inputgroup .p-inputtext {
  font-size: 1.25rem;
  border-radius: 5px 0 0 5px;
  width: 100%;
  padding: .5em 1.5rem;
}

.p-inputgroup .p-button {
  font-size: 1.25rem;
  border-radius: 0 5px 5px 0;
  padding: .5em 1.5rem;
}

.header-content {
  flex-grow: 1;
  font-weight: 600;
}

.similarity-container {
  flex-shrink: 0;
  width: 80px;
  text-align: left;
  margin: 0 0.5rem 0 1rem;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

.content-preview {
  padding: .5rem;
  font-size: 0.9rem;
  font-style: italic;
}
</style>
