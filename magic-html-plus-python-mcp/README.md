# Magic HTML Extractor - MCP 服务

这是一个基于 Model Context Protocol (MCP) 的网页内容提取服务，可以从任意 URL 提取网页内容并保存为 JSON、HTML 和 Markdown 格式。

## 功能特性

- 📄 从 URL 提取网页正文内容
- 🎨 支持多种网页类型（文章、论坛、微信公众号）
- 💾 自动保存为 JSON、HTML 和 Markdown 格式
- 🖼️ 可选下载图片到本地
- 🔧 易于集成到 Claude Desktop 等 MCP 客户端

## 安装

确保已安装 Python 3.13+ 和 uv：

```bash
# 安装依赖
uv sync
```

## MCP 工具列表

### 1. extract_webpage

从 URL 提取网页内容并保存为多种格式。

**参数：**
- `url` (必需): 要解析的网页 URL
- `html_type` (可选): HTML 类型，可选值:
  - `article` - 文章页面（默认）
  - `forum` - 论坛页面
  - `weixin` - 微信公众号文章
- `output_dir` (可选): 输出目录，默认为 `output`

**返回值：**
包含提取结果的 JSON，包括：
- 保存的文件路径（JSON、HTML、Markdown）
- 内容摘要（标题、文本长度、图片数量等）

### 2. extract_webpage_with_images

从 URL 提取网页内容，并下载所有图片到本地。

**参数：**
- `url` (必需): 要解析的网页 URL
- `html_type` (可选): HTML 类型，同上
- `output_dir` (可选): 输出目录，默认为 `output`

**返回值：**
除了基本信息外，还包括下载的图片数量和图片目录路径。

## 配置 Claude Desktop

1. 打开 Claude Desktop 配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加以下配置（请将路径替换为你的实际路径）：

```json
{
  "mcpServers": {
    "magic-html-extractor": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/fujd/Desktop/magic-html-plus-python-mcp",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

3. 重启 Claude Desktop

## 命令行使用（传统方式）

如果你想直接使用命令行工具而不是 MCP 服务：

```bash
# 基本用法
uv run main.py https://example.com

# 指定网页类型
uv run main.py https://example.com --type forum

# 下载图片
uv run main.py https://example.com --download-images

# 自定义输出目录
uv run main.py https://example.com --output-dir my_output
```

## 使用示例

### 在 Claude Desktop 中使用

配置完成后，你可以在 Claude Desktop 中这样使用：

```
请帮我提取这个网页的内容：https://example.com/article
```

Claude 会自动调用 `extract_webpage` 工具来提取内容。

如果你需要下载图片：

```
请提取这个网页内容并下载所有图片：https://example.com/article
```

Claude 会调用 `extract_webpage_with_images` 工具。

### 输出结果

提取的内容会保存在 `output/文章标题/` 目录下，包含：

```
output/
└── 文章标题/
    ├── content.json      # 完整的提取数据
    ├── content.html      # 格式化的 HTML
    ├── content.md        # Markdown 格式
    └── images/          # 下载的图片（如果使用了图片下载功能）
        ├── img_xxxxx.jpg
        └── img_yyyyy.png
```

## 依赖项

- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `magic-html` - 网页内容提取
- `mcp` - Model Context Protocol SDK

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
