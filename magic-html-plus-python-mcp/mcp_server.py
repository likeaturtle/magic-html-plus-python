#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MCP 服务器：提供网页内容提取工具

该服务器提供了以下工具：
1. extract_webpage - 从URL提取网页内容
2. extract_webpage_with_images - 从URL提取网页内容并下载图片
"""

import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, urljoin
from typing import Any

import requests
from bs4 import BeautifulSoup
from magic_html import GeneralExtractor
import hashlib
import time

from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP("magic-html-extractor")


def fetch_html(url: str) -> str:
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
        raise Exception(f"无法获取URL内容: {e}")


def extract_content(html: str, url: str, html_type: str = "article") -> dict:
    """提取HTML内容"""
    try:
        extractor = GeneralExtractor()
        data = extractor.extract(html, base_url=url, html_type=html_type)
        return data
    except Exception as e:
        raise Exception(f"提取内容失败: {e}")


def sanitize_dirname(name: str) -> str:
    """清理目录名，移除非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip()
    if len(name) > 100:
        name = name[:100]
    if not name:
        name = "untitled"
    return name


def format_html(html_content: str, remove_hidden_styles: bool = False) -> str:
    """格式化HTML内容"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if remove_hidden_styles:
            for elem in soup.find_all(style=True):
                style = elem.get('style', '')
                if 'visibility' in style or 'opacity' in style:
                    style = re.sub(r'visibility\s*:\s*hidden\s*;?', '', style)
                    style = re.sub(r'opacity\s*:\s*0\s*;?', '', style)
                    style = re.sub(r';\s*;', ';', style).strip()
                    if style:
                        elem['style'] = style
                    else:
                        del elem['style']
        
        return soup.prettify()
    except Exception:
        return html_content


def download_image(image_url: str, save_dir: str, base_url: str = "") -> str:
    """下载图片到本地"""
    try:
        if not image_url.startswith(('http://', 'https://')):
            if not base_url:
                return image_url
            image_url = urljoin(base_url, image_url)
        
        images_dir = os.path.join(save_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        ext = os.path.splitext(urlparse(image_url).path)[1]
        if not ext or len(ext) > 5:
            ext = '.jpg'
        
        filename = f"img_{url_hash}{ext}"
        filepath = os.path.join(images_dir, filename)
        
        if os.path.exists(filepath):
            return f"images/{filename}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': base_url if base_url else image_url
        }
        
        response = requests.get(image_url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        time.sleep(0.1)
        return f"images/{filename}"
    
    except Exception as e:
        return image_url


def html_to_markdown(html_content: str, title: str = "", download_images: bool = False, 
                     save_dir: str = "", base_url: str = "") -> str:
    """将HTML内容转换为Markdown格式"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        markdown_lines = []
        
        if title:
            markdown_lines.append(f"# {title}\n")
        
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
                if element.parent and element.parent.name == 'pre':
                    return [text]
                else:
                    result.append(f"`{text}`")
            
            elif tag_name == 'pre':
                code = element.get_text()
                result.append(f"\n```\n{code}\n```\n")
            
            elif tag_name == 'a':
                img_tag = element.find('img')
                if img_tag:
                    result.extend(process_element(img_tag, list_level, ordered))
                else:
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
                    header_row = rows[0]
                    headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
                    if headers:
                        result.append('| ' + ' | '.join(headers) + ' |\n')
                        result.append('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')
                    
                    for row in rows[1:] if len(rows) > 1 else []:
                        cells = [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                        if cells:
                            result.append('| ' + ' | '.join(cells) + ' |\n')
                result.append('\n')
            
            elif tag_name == 'hr':
                result.append('\n---\n\n')
            
            elif tag_name in ['div', 'section', 'article', 'span']:
                for child in element.children:
                    result.extend(process_element(child, list_level, ordered))
            
            else:
                for child in element.children:
                    result.extend(process_element(child, list_level, ordered))
            
            return result
        
        for child in soup.children:
            markdown_lines.extend(process_element(child))
        
        markdown_text = ''.join(markdown_lines)
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        markdown_text = markdown_text.strip()
        
        return markdown_text
    
    except Exception as e:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except:
            return html_content


def save_results(data: dict, output_dir: str, html_type: str = 'article', 
                download_images: bool = False, base_url: str = "") -> tuple:
    """保存数据为JSON、HTML和Markdown格式"""
    title = data.get('title', 'untitled')
    dir_name = sanitize_dirname(title)
    
    title_dir = os.path.join(output_dir, dir_name)
    os.makedirs(title_dir, exist_ok=True)
    
    json_filename = "content.json"
    json_path = os.path.join(title_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    html_path = None
    markdown_path = None
    html_content = data.get('html', '')
    
    if html_content:
        html_filename = "content.html"
        html_path = os.path.join(title_dir, html_filename)
        
        remove_hidden = (html_type == 'weixin')
        formatted_html = format_html(html_content, remove_hidden_styles=remove_hidden)
        
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
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        markdown_filename = "content.md"
        markdown_path = os.path.join(title_dir, markdown_filename)
        
        markdown_content = html_to_markdown(
            html_content, 
            title, 
            download_images=download_images,
            save_dir=title_dir,
            base_url=base_url or data.get('base_url', '')
        )
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    return title_dir, json_path, html_path, markdown_path


@mcp.tool()
def extract_webpage(
    url: str,
    html_type: str = "article",
    output_dir: str = "output",
    download_images: bool = True
) -> str:
    """
    从URL提取网页内容并保存为JSON、HTML和Markdown格式
    
    Args:
        url: 要解析的网页URL
        html_type: HTML类型，可选值: article（文章）, forum（论坛）, weixin（微信文章），默认为 article
        output_dir: 输出目录，默认为 output
        download_images: 是否下载图片到本地，默认为 True
    
    Returns:
        包含提取结果的JSON字符串，包括保存路径和内容摘要
    """
    try:
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            return json.dumps({
                "success": False,
                "error": "URL必须以 http:// 或 https:// 开头"
            }, ensure_ascii=False, indent=2)
        
        # 获取HTML
        html = fetch_html(url)
        
        # 提取内容
        data = extract_content(html, url, html_type)
        
        # 保存结果
        title_dir, json_path, html_path, markdown_path = save_results(
            data, 
            output_dir, 
            html_type,
            download_images=download_images,
            base_url=url
        )
        
        # 统计下载的图片数量
        downloaded_image_count = 0
        if download_images:
            images_dir = os.path.join(title_dir, 'images')
            if os.path.exists(images_dir):
                downloaded_image_count = len([
                    f for f in os.listdir(images_dir) 
                    if os.path.isfile(os.path.join(images_dir, f))
                ])
        
        # 构建返回结果
        result = {
            "success": True,
            "output_directory": title_dir,
            "files": {
                "json": json_path,
                "html": html_path,
                "markdown": markdown_path,
                "images_directory": os.path.join(title_dir, 'images') if downloaded_image_count > 0 else None
            },
            "summary": {
                "title": data.get('title', 'N/A'),
                "html_length": len(data.get('html', '')),
                "text_length": len(data.get('text', '')),
                "image_count": len(data.get('images', [])),
                "downloaded_image_count": downloaded_image_count
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def extract_webpage_with_images(
    url: str,
    html_type: str = "article",
    output_dir: str = "output"
) -> str:
    """
    从URL提取网页内容，下载图片到本地，并保存为JSON、HTML和Markdown格式
    
    Args:
        url: 要解析的网页URL
        html_type: HTML类型，可选值: article（文章）, forum（论坛）, weixin（微信文章），默认为 article
        output_dir: 输出目录，默认为 output
    
    Returns:
        包含提取结果的JSON字符串，包括保存路径、内容摘要和下载的图片数量
    """
    try:
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            return json.dumps({
                "success": False,
                "error": "URL必须以 http:// 或 https:// 开头"
            }, ensure_ascii=False, indent=2)
        
        # 获取HTML
        html = fetch_html(url)
        
        # 提取内容
        data = extract_content(html, url, html_type)
        
        # 保存结果（包含图片下载）
        title_dir, json_path, html_path, markdown_path = save_results(
            data, 
            output_dir, 
            html_type,
            download_images=True,
            base_url=url
        )
        
        # 统计下载的图片数量
        images_dir = os.path.join(title_dir, 'images')
        downloaded_image_count = 0
        if os.path.exists(images_dir):
            downloaded_image_count = len([
                f for f in os.listdir(images_dir) 
                if os.path.isfile(os.path.join(images_dir, f))
            ])
        
        # 构建返回结果
        result = {
            "success": True,
            "output_directory": title_dir,
            "files": {
                "json": json_path,
                "html": html_path,
                "markdown": markdown_path,
                "images_directory": images_dir if downloaded_image_count > 0 else None
            },
            "summary": {
                "title": data.get('title', 'N/A'),
                "html_length": len(data.get('html', '')),
                "text_length": len(data.get('text', '')),
                "image_count": len(data.get('images', [])),
                "downloaded_image_count": downloaded_image_count
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 运行 MCP 服务器
    mcp.run()
