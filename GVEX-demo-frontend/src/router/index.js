import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/home/index.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: Home,
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior() {
        return {
            el: '#app',
            top: 0,
            behavior: 'smooth',
        };
    },
});

export default router;