# -*- coding:utf-8 -*-

from magic_html.utils import *
from magic_html.extractors.base_extractor import BaseExtractor
from magic_html.extractors.title_extractor import TitleExtractor


class WeixinExtractor(BaseExtractor):
    def __init__(self) -> None:
        super().__init__()

    def extract(self, html="", base_url="") -> dict:
        html = html.replace("&nbsp;", " ")
        tree = load_html(html)
        if tree is None:
            raise ValueError

        # 获取title
        title = TitleExtractor().process(tree)

        # base_url
        base_href = tree.xpath("//base/@href")

        if base_href and "http" in base_href[0]:
            base_url = base_href[0]

        # 文章区域
        try:
            body_tree_match = tree.xpath('.//*[@id="img-content"]')
            if not body_tree_match:
                body_tree_match = tree.xpath('.//*[@id="js_content"]')
            body_tree = body_tree_match[0]
        except:
            raise ValueError

        # 去除 js , style, comment
        for script in body_tree.xpath(".//script"):
            self.remove_node(script)
        for style in body_tree.xpath(".//style"):
            self.remove_node(style)
        for comment in body_tree.xpath(".//comment()"):
            self.remove_node(comment)

        # 删除所有的公众号介绍
        for mp in body_tree.xpath('.//div[@id="meta_content"]'):
            self.remove_node(mp)
        for mp in body_tree.xpath('.//div[@id="js_tags"]'):
            self.remove_node(mp)
        for mp in body_tree.xpath('.//div[@class="original_area_primary"]'):
            self.remove_node(mp)
            # 隐藏的封禁 介绍
        for mp in body_tree.xpath('.//section[@class="wx_profile_card_inner"]'):
            self.remove_node(mp)
            # 特殊的wx卡片介绍
        for mp in body_tree.xpath(
                ".//section[contains(@class, 'wx_profile_msg_inner')]"
        ):
            self.remove_node(mp)

        #  针对杂乱内容进行去除
        all_raga = body_tree.xpath(
            ".//*[contains(@style, 'color: rgba(255, 255, 255, 0)')] | .//*[contains(@style, 'color: rgba(255 255 255 0)')]"
        )

        for mp in all_raga:
            flag_have_color_rgb, detail_style = self.ensure_have_color_rgb(
                mp.attrib["style"]
            )

            if not flag_have_color_rgb:
                continue
            self.remove_node(mp)

        # 处理图片的 data-src 属性
        # 微信文章使用懒加载，真实图片地址在 data-src 中
        for img in body_tree.xpath(".//img"):
            # 如果有 data-src，将其设置为 src（覆盖原有的 src）
            if "data-src" in img.attrib:
                try:
                    img.set("src", img.attrib["data-src"])
                except Exception as e:
                    continue

        for h1 in body_tree.xpath(".//h1"):
            if not h1.text:
                continue
            h1.text = h1.text.replace("\n", "").strip()

        # 移除所有元素的 visibility: hidden 和 opacity: 0 样式
        for elem in body_tree.xpath(".//*[@style]"):
            style = elem.get("style", "")
            if "visibility" in style or "opacity" in style:
                # 移除 visibility 和 opacity 属性
                style = re.sub(r'visibility\s*:\s*hidden\s*;?', '', style)
                style = re.sub(r'opacity\s*:\s*0\s*;?', '', style)
                # 清理多余的分号和空格
                style = re.sub(r';\s*;', ';', style).strip()
                if style and not style.endswith(';'):
                    style += ';'
                elem.set("style", style)

        body_html = tostring(body_tree, encoding=str)

        return {
            "xp_num": "weixin",
            "drop_list": False,
            "html": body_html,
            "title": title,
            "base_url": base_url
        }

    @staticmethod
    def ensure_have_color_rgb(htmlstr):
        pattern = r"(?<!-)\bcolor\s*:\s*rgba\(\s*255\s*[,|\s]\s*255\s*[,|\s]\s*255\s*[,|\s]\s*0\s*\)"

        result = re.search(pattern, htmlstr)
        if result:
            return True, result.group()
        else:
            return False, ""