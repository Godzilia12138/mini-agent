import { marked } from "marked";
import hljs from "highlight.js";

marked.setOptions({ breaks: true, gfm: true });

function highlightCode(code, lang) {
  if (lang && hljs.getLanguage(lang)) {
    return hljs.highlight(code, { language: lang }).value;
  }
  return hljs.highlightAuto(code).value;
}

const renderer = {
  code({ text, lang }) {
    const language = lang || "text";
    const highlighted = highlightCode(text, language);
    const encoded = encodeURIComponent(text);
    return `<div class="code-block-wrapper">
      <div class="code-block-header">
        <span class="code-lang">${language}</span>
        <button type="button" class="copy-code-btn" data-code="${encoded}">复制</button>
      </div>
      <pre><code class="hljs language-${language}">${highlighted}</code></pre>
    </div>`;
  },
};

marked.use({ renderer });

export function renderMarkdown(text) {
  if (!text) return "";
  try {
    return marked.parse(text);
  } catch {
    return text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

export function escapeHtml(text) {
  return text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
