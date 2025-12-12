<script setup lang="ts">
import type { SourceType } from "@/dto/sourceType";

interface Props {
    sourceType: SourceType
}

const props = defineProps<Props>()

</script>

<template>
    <Badge :value="props.sourceType.name" size="small" class="source-type" :data-value="props.sourceType.name"></Badge>
</template>

<style scoped>
.source-type {
    margin: 0 0.5rem;
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
</style>
