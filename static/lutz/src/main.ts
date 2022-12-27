import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'

import './assets/main.css'

const messages = {
    en: {
        message: {
          hello: 'hello world',
        },
        menu: {
            home: 'Home',
            about: 'About'
        }
      },
    pt: {
        message: {
            hello: 'Olá Mundo',
        },
        menu: {
            home: 'Início',
            about: 'Sobre',
        }
    }
}
const i18n = createI18n({
    locale: 'pt', // set locale
    fallbackLocale: 'en', // set fallback locale
    messages, // set locale messages
})

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(i18n)
app.mount('#app')
