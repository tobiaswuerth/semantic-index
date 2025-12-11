import { ref, reactive, onMounted } from 'vue'
import { usePopup } from '@/composables/usePopup'
import { getContentByEmbeddingId } from '@/composables/useAPI'
import type { KnnSearchResult } from '@/composables/useAPI'
import { useRouter } from 'vue-router'

export type SearchFunction = (query: string, limit: number) => Promise<KnnSearchResult[]>

export function useSearch(searchFn: SearchFunction, limit: number = 20) {
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
            return
        }

        isSearching.value = true
        showLoading('Searching...')
        router.replace({ query: { q: searchQuery.value } })

        searchFn(searchQuery.value, limit)
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
            return
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

    onMounted(() => {
        const params = new URLSearchParams(window.location.search)
        const q = params.get('q')
        if (q) {
            searchQuery.value = q
            handleSearch()
        }
    })

    return {
        searchQuery,
        isSearching,
        searchResults,
        collapsedState,
        loadingState,
        contentCache,
        handleSearch,
        onPanelToggle
    }
}
