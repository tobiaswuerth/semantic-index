<script setup lang="ts">
import { ref } from 'vue';

const visible = ref(true);
const message = ref('');

const showError = (msg: string) => {
    message.value = msg;
    visible.value = true;
};
const hideError = () => {
    visible.value = false;
};

</script>

<template>
    <Dialog v-model:visible="visible" modal :closable="false" :dismissableMask="false"
        contentClass="p-0 bg-transparent border-0 shadow-none" class="bg-red-50">
        <div class="flex flex-column align-items-center justify-content-center px-6 pb-5 border-round-lg shadow-4">
            <div class="flex align-items-center justify-content-center bg-red-500 text-white border-circle"
                style="width:5rem;height:5rem;">
                <i class="pi pi-times-circle text-5xl"></i>
            </div>
            <span class="font-bold text-2xl text-red-700 dark:text-red-200 mt-4 mb-2">Error</span>
            <p class="text-center text-lg text-red-800 dark:text-red-100 mb-4">
                {{ message || 'No details provided.' }}
            </p>
            <Button label="Dismiss" class="p-button-danger w-8rem" @click="hideError"></Button>
        </div>
    </Dialog>
</template>
<style scoped></style>
