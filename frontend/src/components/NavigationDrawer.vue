<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useNavigation } from '@/composables/useNavigation';

const { showDrawer, navigateTo } = useNavigation();

const isDark = ref(false)

onMounted(() => {
  const savedTheme = localStorage.getItem('theme-preference')
  isDark.value = savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
  document.documentElement.classList.toggle('dark', isDark.value)
})

watch(isDark, (newValue) => {
  document.documentElement.classList.toggle('dark', newValue)
  localStorage.setItem('theme-preference', newValue ? 'dark' : 'light')
})

const menuItems = computed(() => [
  { label: 'Search Chunks', icon: 'pi pi-align-left', command: () => navigateTo('/chunks') },
  { label: 'Search Documents', icon: 'pi pi-file', command: () => navigateTo('/docs') },
])

</script>

<template>

  <Drawer v-model:visible="showDrawer" position="left">
    <template #header>
      <div>
        <img src="/icon.png" alt="Logo" @click="navigateTo('/')" style="cursor: pointer;" />
        <div>
          <div class="title">Semantic Index</div>
          <div class="subtitle">Search Your Knowledge Base</div>
        </div>
      </div>
    </template>

    <Divider />
    <Menu :model="menuItems" />
    <Divider />

    <div class="toggle">
      <div>
        <i :class="isDark ? 'pi pi-moon' : 'pi pi-sun'"></i>
        <span>{{ isDark ? 'Dark' : 'Light' }}</span>
      </div>
      <ToggleSwitch v-model="isDark" />
    </div>
  </Drawer>


</template>

<style scoped>

.title {
  font-weight: 600;
}

.toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  margin-top: auto;
}

.toggle>div {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.toggle i {
  color: var(--p-primary-color);
}
</style>

<style>
/* Ensure styles apply to PrimeVue Drawer content which may be teleported outside this component */

.p-drawer-header {
  padding-bottom: 0.5rem !important;
}

.p-drawer-header>div {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.p-drawer-header img {
  height: 48px;
  width: 48px;
}

.p-drawer {
  width: 23rem !important;
  max-width: 85vw !important;
}

.p-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.p-drawer-content .language-selector,
.p-drawer-content .toggle {
  padding-bottom: 0.5rem !important;
  padding-top: 0.5rem !important;
}

.p-drawer-content .p-menu {
  border: 0 !important;
  background: transparent !important;
  margin: 1rem 0;
  flex-grow: 1;
}
</style>
