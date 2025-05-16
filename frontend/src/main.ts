import './style.css'

import { createApp } from 'vue'
import App from './App.vue'
const app = createApp(App)

import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';
import PrimeVue from 'primevue/config';
import Nora from '@primeuix/themes/nora';
app.use(PrimeVue, {
    theme: {
        preset: Nora
    },
    ripple: true,
});

app.mount('#app')
