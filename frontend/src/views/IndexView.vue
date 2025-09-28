<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePopup } from '@/composables/usePopup'

interface Source {
  id: number
  uri: string
  last_modified: string
  last_processed: string | null
  error: number
  error_message: string | null
}

interface KnnSearchResult {
  embedding_id: number
  similarity: number
  source: Source
}

function useContentLoader() {
  const loadingState = reactive<Record<number, boolean>>({})
  const contentCache = reactive<Record<number, string>>({})
  const { showError } = usePopup()

  const isLoading = (id: number) => !!loadingState[id]
  const getContent = (id: number) => contentCache[id] || ''

  async function loadContent(embeddingId: number) {
    if (contentCache[embeddingId] || loadingState[embeddingId]) {
      return
    }

    loadingState[embeddingId] = true
    try {
      const resp = await fetch(`${BASE_API}/api/read_content_by_embedding_id/${embeddingId}`)
      if (!resp.ok) {
        throw new Error((await resp.text()) || `Failed to load content: ${resp.status}`)
      }
      const data = await resp.json()
      contentCache[embeddingId] = data.section || 'Content is not available or empty.'
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      showError('Load content failed', msg, true)
      contentCache[embeddingId] = 'Error: Could not load content.'
    } finally {
      loadingState[embeddingId] = false
    }
  }

  return { isLoading, getContent, loadContent }
}

const { showLoading, closePopup, showError } = usePopup()
const { isLoading: isContentLoading, getContent, loadContent } = useContentLoader()

const BASE_API = 'http://localhost:5000'
const limit = 10

const searchQuery = ref('')
const searchResults = ref<KnnSearchResult[]>([])
const collapsedState = reactive<Record<number, boolean>>({})
const isSearching = ref(false)
const hasSearched = ref(false)

const handleSearch = async () => {
  if (!searchQuery.value.trim() || isSearching.value) return

  isSearching.value = true
  hasSearched.value = true
  showLoading('Searching...')
  // add to url
  window.history.replaceState(null, '', `?q=${encodeURIComponent(searchQuery.value)}`)

  try {
    const resp = await fetch(`${BASE_API}/api/search_knn_by_query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: searchQuery.value, limit }),
    })

    if (!resp.ok) {
      throw new Error((await resp.text()) || `Search failed: ${resp.status}`)
    }

    const results: KnnSearchResult[] = await resp.json() || []
    searchResults.value = results

    results.forEach(result => {
      if (collapsedState[result.embedding_id] === undefined) {
        collapsedState[result.embedding_id] = true
      }
    })

  } catch (err: unknown) {
    searchResults.value = []
    const msg = err instanceof Error ? err.message : String(err)
    showError('Search failed', msg)
  } finally {
    isSearching.value = false
    closePopup()
  }
}

const onPanelToggle = (isCollapsed: boolean, embeddingId: number) => {
  if (!isCollapsed) {
    loadContent(embeddingId)
  }
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

      <div v-if="isContentLoading(result.embedding_id)" class="loading-container">
        <ProgressSpinner style="width: 30px; height: 30px" strokeWidth="6" />
      </div>
      <div v-else class="content-preview">
        {{ getContent(result.embedding_id) }}
      </div>
    </Panel>
  </div>
  <div v-else-if="hasSearched && !isSearching">
    <div style="text-align: center;">
      <i>No results found for your query</i>
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
