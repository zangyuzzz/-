# -*- coding: utf-8 -*-
"""
作者：飞鱼
ppp.porn 爬虫 (XYQHiker 规则转换 Python 适配版)
适配壳子: PeekPro(羊壳) / TVBox / 影视壳 / 猫影视
"""
import sys
import re
import json
import requests
import urllib3
import time
import html
from urllib.parse import quote, urljoin, unquote

urllib3.disable_warnings()
sys.path.append('..')
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    host = 'https://ppp.porn'
    session = requests.Session()
    _debug = True
    _categories = []

    # 广告过滤词与域名黑名单
    AD_TITLE_FILTER = ['广告', '推广', 'APP', '下载', '注册', '菠菜', '博彩', '棋牌']
    AD_DOMAIN_FILTER = ['doubleclick', 'adservice', 'adsystem', 'adnxs', 'casalemedia', 'fluxtrck']

    def _log(self, msg):
        if self._debug:
            print(f'[ppp.porn] {msg}')

    def getName(self):
        return 'PPP-Porn'

    def isVideoFormat(self, url):
        return url and ('.m3u8' in url or '.mp4' in url or '.ts' in url)

    def manualVideoCheck(self):
        return False

    def destroy(self):
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except:
                pass
            self.session = None

    # ---------- 清洗文本与 HTML 实体 (解决字符乱码/转义问题) ----------
    def _clean_text(self, text):
        if not text:
            return ''
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), clean)
        clean = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), clean)
        clean = html.unescape(clean)
        clean = html.unescape(clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def _get_headers(self, referer=None):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': referer or self.host + '/'
        }

    def _fetch(self, url, referer=None, retries=2):
        for attempt in range(retries):
            try:
                if attempt > 0:
                    time.sleep(1)
                r = self.session.get(url, headers=self._get_headers(referer), timeout=(10, 15), verify=False)
                r.encoding = 'utf-8'
                if r.status_code == 200:
                    return r.text
            except Exception as e:
                self._log(f'请求异常 {e} -> {url}')
                continue
        return ''

    # ---------- 初始化与分类/筛选 ----------
    def init(self, extend=''):
        self._log('正在初始化...')
        self.session = requests.Session()
        self._categories = [
            {'type_id': 'new', 'type_name': '最新'},
            {'type_id': 'hot', 'type_name': '🔥热门🔥'},
            {'type_id': 'categories/china-av', 'type_name': '系列'},
            {'type_id': 'categories/china', 'type_name': '地区'},
            {'type_id': 'categories/cosplay', 'type_name': '主题'},
            {'type_id': 'categories/office-lady', 'type_name': '衣着'}
        ]

    def _get_filters(self):
        return {
            "categories/china-av": [
                {"key": "cateId", "name": "系列", "value": [
                    {"v": "categories/china-av", "n": "中國AV"},
                    {"v": "categories/japan-producer", "n": "日本片商"},
                    {"v": "categories/amateur", "n": "素人自拍"}
                ]}
            ],
            "categories/china": [
                {"key": "cateId", "name": "地区", "value": [
                    {"v": "categories/china", "n": "中國"},
                    {"v": "categories/taiwan", "n": "台灣"},
                    {"v": "categories/japan", "n": "日本"},
                    {"v": "categories/se-asia", "n": "東南亞"},
                    {"v": "categories/korea", "n": "韓國"},
                    {"v": "categories/hongkong", "n": "香港"}
                ]}
            ],
            "categories/cosplay": [
                {"key": "cateId", "name": "主题", "value": [
                    {"v": "categories/cosplay", "n": "Cosplay"},
                    {"v": "categories/streamer", "n": "主播"},
                    {"v": "categories/first-person-pov", "n": "主觀視角"},
                    {"v": "categories/bdsm", "n": "凌辱"},
                    {"v": "categories/drama", "n": "劇情"},
                    {"v": "categories/threesome", "n": "多P"},
                    {"v": "categories/91-tanhua", "n": "探花"},
                    {"v": "categories/leaked", "n": "流出"},
                    {"v": "categories/uncensored", "n": "無碼"},
                    {"v": "categories/lesbian", "n": "百合"},
                    {"v": "categories/exhibitionists", "n": "野外露出"}
                ]}
            ],
            "categories/office-lady": [
                {"key": "cateId", "name": "衣着", "value": [
                    {"v": "categories/office-lady", "n": "OL"},
                    {"v": "categories/acg", "n": "動漫"},
                    {"v": "categories/costume", "n": "古裝"},
                    {"v": "categories/maid", "n": "女僕"},
                    {"v": "categories/student", "n": "學生"},
                    {"v": "categories/cheongsam", "n": "旗袍"},
                    {"v": "categories/kemonomimi", "n": "獸耳"},
                    {"v": "categories/yoga-pants", "n": "瑜伽褲"},
                    {"v": "categories/dolfin-shorts", "n": "真理褲"},
                    {"v": "categories/flight-attendant", "n": "空姐"},
                    {"v": "categories/pantyhose", "n": "絲襪"},
                    {"v": "categories/nurse", "n": "護士"},
                    {"v": "categories/knee-socks", "n": "過膝襪"}
                ]}
            ]
        }

    # ---------- 解析网页 HTML 卡片列表 ----------
    def _parse_item_list(self, html_str, is_home=False):
        items = []
        if not html_str:
            return items

        # 1. 截取卡片包含区域
        if is_home:
            container_match = re.search(r'class="[^"]*max-width-lg[^"]*"[^>]*>(.*?)(?=<footer|</body>|$)', html_str, re.S)
        else:
            container_match = re.search(r'class="[^"]*padding-bottom-md[^"]*"[^>]*>(.*?)(?=<footer|</body>|$)', html_str, re.S)
        
        target_html = container_match.group(1) if container_match else html_str

        # 2. 提取原始视频卡片块 (.item)
        raw_blocks = re.findall(r'<div[^>]+class="[^"]*item[^"]*"[^>]*>(.*?)(?=<div[^>]+class="[^"]*item[^"]*"|$)', target_html, re.S)

        # 3. 拆分卡片内嵌套的 end-sc 隐藏层广告
        sub_blocks = []
        for b in raw_blocks:
            if 'end-sc' in b:
                parts = re.split(r'<style>\s*\.end-sc\s*~\s*\*[^}]*</style>', b)
                sub_blocks.extend(parts)
            else:
                sub_blocks.append(b)

        # 4. 解析每个独立卡片
        