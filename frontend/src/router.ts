import { createRouter, createWebHistory } from 'vue-router'
import Index from '@/views/Index.vue'
import ChunkSearch from '@/views/ChunkSearch.vue'
import DocumentSearch from '@/views/DocumentSearch.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '/',
        name: 'index',
        component: Index,
      },
      {
        path: '/chunks',
        name: 'chunks',
        component: ChunkSearch,
      },
      {
        path: '/docs',
        name: 'documents',
        component: DocumentSearch,
      },
  ],
})

export default router
