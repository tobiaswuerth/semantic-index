import { ref } from 'vue'

export const errorState = ref<{
    message: string;
    visible: boolean;
}>({
    message: '',
    visible: false
})

export function showError(error: unknown): void {
    console.error("An error occurred:", error)

    const message = error instanceof Error ? error.message :
        typeof error === 'string' ? error :
            typeof error === 'object' && error !== null ? JSON.stringify(error) :
                "An unknown error occurred"

    errorState.value = { message, visible: true }
}

export function clearError(): void {
    errorState.value = { message: '', visible: false }
}