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
      let mdText = await fetch(`/content/${slug}.md`).then((res) => {
        if (!res.ok) throw new Error(`无法加载 ${slug}.md`);
        return res.text();
      });

      // --- 新增：Frontmatter 解析与渲染 ---
      let headerHtml = '';
      const frontmatterMatch = mdText.match(/^---\s*([\s\S]*?)\s*---/);

      if (frontmatterMatch) {
        const frontmatterText = frontmatterMatch[1];
        mdText = mdText.substring(frontmatterMatch[0].length).trim(); // 移除 frontmatter

        // 简单解析 frontmatter
        const titleMatch = frontmatterText.match(/title:\s*"(.*?)"/);
        const dateMatch = frontmatterText.match(/date:\s*(.*)/);
        const summaryMatch = frontmatterText.match(/summary:\s*"(.*?)"/s);

        const title = titleMatch ? titleMatch[1] : '未命名文档';
        const date = dateMatch ? dateMatch[1] : '';
        const summary = summaryMatch ? summaryMatch[1] : '';

        // 创建美化的头部 HTML
        headerHtml = `
          <div class="markdown-header mb-5">
            <h1 class="display-5 fw-bold">${title}</h1>
            ${date ? `<p class="text-muted fst-italic">${date}</p>` : ''}
            ${summary ? `<p class="lead bg-light p-3 rounded">${summary}</p>` : ''}
          </div>
          <hr class="mb-5">
        `;
      }
      // --- 结束：Frontmatter 解析 ---


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

      // 图片渲染逻辑
      const defaultRender = md.renderer.rules.image;
      md.renderer.rules.image = function (tokens, idx, options, env, self) {
        const token = tokens[idx];
        const srcIndex = token.attrIndex('src');
        let src = token.attrs[srcIndex][1];

        if (!/^(https?:)?\/\//.test(src) && !src.startsWith('/')) {
            src = `/content/${src}`;
            token.attrs[srcIndex][1] = src;
        }
        return defaultRender(tokens, idx, options, env, self);
      };

      // 组合头部和正文
      htmlContent.value = headerHtml + md.render(mdText);

      // 生成目录 (使用处理后的 mdText)
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
