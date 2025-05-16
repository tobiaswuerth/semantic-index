import { createApp } from 'vue'
import App from './App.vue'

import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: true,//'system',
            cssLayer: false
        },
    },
    ripple: true,
    inputStyle: 'filled',
});

app.mount('#app')
