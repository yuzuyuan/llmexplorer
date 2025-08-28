// src/composables/useCombinedMarkdown.js
import { ref, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import markdownItAnchor from 'markdown-it-anchor';
import slugify from 'slugify';

export function useCombinedMarkdown(slugs = []) {
  const htmlContent = ref('');
  const toc = ref([]);

  const loadAndCombineContent = async () => {
    if (!slugs.length) return;

    try {
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

      let combinedMdText = '';
      const allHeadings = [];

      for (const slug of slugs) {
        const mdText = await fetch(`/src/content/${slug}.md`).then((res) => {
          if (!res.ok) throw new Error(`无法加载 ${slug}.md`);
          return res.text();
        });

        // 添加分隔符
        if (combinedMdText) {
          combinedMdText += '\n\n<hr class="article-separator">\n\n';
        }
        combinedMdText += mdText;

        // 为当前文件生成目录项
        const tokens = md.parse(mdText, {});
        tokens.forEach((token, index) => {
          if (token.type === 'heading_open' && ['h1', 'h2', 'h3'].includes(token.tag)) {
            const nextToken = tokens[index + 1];
            if (nextToken.type === 'inline' && nextToken.children.length > 0) {
              const title = nextToken.content;
              allHeadings.push({
                level: parseInt(token.tag.substring(1)),
                title: title,
                id: slugify(title, { lower: true, strict: true }),
              });
            }
          }
        });
      }

      htmlContent.value = md.render(combinedMdText);
      toc.value = allHeadings;

    } catch (error) {
      htmlContent.value = `<p class="alert alert-danger">内容加载失败: ${error.message}</p>`;
    }
  };

  onMounted(loadAndCombineContent);

  return { htmlContent, toc };
}