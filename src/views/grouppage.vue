<template>
  <div class="group-page">
    <div class="container mx-auto px-4 py-8">
      <!-- 返回按钮 -->
      <div class="mb-8">
        <router-link 
          to="/" 
          class="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors duration-200 text-sm"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          返回主页
        </router-link>
      </div>

      <!-- 页面标题 -->
      <div class="text-center mb-12">
        <h1 class="text-3xl font-bold text-gray-800 mb-4">我们的小组</h1>
        <p class="text-gray-600">认识我们优秀的团队成员</p>
      </div>
      
      <!-- 小组介绍 -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-12 border border-gray-100">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">小组介绍</h2>
        <div class="prose max-w-none">
          <p class="text-gray-700 mb-3 text-sm leading-relaxed">
            我们是一个充满活力和创造力的团队，专注于探索大型语言模型的前沿应用。
            每个成员都有自己独特的技能和兴趣，但我们共同致力于技术创新和卓越开发。
          </p>
          <p class="text-gray-700 text-sm leading-relaxed">
            在这里，你可以了解我们每个成员的个人背景、技能专长和项目经验。
          </p>
        </div>
      </div>

      <!-- 成员网格 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="member in members" 
          :key="member.id"
          class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-all duration-300 border border-gray-100 hover:border-blue-200"
        >
          <router-link :to="member.route" class="block h-full">
            <div class="p-6">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-lg mr-4 flex-shrink-0">
                  {{ member.name.charAt(0) }}
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-800">{{ member.name }}</h3>
                  <p class="text-blue-600 text-sm font-medium">{{ member.role }}</p>
                </div>
              </div>
              <p class="text-gray-600 text-xs leading-relaxed line-clamp-3">{{ member.bio }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const members = [
  {
    id: 1,
    name: '喻祖源',
    role: '软件工程师',
    bio: 'Python开发者，动漫爱好者，游戏设计爱好者。专注于软件工程和大型语言模型应用开发。',
    route: '/member/yu-zuyuan'
  },
  {
    id: 2,
    name: '李剑',
    role: '前端开发',
    bio: '专注于前端技术开发，擅长Vue.js和React框架，对用户体验设计有深入研究。',
    route: '/member/li-jian'
  },
  {
    id: 3,
    name: '宋春成',
    role: '后端开发',
    bio: '后端技术专家，精通Python和Java，擅长系统架构设计和数据库优化。',
    route: '/member/song-chuncheng'
  },
  {
    id: 4,
    name: '瓦里斯',
    role: '算法工程师',
    bio: '机器学习和深度学习专家，专注于自然语言处理和计算机视觉技术研究。',
    route: '/member/walis'
  },
  {
    id: 5,
    name: '赵子彦',
    role: '产品经理',
    bio: '产品设计专家，擅长用户需求分析和产品规划，具有丰富的项目管理经验。',
    route: '/member/zhao-ziyan'
  },
  {
    id: 6,
    name: '吴威廉',
    role: 'UI/UX设计师',
    bio: '用户体验设计师，专注于界面设计和交互体验优化，追求简洁美观的设计风格。',
    route: '/member/wu-weilian'
  }
]
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prose {
  color: #374151;
}

.prose h2 {
  color: #1f2937;
  font-weight: 600;
}

.prose p {
  line-height: 1.6;
}
</style>