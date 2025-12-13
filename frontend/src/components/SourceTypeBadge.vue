<script setup lang="ts">
import { computed } from "vue";
import type { SourceType } from "@/dto/sourceType";

interface Props {
    sourceType: SourceType
}

const props = defineProps<Props>()

const tooltip = computed(() => {
    return props.sourceType.contains && props.sourceType.contains.length > 0
        ? props.sourceType.contains.join(", ")
        : '';
});

</script>

<template>
    <Badge :value="props.sourceType.name" size="small" class="source-type" :data-value="props.sourceType.name"
        v-tooltip="tooltip"></Badge>
</template>

<style scoped>
.source-type {
    margin: 0 0.5rem;
}

.source-type[data-value="Text"] {
    background-color: #9b9b9b;
}

.source-type[data-value="Data"] {
    background-color: #62ac2c;
}

.source-type[data-value="System"] {
    background-color: #6c6c6c;
}

.source-type[data-value="PDF"] {
    background-color: #F44336;
}

.source-type[data-value="Word"] {
    background-color: #3F51B5;
}

.source-type[data-value="Mail"] {
    background-color: #ae63bb;
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
