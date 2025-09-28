import { reactive, readonly, toRef } from 'vue'

const state = reactive({
  isShown: false,
  isError: false,
  isClosable: false,
  title: '',
  message: '',
  icon: '',
})

export function usePopup() {
  const closePopup = (): void => {
    state.isShown = false
  }

  const showLoading = (title: string): void => {
    state.isShown = true
    state.isError = false
    state.isClosable = false
    state.title = title
    state.message = ''
    state.icon = 'pi pi-spin pi-spinner'
  }

  const showError = (title: string, message: string, isClosable: boolean = false): void => {
    state.isShown = true
    state.isError = true
    state.isClosable = isClosable
    state.title = title
    state.message = message
    state.icon = 'pi pi-exclamation-triangle'
  }

  const showMessage = (
    title: string,
    message: string,
    icon: string = '',
    isClosable: boolean = true,
  ): void => {
    state.isShown = true
    state.isError = false
    state.isClosable = isClosable
    state.title = title
    state.message = message
    state.icon = icon
  }

  return {
    closePopup,
    showLoading,
    showError,
    showMessage,
    isShown: readonly(toRef(state, 'isShown')),
    isError: readonly(toRef(state, 'isError')),
    isClosable: readonly(toRef(state, 'isClosable')),
    title: readonly(toRef(state, 'title')),
    icon: readonly(toRef(state, 'icon')),
    message: readonly(toRef(state, 'message')),
  }
}
