import { createRouter, createWebHistory } from 'vue-router'
import TestRoute from '@/views/TestRoute.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/App.vue')
  },
  {
    path: '/test-route',
    name: 'TestRoute',
    component: TestRoute
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router