<script setup lang="ts">

import { useNavigation } from '@/composables/useNavigation';
import NavigationDrawer from './NavigationDrawer.vue';
import FilterDrawer from './FilterDrawer.vue'

const { showDrawer, navigateTo } = useNavigation();

</script>

<template>
  <Toolbar>
    <template #start>
      <Button icon="pi pi-bars" @click="showDrawer = true" text rounded />
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

  <NavigationDrawer />
  <FilterDrawer />

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
  margin-right: 40px;
}

.p-toolbar-center img {
  height: 24px;
  width: 24px;
}
</style>