<script setup lang="ts">
import type { SearchResult } from "@/dto/searchResult";
import { useToast } from "primevue/usetoast";
const toast = useToast();

interface Props {
  result: SearchResult
  collapsed: boolean
  loadingState: Record<number, boolean>
  contentCache: Record<number, string>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:collapsed': [value: boolean]
}>()

const formatDate = (dateString?: string) => {
  if (!dateString) return 'No date'
  return dateString.split('T')[0]
}
const handleResolveLink = (source: SearchResult['source']) => {
  const link = source.resolved_to || source.uri
  // link, open
  if (link.startsWith('http://') || link.startsWith('https://')) {
    window.open(link, '_blank', 'noopener,noreferrer')
    return
  }

  // file, copy path
  if (navigator.clipboard) {
    navigator.clipboard.writeText(link).then(() => {
      toast.add({ severity: 'success', summary: 'Copied to clipboard', detail: link, life: 1500 });
    })
  } else {
    toast.add({ severity: 'error', summary: 'Clipboard not supported', detail: 'Cannot copy file path', life: 1500 });
  }
}
</script>

<template>
  <Panel class="result-item" :collapsed="props.collapsed" toggleable
    @update:collapsed="(v) => emit('update:collapsed', v)">
    <template #header>
      <div class="header-content">
        <strong>{{ props.result.source.title }}</strong>
        <Badge :value="props.result.source.source_type.name" size="small" class="source-type"
          :data-value="props.result.source.source_type.name"></Badge>
        <br />
        <small>
          <a @click="handleResolveLink(props.result.source)" class="resolve-link">
            {{ props.result.source.resolved_to }}
          </a>
        </small>
      </div>
      <div class="info-box">
        <div class="similarity-container">
          <small>{{ (props.result.similarity * 100).toFixed(1) }}% Match</small>
          <ProgressBar :value="props.result.similarity * 100" :show-value="false" style="height: 6px;"></ProgressBar>
        </div>
      </div>
    </template>

    <div v-if="props.loadingState[props.result.embedding.id]">
      <ProgressBar mode="indeterminate" style="height: 4px"></ProgressBar>
    </div>
    <div v-else class="content-preview">
      <div class="source-dates">
        <small v-tooltip="'Created Date'">
          <span class="pi pi-file-plus"></span> {{ formatDate(props.result.source.obj_created) }}
        </small> /
        <small v-tooltip="'Modified Date'">
          <span class="pi pi-file-edit"></span> {{ formatDate(props.result.source.obj_modified) }}
        </small> /
        <small v-tooltip="'Last Checked'">
          <span class="pi pi-file-check"></span> {{ formatDate(props.result.source.last_checked) }}
        </small> /
        <small v-tooltip="'Last Processed'">
          <span class="pi pi-file-export"></span> {{ formatDate(props.result.source.last_processed) }}
        </small>
        <div v-if="props.result.source.last_processed < props.result.source.obj_modified">
          <Badge severity="warn" size="small"
            v-tooltip="'This source has been modified since it was last processed. The content may be outdated.'">
            <span class="pi pi-exclamation-triangle"></span> Outdated
          </Badge>
        </div>
      </div>
      <p> {{ props.contentCache[props.result.embedding.id] }} </p>
    </div>
  </Panel>
</template>

<style scoped>
.info-box {
  display: flex;
  align-items: top;
  flex-direction: row;
  flex-shrink: 0;
  flex-grow: 0;
  margin: 0 0.75rem 0 1.5rem;
}

.source-dates {
  margin-bottom: 0.5rem;
  display: flex;
  gap: 0.5rem;
  align-items: bottom;
}

.info-box>.similarity-container {
  align-self: top;
}

.result-item {
  margin-bottom: 0.2rem;
  border: 0;
}

.header-content {
  flex-grow: 1;
  font-weight: 600;
  word-break: break-all;
}

.content-preview {
  padding: .5rem;
  font-size: 0.9rem;
}

.content-preview>p {
  font-style: italic;
}

.source-type {
  margin-left: 0.5rem;
}

.source-type[data-value="PDF"] {
  background-color: #F44336;
}

.source-type[data-value="Word"] {
  background-color: #3F51B5;
}

.source-type[data-value="CSV"] {
  background-color: #45a445;
}

.source-type[data-value="Markdown"] {
  background-color: #af934c;
}

.source-type[data-value="TXT"] {
  background-color: #787878;
}

.source-type[data-value="Mail"] {
  background-color: #83408f;
}

.source-type[data-value="Issue"] {
  background-color: #0748a6;
}

.source-type[data-value="Comment"] {
  background-color: #496790;
}

.source-type[data-value="Attachment"] {
  background-color: #49525e;
}

.resolve-link {
  cursor: pointer;
  color: var(--p-primary-color);
}
</style>
