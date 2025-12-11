<script setup lang="ts">
import { useSearch, type SearchFunction } from '@/composables/useSearch'
import SearchResultItem from './SearchResultItem.vue'

interface Props {
    title: string
    searchFn: SearchFunction
}

const props = defineProps<Props>()

const {
    searchQuery,
    isSearching,
    searchResults,
    collapsedState,
    loadingState,
    contentCache,
    handleSearch,
    onPanelToggle
} = useSearch(props.searchFn)
</script>

<template>
    <div class="search-header">
        <h3>{{ props.title }}</h3>
    </div>
    <div class="input-group">
        <div class="p-inputgroup p-inputgroup-lg">
            <InputText v-model="searchQuery" placeholder="Enter your search query..." :disabled="isSearching"
                @keyup.enter="handleSearch" />
            <Button icon="pi pi-search" label="Search" :loading="isSearching"
                :disabled="isSearching || !searchQuery.trim()" @click="handleSearch" />
        </div>
    </div>

    <div v-if="searchResults.length > 0">
        <SearchResultItem v-for="result in searchResults" :key="result.embedding_id" :result="result"
            :collapsed="collapsedState[result.embedding_id]" :loading-state="loadingState" :content-cache="contentCache"
            @update:collapsed="(v) => onPanelToggle(v, result.embedding_id)" />
    </div>
    <div v-else-if="!isSearching">
        <div style="text-align: center;">
            <i>No results to display</i>
        </div>
    </div>
</template>

<style scoped>
.search-header {
    text-align: center;
    margin-bottom: 1rem;
}

.input-group {
    display: flex;
    justify-content: center;
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
</style>