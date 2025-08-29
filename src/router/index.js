import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Team from '../views/Team.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'


// 成员个人页面组件
const YuZuyuanPage = () => import('../views/members/yuzuyuanpage.vue')
const SongChunchengPage = () => import('../views/members/sok_chhhunheangpage.vue')
const LiJianPage = () => import('../views/members/LiJianPage.vue')
const WalisPage = () => import('../views/members/WarisPage.vue')
const KyawKyawTunPage = () => import('../views/members/KyawKyawTunPage.vue') // <--- 更新
const WuWeilianPage = () => import('../views/members/WuWeilianPage.vue')
const LlmBasicsPage = () => import('../views/pages/LlmBasicsPage.vue');
const PromptEngineeringPage = () => import('../views/pages/PromptEngineeringPage.vue');
const RagPage = () => import('../views/pages/RagPage.vue');
const SftPage = () => import('../views/pages/SftPage.vue');
const ArticlesPage = () => import('../views/pages/ArticlesPage.vue');
const routes = [
  { path: '/', component: Home },
  { path: '/team', component: Team },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/articles', component: ArticlesPage },
    // 更新知识库路由指向新的独立页面
  { path: '/kb/1-llm-basics', component: LlmBasicsPage },
  { path: '/kb/2-prompt-engineering', component: PromptEngineeringPage },
  { path: '/kb/3-rag', component: RagPage },
  { path: '/kb/4-sft', component: SftPage },
  // 成员个人页面路由
  { path: '/member/yu-zuyuan', component: YuZuyuanPage },
  { path: '/member/song-chuncheng', component: SongChunchengPage },
  { path: '/member/li-jian', component: LiJianPage },
  { path: '/member/walis', component: WalisPage },
  { path: '/member/kyaw-kyaw-tun', component: KyawKyawTunPage }, // <--- 更新
  { path: '/member/wu-weilian', component: WuWeilianPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router