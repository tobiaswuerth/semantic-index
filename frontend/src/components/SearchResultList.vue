<script setup lang="ts">
import { useSearch, type SearchFunction } from '@/composables/useSearch'
import SearchResultItem from './SearchResultItem.vue'
import { useFilter } from '@/composables/useFilter';
const { showDrawer, totalFiltersActive } = useFilter();

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
            <Button icon="pi pi-search" label="Search" :loading="isSearching" class="search-button"
                :disabled="isSearching || !searchQuery.trim()" @click="handleSearch" />
        </div>

        <template v-if="totalFiltersActive > 0">
            <OverlayBadge :value="totalFiltersActive" severity="danger" size="small">
                <Button icon="pi pi-filter" @click="showDrawer = true" />
            </OverlayBadge>
        </template>
        <template v-else>
            <Button icon="pi pi-filter" @click="showDrawer = true" v-tooltip.top="'Filter'" />
        </template>
    </div>

    <div v-if="searchResults.length > 0">
        <SearchResultItem v-for="result in searchResults" :key="result.embedding.id" :result="result"
            :collapsed="collapsedState[result.embedding.id]" :loading-state="loadingState" :content-cache="contentCache"
            @update:collapsed="(v) => onPanelToggle(v, result.embedding.id)" />
    </div>
    <div v-else-if="!isSearching">
        <div style="text-align: center;">
            <i>No results to display</i>
        </div>
    </div>
</template>

<style scoped>
.title {
    font-weight: 600;
}

.search-header {
    text-align: center;
    margin-bottom: 1rem;
}

.input-group {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
    gap: 0.5rem;
}

.p-inputgroup.p-inputgroup-lg {
    display: flex;
    justify-content: center;
    width: 100%;
    max-width: 700px;
}

.p-inputgroup .p-inputtext {
    font-size: 1.25rem;
    border-radius: 5px 0 0 5px;
    width: 100%;
    padding: .5em 1.5rem;
}

.p-button {
    font-size: 1.25rem;
    padding: .5em 1.5rem;
}

.search-button {
    border-radius: 0 5px 5px 0;
}
</style>