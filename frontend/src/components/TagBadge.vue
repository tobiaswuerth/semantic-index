<script setup lang="ts">
import { computed } from "vue";
import type { Tag } from "@/dto/tag";

interface Props {
    tag: Tag
}

const props = defineProps<Props>()

const tooltip = computed(() => {
    return props.tag.contains && props.tag.contains.length > 0
        ? props.tag.contains.join(", ")
        : '';
});

</script>

<template>
    <Badge :value="props.tag.name" size="small" class="tag" :data-value="props.tag.name" v-tooltip="tooltip"></Badge>
</template>

<style scoped>
.tag {
    margin: 0 0.5rem;
}

.tag[data-value="File"] {
    background-color: #d3ac40;
}

.tag[data-value=".txt"] {
    background-color: #9b9b9b;
}

.tag[data-value=".xlsx"],
.tag[data-value=".csv"] {
    background-color: #62ac2c;
}

.tag[data-value=".pdf"] {
    background-color: #F44336;
}

.tag[data-value=".docx"],
.tag[data-value=".doc"],
.tag[data-value=".dot"],
.tag[data-value=".dotx"] {
    background-color: #2c78ce;
}

.tag[data-value=".msg"] {
    background-color: #ae63bb;
}

.tag[data-value="Jira"] {
    background-color: hsl(215, 82%, 41%);
}

.tag[data-value="Issue"] {
    background-color: hsl(215, 68%, 65%);
}

.tag[data-value="Comment"] {
    background-color: hsl(215, 53%, 65%);
}

.tag[data-value="Attachment"] {
    background-color: hsl(215, 38%, 57%);
}
</style>
