---
name: magic-html-extractor
description: 使用 magic-html MCP 服务器，将网页内容提取并保存为本地 JSON/HTML/Markdown 文件，适用于文章、论坛和微信公众号页面，可按需下载图片。
---

# Magic HTML 网页内容提取 Skill

## 目标

- 使用 `magic-html-extractor` MCP 服务器，将网页内容提取并保存为本地 JSON / HTML / Markdown。
- 针对文章、论坛帖子、微信公众号文章等场景选择合适的 `html_type`。
- 在对话中返回清晰的摘要和文件位置，并按需加载生成的 Markdown 内容进行后续分析或改写。

## 使用时机

当用户提出以下需求之一时，应考虑启用本 Skill：

- **保存网页内容**：例如“保存网页为 Markdown/HTML/JSON”“离线阅读网页”。
- **对网页内容做进一步处理**：例如“总结这篇文章”“帮我翻译/改写这篇网页内容”。
- **需要连同图片一起完整归档网页**：例如“把这篇公众号文章连图片一起保存到本地”。

## MCP 工具说明

本 Skill 依赖 `magic-html-extractor` MCP 服务器中提供的两个工具：

- `extract_webpage`
- `extract_webpage_with_images`

两者的通用参数与返回值：

- **参数**：
  - `url`：必填，必须以 `http://` 或 `https://` 开头。
  - `html_type`：可选，`article` / `forum` / `weixin`，默认 `article`。
  - `output_dir`：可选，默认 `"output"`，为生成内容的根目录。
- **返回值**：
  - 返回的是 **JSON 字符串**，需要先解析成对象再使用。
  - 主要字段包括：
    - `success`：布尔值，表示是否成功。
    - `output_directory`：当前提取内容所在目录（目录名根据标题清洗生成）。
    - `files`：包含 `json`、`html`、`markdown`、`images_directory` 的本地路径。
    - `summary`：包括 `title`、`html_length`、`text_length`、`image_count`、`downloaded_image_count` 等信息。

### `extract_webpage`

- 额外参数：
  - `download_images`：是否下载图片到本地，默认为 `True`。
- 适用场景：
  - 一般“提取网页内容并保存”的请求，用户未特别强调必须下载所有图片时优先使用。

### `extract_webpage_with_images`

- 行为特征：
  - 始终会下载图片（等价于 `download_images=True`）。
- 适用场景：
  - 用户明确提出“需要连图片一起完整保存/归档网页”时优先使用。

## 参数选择策略

- **选择 `html_type`：**
  - 若 URL 包含 `mp.weixin.qq.com` 或用户说明是“微信公众号文章”：使用 `weixin`。
  - 若页面明显是论坛/BBS 帖子结构：使用 `forum`。
  - 其他大部分普通网页：使用默认 `article`。

- **选择工具：**
  - 普通“保存/提取网页内容”请求：优先使用 `extract_webpage`。
  - 用户强调“需要下载图片”“完整归档网页”：优先使用 `extract_webpage_with_images`。

- **选择 `output_dir`：**
  - 若用户有明确目录要求（例如“保存到某个路径/项目目录下”），按用户要求设置 `output_dir`。
  - 否则使用默认 `"output"`，由 MCP 服务器在当前工作目录下创建输出目录。

## 典型工作流程

当本 Skill 被触发时，一般遵循以下步骤：

1. **澄清需求（如有必要）**
   - 确认用户是否需要下载图片。
   - 确认是否有特定保存目录，还是使用默认目录即可。

2. **选择并调用 MCP 工具**
   - 根据“参数选择策略”选定合适的 `html_type` 和工具函数。
   - 调用对应的 MCP 工具，传入：
     - `url`
     - `html_type`
     - `output_dir`（以及 `download_images`，如果使用 `extract_webpage` 且需要覆盖默认值）。

3. **解析返回结果**
   - 将 MCP 返回的 JSON 字符串解析为对象。
   - 若 `success` 为 `False`，读取 `error` 字段，向用户解释错误原因（例如 URL 格式错误或网络异常），必要时在用户同意下调整参数重试。

4. **向用户汇报结果**
   - 提供清晰的结果概要：
     - 标题：`summary.title`
     - 文本长度：`summary.text_length`
     - 图片数量：`summary.image_count` 和 `summary.downloaded_image_count`
   - 明确告知生成文件的路径：
     - JSON 文件路径：`files.json`
     - HTML 文件路径：`files.html`
     - Markdown 文件路径：`files.markdown`
     - 图片目录：`files.images_directory`（如存在）。

5. **按需加载和处理 Markdown 内容**
   - 若用户需要对内容进行“阅读/总结/翻译/改写/提炼要点”等操作：
     - 优先读取生成的 Markdown 文件（`files.markdown`），而不是原始 HTML。
     - 使用 Markdown 内容作为后续分析和生成的主要信息来源。
   - 若用户只关心保存结果而不需要在对话中展开内容：
     - 只需汇报路径和摘要，无需加载完整内容。

## 示例

### 示例一：保存技术博客文章为 Markdown 并总结

- 用户请求：
  - “帮我把这篇技术博客保存成 Markdown 并简单总结一下：<URL>”
- 预期行为：
  1. 使用 `html_type="article"` 调用 `extract_webpage`。
  2. 解析结果，获取 Markdown 文件路径（例如：`output/<清洗后的标题>/content.md`）。
  3. 向用户汇报保存路径和 `summary` 中的关键信息。
  4. 读取生成的 Markdown 文件内容，对文章进行简要总结后回复用户。

### 示例二：完整归档微信公众号文章（包括图片）

- 用户请求：
  - “把这篇公众号文章完整保存下来，连图片也要：<URL>”
- 预期行为：
  1. 将 `html_type` 设置为 `"weixin"`。
  2. 调用 `extract_webpage_with_images`，使用默认 `output_dir="output"`（或按用户指定）。
  3. 解析结果，向用户报告：标题、图片总数、实际下载的图片数量以及各类输出文件路径。
  4. 如用户随后要求对文章内容做进一步处理（如提炼要点/生成笔记），则读取生成的 Markdown 文件并继续后续任务。

## 错误处理

- 若 URL 未以 `http://` 或 `https://` 开头：
  - 直接提示用户 URL 格式不正确，要求其修正后重试。
- 若网络异常或目标网站暂时无法访问：
  - 向用户说明可能的网络/站点问题，并询问是否稍后重试或更换 URL。
- 对于多次失败的情况：
  - 明确说明当前自动化提取的限制，并在可能的情况下建议替代方案（例如手动复制关键内容后再协助整理）。
