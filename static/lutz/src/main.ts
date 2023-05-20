import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'

import './assets/main.css'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

const messages = {
    en: {
        message: {
            hello: 'hello world',
            loading: 'Waiting for data',
            Female: "Female",
            Male: "Male",
            Neutral: "Neutral",
            dataType: "Type of data",
            about: "This tool grabs the data for gender set in user preferences by each editor in Wikimedia projects and graphs it.",
            startDate: "Start date",
            periodicity: "Periodicity",
            periodicities: {
                monthly: "monthly",
                daily: "daily",
                weekly: "weekly",
            }
        },
        menu: {
            home: 'Home',
            about: 'About'
        }
      },
    pt: {
        message: {
            hello: 'Olá Mundo',
            loading: 'Aguardando dados',
            Female: "Feminino",
            Male: "Masculino",
            Neutral: "Não especificado",
            dataType: "Tipo de dados",
            about: "Essa ferramenta puxa os dados de gêneros definidos nas preferências de cada editor em projetos Wikimedia e cria gráficos.",
            startDate: "Data de início",
            periodicity: "Periodicidade",
            periodicities: {
                monthly: "mensal",
                daily: "diário",
                weekly: "semanal",
            }
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

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(i18n)
app.use(vuetify)
app.mount('#app')
