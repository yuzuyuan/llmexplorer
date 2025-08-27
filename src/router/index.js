import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Team from '../views/Team.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'

// 成员个人页面组件
const YuZuyuanPage = () => import('../views/members/yuzuyuanpage.vue')
const SongChunchengPage = () => import('../views/members/sok_chhhunheangpage.vue')
const LiJianPage = () => import('../views/members/LiJianPage.vue')
const WalisPage = () => import('../views/members/WalisPage.vue')
const ZhaoZiyanPage = () => import('../views/members/ZhaoZiyanPage.vue')
const WuWeilianPage = () => import('../views/members/WuWeilianPage.vue')

const routes = [
  { path: '/', component: Home },
  { path: '/team', component: Team },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/kb/:slug', component: KnowledgeBase, props: true },
  // 成员个人页面路由
  { path: '/member/yu-zuyuan', component: YuZuyuanPage },
  { path: '/member/song-chuncheng', component: SongChunchengPage },
  { path: '/member/li-jian', component: LiJianPage },
  { path: '/member/walis', component: WalisPage },
  { path: '/member/zhao-ziyan', component: ZhaoZiyanPage },
  { path: '/member/wu-weilian', component: WuWeilianPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router