import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import './style.css'
import App from './App.vue'

import en from './locales/en.json'
import cs from './locales/cs.json'

const i18n = createI18n({
  legacy: false,
  locale: 'cs', // default locale
  fallbackLocale: 'en',
  messages: {
    en,
    cs
  }
})

const app = createApp(App)
app.use(i18n)
app.mount('#app')