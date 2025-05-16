import './style.css'
import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';

import { createApp } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/nora';

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura
    },
    ripple: true,
});

app.mount('#app')
