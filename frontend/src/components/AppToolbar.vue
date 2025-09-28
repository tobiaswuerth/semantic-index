<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const drawerVisible = ref(false)
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

const navigateTo = (path: string) => {
  router.push(path)
  drawerVisible.value = false
}

// Replaced static array with computed so labels react to locale changes
const menuItems = computed(() => [
  { label: 'Home', icon: 'pi pi-home', command: () => navigateTo('/') },
])

</script>

<template>
  <Toolbar>
    <template #start>
      <Button icon="pi pi-bars" @click="drawerVisible = true" text rounded />
    </template>
    <template #center>
      <div class="toolbar-center">
        <div class="app-title" @click="navigateTo('/')">
          <img src="/icon.png" alt="Logo" />
          <span>Semantic Index</span>
        </div>
      </div>
    </template>
  </Toolbar>

  <Drawer v-model:visible="drawerVisible">
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
.p-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  border-top: 0 !important;
  border-left: 0 !important;
  border-right: 0 !important;
  border-radius: 0 !important;
  max-width: 1800px;
  margin-left: auto;
  margin-right: auto;
  border-left: 1px solid var(--p-content-border-color) !important;
  border-right: 1px solid var(--p-content-border-color) !important;
}

.p-toolbar-center .app-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.2rem;
  cursor: pointer;
}

.p-toolbar-center img {
  height: 24px;
  width: 24px;
}

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
