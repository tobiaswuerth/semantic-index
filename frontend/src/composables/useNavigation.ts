import { reactive, readonly, toRef } from 'vue'
import { useRouter } from 'vue-router'

const state = reactive({
  showDrawer: false,
})

export function useNavigation() {
  const router = useRouter()

  const navigateTo = (path: string) => {
    router.push(path);
    state.showDrawer = false;
  }
  return {
    showDrawer: toRef(state, 'showDrawer'),
    navigateTo,
    state: readonly(state),
  }
}
