import { createRouter, createWebHistory } from 'vue-router'
import ChunkSearch from './views/ChunkSearch.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: ChunkSearch,
    },
  ],
})

export default router
