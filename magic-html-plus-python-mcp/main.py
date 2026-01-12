#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令行工具：从URL提取网页内容并保存为JSON格式

Usage:
    python main.py <url> [--type article|forum|weixin] [--output-dir output]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from magic_html import GeneralExtractor
import hashlib
import time


def fetch_html(url):
    """从URL获取HTML内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.RequestException as e:
        print(f"错误：无法获取URL内容 - {e}", file=sys.stderr)
        sys.exit(1)


def extract_content(html, url, html_type="article"):
    """提取HTML内容"""
    try:
        extractor = GeneralExtractor()
        data = extractor.extract(html, base_url=url, html_type=html_type)
        return data
    except Exception as e:
        print(f"错误：提取内容失败 - {e}", file=sys.stderr)
        sys.exit(1)


def sanitize_dirname(name):
    """清理目录名，移除非法字符"""
    # 移除或替换Windows/Unix文件系统不允许的字符
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除前后空格
    name = name.strip()
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    # 如果为空，使用默认名称
    if not name:
        name = "untitled"
    return name


def generate_filename(url):
    """根据URL生成文件名"""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{domain}_{timestamp}.json"


def format_html(html_content, remove_hidden_styles=False):
    """格式化HTML内容
    
    Args:
        html_content: HTML内容字符串
        remove_hidden_styles: 是否移除 visibility:hidden 和 opacity:0 样式
                             (主要用于微信文章的显示修复)
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 仅在需要时移除隐藏样式（主要用于微信文章）
        if remove_hidden_styles:
            for elem in soup.find_all(style=True):
                style = elem.get('style', '')
                if 'visibility' in style or 'opacity' in style:
                    # 移除 visibility 和 opacity 属性
                    style = re.sub(r'visibility\s*:\s*hidden\s*;?', '', style)
                    style = re.sub(r'opacity\s*:\s*0\s*;?', '', style)
                    # 清理多余的分号和空格
                    style = re.sub(r';\s*;', ';', style).strip()
                    if style:
                        elem['style'] = style
                    else:
                        # 如果style为空，移除style属性
                        del elem['style']
        
        return soup.prettify()
    except Exception:
        # 如果格式化失败，返回原始内容
        return html_content


def download_image(image_url, save_dir, base_url=""):
    """下载图片到本地
    
    Args:
        image_url: 图片URL
        save_dir: 保存目录
        base_url: 基础URL，用于处理相对路径
    
    Returns:
        本地文件路径（相对于save_dir的父目录），如果下载失败则返回原URL
    """
    try:
        # 处理相对URL
        if not image_url.startswith(('http://', 'https://')):
            if not base_url:
                return image_url
            image_url = urljoin(base_url, image_url)
        
        # 创建images子目录
        images_dir = os.path.join(save_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # 生成文件名（使用URL的hash值避免文件名冲突）
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        
        # 尝试从URL获取文件扩展名
        ext = os.path.splitext(urlparse(image_url).path)[1]
        if not ext or len(ext) > 5:
            ext = '.jpg'  # 默认扩展名
        
        filename = f"img_{url_hash}{ext}"
        filepath = os.path.join(images_dir, filename)
        
        # 如果文件已存在，直接返回路径
        if os.path.exists(filepath):
            return f"images/{filename}"
        
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': base_url if base_url else image_url
        }
        
        response = requests.get(image_url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()
        
        # 保存图片
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # 添加小延迟，避免请求过快
        time.sleep(0.1)
        
        return f"images/{filename}"
    
    except Exception as e:
        print(f"  警告：图片下载失败 {image_url}: {e}", file=sys.stderr)
        return image_url  # 下载失败时返回原URL


def html_to_markdown(html_content, title="", download_images=False, save_dir="", base_url=""):
    """将HTML内容转换为Markdown格式
    
    Args:
        html_content: HTML内容字符串
        title: 文章标题
        download_images: 是否下载图片到本地
        save_dir: 保存目录（用于下载图片）
        base_url: 基础URL（用于处理相对路径）
    
    Returns:
        Markdown格式的文本
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        markdown_lines = []
        
        # 添加标题
        if title:
            markdown_lines.append(f"# {title}\n")
        
        # 遍历处理HTML元素
        def process_element(element, list_level=0, ordered=False):
            """递归处理HTML元素转换为Markdown"""
            result = []
            
            if isinstance(element, str):
                text = element.strip()
                if text:
                    return [text]
                return []
            
            tag_name = element.name if hasattr(element, 'name') else None
            
            if tag_name is None:
                return []
            
            # 处理各种HTML标签
            if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(tag_name[1])
                text = element.get_text().strip()
                if text:
                    result.append(f"\n{'#' * level} {text}\n")
            
            elif tag_name == 'p':
                text = ''
                for child in element.children:
                    text += ''.join(process_element(child, list_level, ordered))
                if text.strip():
                    result.append(f"\n{text.strip()}\n")
            
            elif tag_name == 'br':
                result.append('  \n')
            
            elif tag_name in ['strong', 'b']:
                text = element.get_text().strip()
                if text:
                    result.append(f"**{text}**")
            
            elif tag_name in ['em', 'i']:
                text = element.get_text().strip()
                if text:
                    result.append(f"*{text}*")
            
            elif tag_name == 'code':
                text = element.get_text()
                # 检查是否在pre标签内（代码块）
                if element.parent and element.parent.name == 'pre':
                    return [text]
                else:
                    result.append(f"`{text}`")
            
            elif tag_name == 'pre':
                code = element.get_text()
                result.append(f"\n```\n{code}\n```\n")
            
            elif tag_name == 'a':
                # 检查是否包含图片
                img_tag = element.find('img')
                if img_tag:
                    # 如果链接内包含图片，处理图片而不是链接文本
                    result.extend(process_element(img_tag, list_level, ordered))
                else:
                    # 普通链接
                    text = element.get_text().strip()
                    href = element.get('href', '')
                    if text and href:
                        result.append(f"[{text}]({href})")
                    elif text:
                        result.append(text)
            
            elif tag_name == 'img':
                alt = element.get('alt', '图片')
                src = element.get('src', '')
                if src:
                    # 如果需要下载图片，下载并使用本地路径
                    if download_images and save_dir:
                        local_path = download_image(src, save_dir, base_url)
                        result.append(f"\n![{alt}]({local_path})\n")
                    else:
                        result.append(f"\n![{alt}]({src})\n")
            
            elif tag_name in ['ul', 'ol']:
                result.append('\n')
                is_ordered = (tag_name == 'ol')
                for idx, li in enumerate(element.find_all('li', recursive=False)):
                    li_content = ''.join(process_element(li, list_level + 1, is_ordered))
                    if li_content.strip():
                        indent = '  ' * list_level
                        if is_ordered:
                            result.append(f"{indent}{idx + 1}. {li_content.strip()}\n")
                        else:
                            result.append(f"{indent}- {li_content.strip()}\n")
                result.append('\n')
            
            elif tag_name == 'li':
                # li标签在ul/ol处理中已经处理，这里处理子元素
                for child in element.children:
                    result.extend(process_element(child, list_level, ordered))
            
            elif tag_name == 'blockquote':
                text = element.get_text().strip()
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            result.append(f"> {line.strip()}\n")
                    result.append('\n')
            
            elif tag_name == 'table':
                result.append('\n')
                rows = element.find_all('tr')
                if rows:
                    # 处理表头
                    header_row = rows[0]
                    headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
                    if headers:
                        result.append('| ' + ' | '.join(headers) + ' |\n')
                        result.append('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')
                    
                    # 处理数据行
                    for row in rows[1:] if len(rows) > 1 else []:
                        cells = [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                        if cells:
                            result.append('| ' + ' | '.join(cells) + ' |\n')
                result.append('\n')
            
            elif tag_name == 'hr':
                result.append('\n---\n\n')
            
            elif tag_name in ['div', 'section', 'article', 'span']:
                # 递归处理子元素
                for child in element.children:
                    result.extend(process_element(child, list_level, ordered))
            
            else:
                # 其他标签，提取文本内容
                for child in element.children:
                    result.extend(process_element(child, list_level, ordered))
            
            return result
        
        # 处理body内容
        for child in soup.children:
            markdown_lines.extend(process_element(child))
        
        # 合并并清理结果
        markdown_text = ''.join(markdown_lines)
        
        # 清理多余的空行
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        markdown_text = markdown_text.strip()
        
        return markdown_text
    
    except Exception as e:
        # 如果转换失败，返回纯文本
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except:
            return html_content


def save_results(data, output_dir, html_type='article', download_images=False, base_url=""):
    """保存数据为JSON、HTML和Markdown格式
    
    Args:
        data: 提取的数据字典
        output_dir: 输出目录
        html_type: HTML类型，用于判断是否需要特殊处理
        download_images: 是否下载图片到本地
        base_url: 基础URL（用于图片下载）
    
    Returns:
        包含目录路径和各文件路径的元组
    """
    # 获取标题并清理
    title = data.get('title', 'untitled')
    dir_name = sanitize_dirname(title)
    
    # 创建以标题命名的子目录
    title_dir = os.path.join(output_dir, dir_name)
    os.makedirs(title_dir, exist_ok=True)
    
    # 保存JSON文件
    json_filename = "content.json"
    json_path = os.path.join(title_dir, json_filename)
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"错误：保存JSON文件失败 - {e}", file=sys.stderr)
        sys.exit(1)
    
    html_path = None
    markdown_path = None
    html_content = data.get('html', '')
    
    # 保存格式化的HTML文件
    if html_content:
        html_filename = "content.html"
        html_path = os.path.join(title_dir, html_filename)
        
        # 格式化HTML（微信类型需要移除隐藏样式）
        remove_hidden = (html_type == 'weixin')
        formatted_html = format_html(html_content, remove_hidden_styles=remove_hidden)
        
        # 创建完整的HTML文档
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>{title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
{formatted_html}
</body>
</html>"""
        
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
        except Exception as e:
            print(f"错误：保存HTML文件失败 - {e}", file=sys.stderr)
            sys.exit(1)
        
        # 保存Markdown文件
        markdown_filename = "content.md"
        markdown_path = os.path.join(title_dir, markdown_filename)
        
        try:
            if download_images:
                print("  正在下载图片...")
            markdown_content = html_to_markdown(
                html_content, 
                title, 
                download_images=download_images,
                save_dir=title_dir,
                base_url=base_url or data.get('base_url', '')
            )
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            if download_images:
                # 检查是否有下载的图片
                images_dir = os.path.join(title_dir, 'images')
                if os.path.exists(images_dir):
                    image_count = len([f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))])
                    if image_count > 0:
                        print(f"  ✓ 已下载 {image_count} 张图片")
        except Exception as e:
            print(f"警告：保存Markdown文件失败 - {e}", file=sys.stderr)
            markdown_path = None
    
    return title_dir, json_path, html_path, markdown_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='从URL提取网页内容并保存为JSON、HTML和Markdown格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py https://example.com
  python main.py https://example.com --type forum
  python main.py https://example.com --type weixin --output-dir my_output
  python main.py https://example.com --download-images  # 下载图片到本地
        """
    )
    
    parser.add_argument('url', help='要解析的网页URL')
    parser.add_argument(
        '--type',
        choices=['article', 'forum', 'weixin'],
        default='article',
        help='HTML类型 (默认: article)'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='输出目录 (默认: output)'
    )
    parser.add_argument(
        '--download-images',
        action='store_true',
        help='下载图片到本地（Markdown中使用相对路径）'
    )
    
    args = parser.parse_args()
    
    # 验证URL
    if not args.url.startswith(('http://', 'https://')):
        print("错误：URL必须以 http:// 或 https:// 开头", file=sys.stderr)
        sys.exit(1)
    
    print(f"正在获取URL: {args.url}")
    html = fetch_html(args.url)
    
    print(f"正在提取内容 (类型: {args.type})...")
    data = extract_content(html, args.url, args.type)
    
    print(f"正在保存到 {args.output_dir} 目录...")
    title_dir, json_path, html_path, markdown_path = save_results(
        data, 
        args.output_dir, 
        args.type,
        download_images=args.download_images,
        base_url=args.url
    )
    
    print(f"✓ 成功！结果已保存到目录: {title_dir}")
    print(f"  - JSON文件: {json_path}")
    if html_path:
        print(f"  - HTML文件: {html_path}")
    if markdown_path:
        print(f"  - Markdown文件: {markdown_path}")
    print(f"\n提取的数据摘要:")
    print(f"  - 标题: {data.get('title', 'N/A')}")
    print(f"  - HTML长度: {len(data.get('html', ''))} 字符")
    print(f"  - 纯文本长度: {len(data.get('text', ''))} 字符")
    if 'images' in data:
        print(f"  - 图片数量: {len(data.get('images', []))}")


if __name__ == '__main__':
    main()
