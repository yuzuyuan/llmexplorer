// src/composables/useMarkdown.js
import { ref, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import markdownItAnchor from 'markdown-it-anchor';
import slugify from 'slugify';

// 这是一个可复用的 Vue Composable 函数
export function useMarkdown(slug) {
  const htmlContent = ref('');
  const toc = ref([]);

  const loadContent = async () => {
    if (!slug) return;
    try {
      const mdText = await fetch(`/src/content/${slug}.md`).then((res) => {
        if (!res.ok) throw new Error(`无法加载 ${slug}.md`);
        return res.text();
      });

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
      });

      htmlContent.value = md.render(mdText);

      // 生成目录
      const tokens = md.parse(mdText, {});
      const headings = [];
      tokens.forEach((token, index) => {
        if (token.type === 'heading_open' && ['h1', 'h2', 'h3'].includes(token.tag)) {
          const nextToken = tokens[index + 1];
          if (nextToken.type === 'inline' && nextToken.children.length > 0) {
            const title = nextToken.content;
            headings.push({
              level: parseInt(token.tag.substring(1)),
              title: title,
              id: slugify(title, { lower: true, strict: true }),
            });
          }
        }
      });
      toc.value = headings;
    } catch (error) {
      htmlContent.value = `<p class="alert alert-danger">内容加载失败: ${error.message}</p>`;
    }
  };

  onMounted(loadContent);

  return { htmlContent, toc };
}