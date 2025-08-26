import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Team from '../views/Team.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/team', component: Team },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/kb/:slug', component: KnowledgeBase, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
