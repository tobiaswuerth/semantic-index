<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const menuItems = [
  { label: 'Search Chunks', icon: 'pi pi-align-left', command: () => router.push('/chunks') },
  { label: 'Search Documents', icon: 'pi pi-file', command: () => router.push('/docs') },
]
</script>

<template>
  <div class="menu-overview">
    <h3>Go to:</h3>
    <Menu :model="menuItems" />
  </div>

</template>

<style scoped>
.menu-overview {
  max-width: 400px;
  margin: 2rem auto;
}
</style>
