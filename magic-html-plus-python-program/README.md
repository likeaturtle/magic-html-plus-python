# Magic HTML Plus Python - 命令行工具

从网页 URL 提取内容并保存为多种格式（JSON、HTML、Markdown）的命令行工具。

## ✨ 功能特性

- 🌐 从任意 URL 自动提取网页内容
- 📝 支持多种内容类型：文章（article）、论坛（forum）、微信文章（weixin）
- 💾 输出多种格式：JSON、HTML、Markdown
- 🖼️ 支持下载图片到本地
- 🎯 智能内容提取，自动过滤无关内容
- 📂 按文章标题自动创建目录组织文件

## 📦 安装

### 前置要求

- Python >= 3.13
- uv（推荐）或 pip

### 使用 uv 安装（推荐）

```bash
uv pip install -r requirements.txt
```

### 使用 pip 安装

```bash
pip install -r requirements.txt
```

## 🚀 使用方法

### 基本用法

```bash
python main.py <URL>
```

### 指定内容类型

```bash
# 提取文章（默认）
python main.py https://example.com/article

# 提取论坛帖子
python main.py https://example.com/forum/thread --type forum

# 提取微信文章
python main.py https://mp.weixin.qq.com/s/xxxxx --type weixin
```

### 自定义输出目录

```bash
python main.py https://example.com --output-dir my_output
```

### 下载图片到本地

```bash
python main.py https://example.com --download-images
```

## 📝 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 要解析的网页 URL（必需） | - |
| `--type` | HTML 类型：`article`、`forum`、`weixin` | `article` |
| `--output-dir` | 输出目录路径 | `output` |
| `--download-images` | 下载图片到本地（Markdown 中使用相对路径） | 否 |

## 📂 输出结构

工具会在输出目录下创建以文章标题命名的子目录，包含以下文件：

```
output/
└── 文章标题/
    ├── content.json      # JSON 格式的提取数据
    ├── content.html      # 格式化的 HTML 文件
    ├── content.md        # Markdown 格式文件
    └── images/           # 图片目录（使用 --download-images 时）
        ├── img_xxxxxxxx.jpg
        └── img_yyyyyyyy.png
```

### content.json 数据结构

```json
{
  "title": "文章标题",
  "html": "提取的 HTML 内容",
  "text": "纯文本内容",
  "images": ["图片URL数组"],
  "base_url": "原始URL"
}
```

## 💡 使用示例

### 示例 1：提取文章并下载图片

```bash
python main.py https://example.com/article --download-images
```

输出：
```
正在获取URL: https://example.com/article
正在提取内容 (类型: article)...
正在保存到 output 目录...
  正在下载图片...
  ✓ 已下载 5 张图片
✓ 成功！结果已保存到目录: output/文章标题
  - JSON文件: output/文章标题/content.json
  - HTML文件: output/文章标题/content.html
  - Markdown文件: output/文章标题/content.md

提取的数据摘要:
  - 标题: 文章标题
  - HTML长度: 12345 字符
  - 纯文本长度: 5678 字符
  - 图片数量: 5
```

### 示例 2：提取微信文章

```bash
python main.py https://mp.weixin.qq.com/s/xxxxx --type weixin --output-dir weixin_articles
```

### 示例 3：提取论坛帖子

```bash
python main.py https://forum.example.com/thread/12345 --type forum
```

## 🔧 核心功能说明

### 智能内容提取

- 使用 `magic_html` 库进行智能内容提取
- 自动识别文章主体内容，过滤广告、导航栏等无关信息
- 支持不同类型网页的特定提取策略

### HTML 格式化

- 美化 HTML 代码结构
- 微信文章自动移除隐藏样式（`visibility:hidden`、`opacity:0`）
- 添加响应式样式和元数据

### Markdown 转换

- 智能转换 HTML 到 Markdown
- 支持标题、列表、表格、代码块、引用等元素
- 保留链接和图片引用
- 可选下载图片到本地并使用相对路径

### 图片下载

- 自动处理相对路径和绝对路径
- 使用 URL hash 避免文件名冲突
- 支持防盗链（添加 Referer 头）
- 失败时回退到原始 URL

## 🛠️ 技术栈

- **requests**: HTTP 请求处理
- **BeautifulSoup4**: HTML 解析和处理
- **magic_html**: 智能内容提取核心库

## 📋 依赖项

```txt
requests>=2.32.5
beautifulsoup4>=4.14.3
magic-html-plus-python-package
```

## ⚙️ 开发说明

### 项目结构

```
magic-html-plus-python-program/
├── main.py                 # 主程序文件
├── requirements.txt        # 依赖配置
├── pyproject.toml         # 项目配置
├── README.md              # 本文档
└── magic_html_plus_python_package-0.1.0-py3-none-any.whl  # 核心包
```

### 主要函数

- `fetch_html(url)`: 从 URL 获取 HTML 内容
- `extract_content(html, url, html_type)`: 提取内容
- `format_html(html_content)`: 格式化 HTML
- `html_to_markdown(html_content)`: HTML 转 Markdown
- `download_image(image_url, save_dir)`: 下载图片
- `save_results(data, output_dir)`: 保存结果

## 📄 许可证

本项目遵循项目根目录下的许可证条款。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如遇问题，请在项目仓库提交 Issue。
