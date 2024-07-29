import { createApp } from 'vue';

import App from './App.vue';
import router from './router';
import axios from 'axios'
import './assets/css/base.css'
import 'amfe-flexible'
import { createPinia } from 'pinia'

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);

// const axiosInstance = axios.create({
//   baseURL: 'http://127.0.0.1:5000/', 
// })
app.config.globalProperties.$axios = axios

app.use(router).mount('#app');