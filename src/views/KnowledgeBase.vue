<template>
  <div class="container my-4">
    <div class="row">
      <div class="col-lg-3 d-none d-lg-block">
        <aside class="toc-sidebar">
          <nav v-if="toc.length > 0">
            <h5 class="toc-title">本文内容</h5>
            <ul class="list-unstyled">
              <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
                <a :href="`#${item.id}`" class="toc-link">{{ item.title }}</a>
              </li>
            </ul>
          </nav>
        </aside>
      </div>

      <div class="col-lg-9">
        <div v-if="htmlContent" class="markdown-body" v-html="htmlContent"></div>
        <div v-else class="text-center my-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2">内容加载中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import markdownItAnchor from 'markdown-it-anchor'
import slugify from 'slugify'

const route = useRoute()
const htmlContent = ref('')
const toc = ref([])

onMounted(async () => {
  const slug = route.params.slug
  try {
    const mdText = await fetch(`/src/content/${slug}.md`).then((res) => res.text())

    const md = new MarkdownIt({
      html: true,
      linkify: true,
      typographer: true,
    }).use(markdownItAnchor, {
      permalink: markdownItAnchor.permalink.ariaHidden({
        placement: 'before',
        symbol: '#',
        class: 'header-anchor',
      }),
      slugify: (s) => slugify(s, { lower: true, strict: true }),
    })

    // 生成 HTML
    htmlContent.value = md.render(mdText)

    // 生成目录
    const tokens = md.parse(mdText, {})
    const headings = []
    tokens.forEach((token, index) => {
      if (token.type === 'heading_open' && ['h1', 'h2', 'h3'].includes(token.tag)) {
        const nextToken = tokens[index + 1]
        if (nextToken.type === 'inline' && nextToken.children.length > 0) {
          const title = nextToken.content
          headings.push({
            level: parseInt(token.tag.substring(1)),
            title: title,
            id: slugify(title, { lower: true, strict: true }),
          })
        }
      }
    })
    toc.value = headings
  } catch (error) {
    htmlContent.value = `<p class="text-danger">内容加载失败: ${error.message}</p>`
  }
})
</script>

<style scoped>
.toc-sidebar {
  position: sticky;
  top: 80px; /* 根据导航栏高度调整 */
  align-self: flex-start;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  padding: 1rem;
  border-left: 1px solid #e0e0e0;
}

.toc-title {
  font-weight: 600;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  color: #616161;
}

.toc-link {
  text-decoration: none;
  color: #616161;
  display: block;
  padding: 0.3rem 0;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.toc-link:hover {
  color: #0066cc;
  transform: translateX(5px);
}

.toc-level-2 {
  padding-left: 1rem;
}
.toc-level-3 {
  padding-left: 2rem;
}

.markdown-body {
  line-height: 1.7;
}

:deep(.markdown-body h1),
:deep(.markdown-body h2),
:deep(.markdown-body h3),
:deep(.markdown-body h4) {
  position: relative;
  scroll-margin-top: 80px; /* 为粘性头部留出偏移量 */
}

:deep(.markdown-body h1) {
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

:deep(.markdown-body .header-anchor) {
  opacity: 0;
  transition: opacity 0.2s ease;
  text-decoration: none;
  font-weight: 500;
  margin-left: -1em;
  padding-right: 0.5em;
}

:deep(.markdown-body h1:hover .header-anchor),
:deep(.markdown-body h2:hover .header-anchor),
:deep(.markdown-body h3:hover .header-anchor),
:deep(.markdown-body h4:hover .header-anchor) {
  opacity: 1;
}

:deep(.markdown-body code) {
  background-color: #f5f5f5;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  border-radius: 6px;
}

:deep(.markdown-body pre) {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

:deep(.markdown-body pre code) {
  background-color: transparent;
  padding: 0;
}

:deep(.markdown-body blockquote) {
  border-left: 0.25em solid #dfe2e5;
  padding: 0 1em;
  color: #6a737d;
}
</style>