# Magic HTML Plus - Python

一个功能强大的 Python 网页内容智能提取工具集，基于增强的 Readability 算法，能够自动识别并提取网页正文内容。支持文章、论坛、微信公众号等多种网页类型，提供命令行工具和 MCP (Model Context Protocol) 服务接口。

## ✨ 核心特性

- 🎯 **智能提取** - 基于密度和可读性算法自动识别网页正文
- 📰 **多类型支持** - 文章、论坛帖子、微信公众号等多种网页类型
- 🎨 **内容清洗** - 自动清除广告、导航栏等无关内容
- 🔧 **自定义规则** - 支持 XPath/CSS 选择器自定义提取规则
- 📐 **数学公式** - MathML 转 LaTeX 支持
- 🖼️ **图片处理** - 自动路径转换和本地下载
- 💾 **多格式输出** - JSON、HTML、Markdown 三种格式
- 🔌 **MCP 集成** - 可集成到 Claude Desktop 等 MCP 客户端

## 📦 项目结构

本仓库包含三个子项目：

```
magic-html-plus-python/
├── magic-html-plus-python-package/    # 核心提取库
├── magic-html-plus-python-mcp/         # MCP 服务
├── magic-html-plus-python-program/     # 命令行应用
└── README.md                           # 本文件
```

### 1. magic-html-plus-python-package (核心库)

核心的网页内容提取 Python 包，提供可编程的 API 接口。

**主要功能：**
- 多种提取器（Article、Forum、Weixin、Custom）
- 智能标题识别
- 内容清洗和格式化
- 基准测试工具

**打包发布：**

该包可以构建并发布到 PyPI，供其他项目依赖使用：

```bash
cd magic-html-plus-python-package

# 使用 uv 构建和发布（推荐）
uv build
uv publish

# 或使用传统工具
pip install build twine
python -m build
twine upload dist/*
```

发布后可以直接安装：
```bash
uv pip install magic-html-plus-python-package
# 或
pip install magic-html-plus-python-package
```

📖 [查看详细文档](./magic-html-plus-python-package/README.md)

### 2. magic-html-plus-python-mcp (MCP 服务)

基于 Model Context Protocol 的网页提取服务，可集成到 Claude Desktop 等 MCP 客户端。

**主要功能：**
- MCP 工具接口：`extract_webpage` 和 `extract_webpage_with_images`
- 自动保存为 JSON、HTML、Markdown
- 可选图片下载功能
- 命令行模式支持

📖 [查看详细文档](./magic-html-plus-python-mcp/README.md)

### 3. magic-html-plus-python-program (命令行应用)

独立的命令行应用程序封装，方便直接使用。

## 🚀 快速开始

### 环境要求

- Python 3.13+
- uv (推荐) 或 pip

### 安装方式

选择以下任一方式安装：

#### 方式 1: 使用核心库 (编程使用)

```bash
cd magic-html-plus-python-package
uv sync
```

```python
from magic_html import GeneralExtractor

extractor = GeneralExtractor()
result = extractor.extract(html=html_content, base_url="https://example.com")
print(result['title'])
print(result['html'])
```

#### 方式 2: 使用 MCP 服务 (集成到 Claude Desktop)

```bash
cd magic-html-plus-python-mcp
uv sync
```

配置 Claude Desktop：

```json
{
  "mcpServers": {
    "magic-html-extractor": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/magic-html-plus-python-mcp",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

#### 方式 3: 使用命令行工具

```bash
cd magic-html-plus-python-mcp
uv sync

# 提取网页
uv run main.py https://example.com

# 提取并下载图片
uv run main.py https://example.com --download-images

# 指定网页类型
uv run main.py https://example.com --type forum
```

## 📦 打包和分发

### 打包核心库 (magic-html-plus-python-package)

核心库可以构建为 Python 包，并发布到 PyPI 供其他项目使用。

#### 快速打包

**使用 uv（推荐）**

```bash
cd magic-html-plus-python-package

# 构建分发包
uv build
```

**使用传统 build 工具**

```bash
cd magic-html-plus-python-package

# 安装构建工具
pip install build

# 构建分发包
python -m build
```

构建后在 `dist/` 目录会生成：
- `magic-html-plus-python-package-0.1.0.tar.gz` - 源码分发包
- `magic_html_plus_python_package-0.1.0-py3-none-any.whl` - wheel 包

#### 本地测试安装

**使用 uv（推荐）**

```bash
# 安装 wheel 包
uv pip install dist/magic_html_plus_python_package-0.1.0-py3-none-any.whl

# 测试导入
python -c "from magic_html import GeneralExtractor; print('Success!')"
```

**使用 pip**

```bash
# 安装 wheel 包
pip install dist/magic_html_plus_python_package-0.1.0-py3-none-any.whl

# 测试导入
python -c "from magic_html import GeneralExtractor; print('Success!')"
```

#### 发布到 PyPI

**使用 uv（推荐）**

```bash
# 发布到测试 PyPI（建议先测试）
uv publish --publish-url https://test.pypi.org/legacy/

# 发布到正式 PyPI
uv publish

# 或者使用 token 参数
uv publish --token <your-pypi-token>
```

**使用 twine**

```bash
# 安装 twine
pip install twine

# 发布到测试 PyPI（建议先测试）
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 发布到正式 PyPI
twine upload dist/*
```

#### 使用已发布的包

发布后，其他用户可以直接安装：

**使用 uv（推荐）**

```bash
uv pip install magic-html-plus-python-package
```

**使用 pip**

```bash
pip install magic-html-plus-python-package
```

**使用示例：**

```python
from magic_html import GeneralExtractor

extractor = GeneralExtractor()
result = extractor.extract(html=html_content, base_url="https://example.com")
```

#### 打包注意事项

1. **更新版本号**：发布前修改 `pyproject.toml` 中的 `version`
2. **检查依赖**：确保所有依赖在 `pyproject.toml` 中正确声明
3. **包含文件**：XSL 文件已在 `package-data` 中配置
4. **先测试**：建议先上传到 Test PyPI 进行充分测试
5. **uv 认证**：使用 `uv publish` 时，可以通过环境变量 `UV_PUBLISH_TOKEN` 或 `--token` 参数配置 PyPI token

详细打包说明请参考：[核心库 README](./magic-html-plus-python-package/README.md#打包和发布)

## 📚 使用示例

### 1. 作为 Python 库使用

```python
from magic_html import GeneralExtractor

# 创建提取器
extractor = GeneralExtractor()

# 基本提取
result = extractor.extract(
    html=html_content, 
    base_url="https://example.com"
)

# 指定网页类型
result = extractor.extract(
    html=html_content, 
    base_url="https://forum.example.com/post/123",
    html_type="forum"
)

# 使用自定义规则
extractor = GeneralExtractor(config_path="rules.json")
result = extractor.extract(html=html_content, base_url=url)
```

### 2. 在 Claude Desktop 中使用

配置完成后，直接对话即可：

```
请帮我提取这个网页的内容：https://example.com/article
```

```
请提取这个网页并下载所有图片：https://example.com/gallery
```

### 3. 命令行使用

```bash
# 基本用法
uv run main.py https://example.com

# 下载图片到本地
uv run main.py https://example.com --download-images

# 指定输出目录
uv run main.py https://example.com --output-dir my_output

# 提取微信公众号文章
uv run main.py https://mp.weixin.qq.com/... --type weixin
```

## 🎯 网页类型说明

### article (默认)
适用于新闻文章、博客文章等标准内容页面。

### forum
专门用于论坛帖子、问答网站等包含多条评论或回复的页面。

### weixin
针对微信公众号文章优化，处理微信特有的标签结构。

## 🔧 高级功能

### 自定义提取规则

创建 `rules.json` 配置文件：

```json
{
  "www.example.com": {
    "clean": [
      "//script",
      "//style",
      "//div[@class='ads']"
    ],
    "title": {
      "mode": "xpath",
      "value": "//h1[@class='article-title']/text()"
    },
    "content": {
      "mode": "xpath",
      "value": "//div[@class='article-content']"
    }
  }
}
```

### 批量处理

```python
from magic_html import GeneralExtractor
import requests

extractor = GeneralExtractor()
urls = ["url1", "url2", "url3"]

for url in urls:
    response = requests.get(url)
    result = extractor.extract(
        html=response.text, 
        base_url=url
    )
    # 处理结果...
```

### 图片本地化

命令行模式下使用 `--download-images` 参数：

```bash
uv run main.py https://example.com --download-images
```

图片将保存在 `output/文章标题/images/` 目录下，Markdown 文件中使用相对路径引用。

## 📊 基准测试

核心库包含针对文章和论坛的基准测试集：

```bash
cd magic-html-plus-python-package

# 评估文章提取效果
uv run benchmark/evaluate_articles.py

# 评估论坛提取效果
uv run benchmark/evaluate_forums.py
```

测试数据位于 `benchmark/data/` 目录下。

## 🏗️ 技术架构

### 核心算法

基于增强的 Readability 算法，结合以下技术：

- **文本密度分析** - 计算节点的文本密度
- **标签权重** - 根据 HTML 标签类型赋予不同权重
- **链接密度** - 识别并过滤导航和广告区域
- **DOM 树分析** - 智能识别正文容器
- **样式过滤** - 移除隐藏和装饰性内容

### 提取器架构

```
BaseExtractor (基类)
    ├── ArticleExtractor (文章)
    ├── ForumExtractor (论坛)
    ├── WeixinExtractor (微信)
    └── CustomExtractor (自定义规则)
```

## 📋 依赖项

### 核心库依赖

- `lxml` - HTML/XML 解析
- `numpy` - 数值计算
- `charset-normalizer` - 字符编码检测
- `py-asciimath` - 数学公式处理

### MCP 服务依赖

- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `mcp` - Model Context Protocol SDK

## 📄 输出格式

### JSON 格式

```json
{
  "title": "文章标题",
  "html": "提取的正文 HTML",
  "text": "纯文本内容",
  "base_url": "https://example.com",
  "images": ["image1.jpg", "image2.png"],
  "xp_num": "xpath标识",
  "drop_list": []
}
```

### HTML 格式

格式化的 HTML 文档，包含样式和元数据，可直接在浏览器中查看。

### Markdown 格式

- 保留标题层级
- 转换列表、表格、代码块
- 支持图片本地化
- 保留链接和格式

## ❓ 常见问题

**Q: 提取的内容不完整怎么办？**

A: 可以尝试：
1. 指定正确的 `html_type` 参数
2. 使用自定义规则配置精确提取
3. 检查 HTML 是否完整（某些网站使用 JavaScript 动态加载）

**Q: 如何处理动态加载的网页？**

A: 本工具处理的是静态 HTML。对于动态网页，建议先使用 Selenium 或 Playwright 渲染完整页面后再提取。

**Q: 支持哪些 Python 版本？**

A: 要求 Python 3.13 及以上版本。

**Q: 如何在 Claude Desktop 中使用？**

A: 参考 [MCP 服务文档](./magic-html-plus-python-mcp/README.md) 中的配置说明。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📜 许可证

MIT License

## 🙏 致谢

- 基于 [Readability](https://github.com/mozilla/readability) 算法
- MathML 转换使用 [mmltex](https://www.cs.bham.ac.uk/~vdg/mmltex/) 
- Model Context Protocol by [Anthropic](https://modelcontextprotocol.io/)

## 📞 联系方式

- 提交 Issue：[GitHub Issues](https://github.com/your-repo/issues)
- 查看文档：各子项目的 README 文件

---

**提示**: 各子项目有独立的详细文档，请查看对应目录下的 README.md 文件获取更多信息。
