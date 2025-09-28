import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import PrimeVue from 'primevue/config'
import PrimeTheme from '@primeuix/themes/aura'
import PrimeToast from 'primevue/toastservice'

import App from './App.vue'
import router from './router.ts'

const app = createApp(App)


app.use(createPinia())
app.use(router)

app.use(PrimeVue, {
  theme: {
    preset: PrimeTheme,
    options: {
      darkModeSelector: '.dark',
    },
  },
})
app.use(PrimeToast)

app.mount('#app')
