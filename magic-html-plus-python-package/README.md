# Magic HTML Plus - Python 包

一个强大的 Python 网页内容提取库，基于智能算法自动识别和提取网页正文内容，支持文章、论坛、微信公众号等多种网页类型。

## 功能特性

- 🎯 **智能提取** - 自动识别网页正文内容，无需手动配置
- 📰 **多类型支持** - 支持文章、论坛帖子、微信公众号等多种网页类型
- 🎨 **内容清洗** - 自动清除广告、导航栏等无关内容
- 🔧 **自定义规则** - 支持通过 XPath 或 CSS 选择器自定义提取规则
- 📐 **数学公式** - 支持 MathML 转 LaTeX
- 🖼️ **图片处理** - 自动转换相对路径为绝对路径
- 📄 **格式输出** - 返回结构化的 HTML 和元数据

## 安装

### 开发环境安装

#### 使用 pip 安装

```bash
pip install -r requirements.txt
```

#### 使用 uv 安装（推荐）

```bash
uv sync
```

### 打包和发布

#### 1. 构建发行版

**使用 uv 构建（推荐）**

uv 提供了更快速的打包方式：

```bash
# 使用 uv 直接构建
uv build
```

**使用传统 build 工具**

```bash
# 安装构建工具
pip install build

# 构建包（生成 dist/ 目录）
python -m build
```

构建完成后，在 `dist/` 目录下会生成两个文件：
- `magic-html-plus-python-package-0.1.0.tar.gz` - 源码分发包
- `magic_html_plus_python_package-0.1.0-py3-none-any.whl` - wheel 包

#### 2. 本地安装打包后的包

**使用 uv 安装（推荐）**

```bash
# 安装 wheel 包
uv pip install dist/magic_html_plus_python_package-0.1.0-py3-none-any.whl

# 或者安装源码包
uv pip install dist/magic-html-plus-python-package-0.1.0.tar.gz
```

**使用传统 pip 安装**

```bash
# 安装 wheel 包
pip install dist/magic_html_plus_python_package-0.1.0-py3-none-any.whl

# 或者安装源码包
pip install dist/magic-html-plus-python-package-0.1.0.tar.gz
```

#### 3. 发布到 PyPI

**使用 uv 发布（推荐）**

```bash
# 发布到 PyPI（需要先配置 PyPI 认证）
uv publish

# 发布到测试 PyPI
uv publish --publish-url https://test.pypi.org/legacy/
```

**使用 twine 发布**

```bash
# 安装 twine
pip install twine

# 上传到 PyPI（需要先注册 PyPI 账号）
twine upload dist/*

# 上传到测试 PyPI（用于测试）
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

#### 4. 从 PyPI 安装

发布后，其他用户可以直接安装：

**使用 uv 安装（推荐）**

```bash
uv pip install magic-html-plus-python-package
```

**使用 pip 安装**

```bash
pip install magic-html-plus-python-package
```

#### 注意事项

- 发布前请确保更新 `pyproject.toml` 中的版本号
- 建议先上传到 Test PyPI 进行测试
- 确保所有依赖项都在 `pyproject.toml` 中正确声明
- 包含的 XSL 文件已在 `pyproject.toml` 的 `package-data` 中配置
- 使用 uv 发布时，需要先配置环境变量 `UV_PUBLISH_TOKEN` 或使用 `--token` 参数

## 依赖项

- `lxml` - HTML/XML 解析和处理
- `numpy` - 数值计算支持
- `charset-normalizer` - 字符编码检测
- `urllib3` - URL 处理
- `brotli` - Brotli 压缩支持
- `py-asciimath` - 数学公式处理

## 快速开始

### 基本用法

```python
from magic_html import GeneralExtractor

# 创建提取器实例
extractor = GeneralExtractor()

# 从 HTML 字符串提取内容
html = """<html>...</html>"""
result = extractor.extract(html=html, base_url="https://example.com")

# 结果包含
print(result['title'])      # 标题
print(result['html'])       # 提取的正文 HTML
print(result['base_url'])   # 基础 URL
```

### 指定网页类型

```python
# 提取文章（默认）
result = extractor.extract(html=html, base_url=url)

# 提取论坛帖子
result = extractor.extract(html=html, base_url=url, html_type="forum")

# 提取微信公众号文章
result = extractor.extract(html=html, base_url=url, html_type="weixin")
```

### 使用自定义规则

创建规则配置文件 `rules.json`：

```json
{
  "www.example.com": {
    "clean": ["//script", "//style", "//div[@class='ads']"],
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

使用规则：

```python
extractor = GeneralExtractor(config_path="rules.json")
result = extractor.extract(html=html, base_url="https://www.example.com/article")
```

## API 文档

### GeneralExtractor

主提取器类，自动选择合适的提取策略。

#### `__init__(config_path="")`

初始化提取器。

**参数：**
- `config_path` (str, 可选): 自定义规则配置文件路径

#### `extract(html="", **kwargs) -> dict`

从 HTML 提取内容。

**参数：**
- `html` (str): HTML 字符串
- `base_url` (str, 可选): 网页基础 URL
- `html_type` (str, 可选): 网页类型，可选值：
  - `article` - 文章（默认）
  - `forum` - 论坛帖子
  - `weixin` - 微信公众号文章

**返回值：**

```python
{
    "title": "文章标题",
    "html": "提取的正文 HTML",
    "base_url": "基础 URL",
    "xp_num": "xpath 数量标识",
    "drop_list": []  # 被移除的节点列表
}
```

## 项目结构

```
magic-html-plus-python-package/
├── magic_html/                  # 主包
│   ├── __init__.py             # GeneralExtractor 入口
│   ├── config.py               # 配置项
│   ├── utils.py                # 工具函数
│   ├── readability_plus.py     # 可读性算法增强版
│   ├── extractors/             # 提取器模块
│   │   ├── base_extractor.py  # 基础提取器
│   │   ├── article_extractor.py    # 文章提取器
│   │   ├── forum_extractor.py      # 论坛提取器
│   │   ├── weixin_extractor.py     # 微信公众号提取器
│   │   ├── custom_extractor.py     # 自定义规则提取器
│   │   └── title_extractor.py      # 标题提取器
│   └── mmltex/                 # MathML 转 LaTeX
│       └── *.xsl               # XSL 转换模板
├── benchmark/                  # 基准测试
│   ├── data/                   # 测试数据
│   ├── evaluate_articles.py    # 文章评估
│   └── evaluate_forums.py      # 论坛评估
├── main.py                     # 命令行入口
├── pyproject.toml              # 项目配置
└── requirements.txt            # 依赖列表
```

## 提取器说明

### ArticleExtractor（文章提取器）

适用于新闻文章、博客文章等内容页面，使用基于密度和可读性的算法自动识别正文。

**特点：**
- 自动识别标题
- 智能清除广告和导航
- 支持数学公式（MathML）
- 自动处理图片路径

### ForumExtractor（论坛提取器）

专门用于论坛帖子、问答网站等包含多条评论或回复的页面。

**特点：**
- 识别楼层结构
- 保留用户信息
- 处理引用和回复

### WeixinExtractor（微信公众号提取器）

针对微信公众号文章优化的提取器。

**特点：**
- 处理微信特有的标签结构
- 保留原始样式
- 优化图片处理

### CustomExtractor（自定义提取器）

基于用户自定义规则的提取器，通过配置 XPath 或 CSS 选择器实现精确提取。

**规则格式：**
```json
{
  "clean": ["//script", "//div[@class='ads']"],
  "title": {
    "mode": "xpath",
    "value": "//h1/text()"
  },
  "content": {
    "mode": "xpath",
    "value": "//div[@class='content']"
  }
}
```

## 基准测试

项目包含针对文章和论坛的基准测试集：

```bash
# 评估文章提取效果
uv run benchmark/evaluate_articles.py

# 评估论坛提取效果
uv run benchmark/evaluate_forums.py
```

测试数据位于 `benchmark/data/` 目录下。

## 高级用法

### 处理编码问题

```python
import chardet

# 检测编码
raw_html = response.content
encoding = chardet.detect(raw_html)['encoding']
html = raw_html.decode(encoding)

# 提取
result = extractor.extract(html=html, base_url=url)
```

### 批量处理

```python
urls = ["url1", "url2", "url3"]
results = []

for url in urls:
    html = fetch_html(url)  # 你的获取函数
    result = extractor.extract(html=html, base_url=url)
    results.append(result)
```

## 常见问题

**Q: 提取的内容不完整怎么办？**

A: 可以尝试：
1. 指定正确的 `html_type`
2. 使用自定义规则配置
3. 检查 HTML 是否完整加载（某些网站使用 JavaScript 动态加载）

**Q: 如何处理动态加载的网页？**

A: 本库处理的是静态 HTML。对于动态网页，建议先使用 Selenium 或 Playwright 渲染完整页面后再提取。

**Q: 支持哪些 Python 版本？**

A: 要求 Python 3.13+

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关项目

- [magic-html-plus-python-mcp](../magic-html-plus-python-mcp/) - 基于 MCP 的网页提取服务
- [magic-html-plus-python-program](../magic-html-plus-python-program/) - 命令行程序包装

## 致谢

本项目基于 Readability 算法并进行了增强优化。
