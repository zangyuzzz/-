# -*- coding: utf-8 -*-
# 🌈 Love 
import json
import random
import re
import sys
import threading
import time
from base64 import b64decode, b64encode
from urllib.parse import urlparse, quote

import requests
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        try:self.proxies = json.loads(extend)
        except:self.proxies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        # Use working dynamic URLs directly
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        self.log(f"使用站点: {self.host}")
        print(f"使用站点: {self.host}")
        pass

    def getName(self):
        return "🌈 今日看料"

    def isVideoFormat(self, url):
        # Treat direct media formats as playable without parsing
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def homeContent(self, filter):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'class': [], 'list': []}
                
            data = self.getpq(response.text)
            result = {}
            classes = []
            
            # 优先从导航栏获取分类
            nav_selectors = [
                '#navbarCollapse .navbar-nav .nav-item .nav-link',
                '.navbar-nav .nav-item .nav-link',
                '#nav .menu-item a',
                '.menu .menu-item a'
            ]
            
            found_categories = False
            for selector in nav_selectors:
                for item in data(selector).items():
                    href = item.attr('href') or ''
                    name = item.text().strip()
                    
                    # 过滤掉非分类链接
                    if (not href or not name or 
                        href == '#' or 
                        href.startswith('http') or
                        'about' in href.lower() or
                        'contact' in href.lower() or
                        'tags' in href.lower() or
                        'top' in href.lower() or
                        'start' in href.lower() or
                        'time' in href.lower()):
                        continue
                    
                    # 确保是分类链接（包含category或明确的分类路径）
                    if '/category/' in href or any(cat in href for cat in ['/dy/', '/ks/', '/douyu/', '/hy/', '/hj/', '/tt/', '/wh/', '/asmr/', '/xb/', '/xsp/', '/rdgz/']):
                        # 处理相对路径
                        if href.startswith('/'):
                            type_id = href
                        else:
                            type_id = f'/{href}'
                            
                        classes.append({
                            'type_name': name,
                            'type_id': type_id
                        })
                        found_categories = True
            
            # 如果导航栏没找到，尝试从分类下拉菜单获取
            if not found_categories:
                category_selectors = [
                    '.category-list a',
                    '.slide-toggle + .category-list a',
                    '.menu .category-list a'
                ]
                for selector in category_selectors:
                    for item in data(selector).items():
                        href = item.attr('href') or ''
                        name = item.text().strip()
                        
                        if href and name and href != '#':
                            if href.startswith('/'):
                                type_id = href
                            else:
                                type_id = f'/{href}'
                                
                            classes.append({
                                'type_name': name,
                                'type_id': type_id
                            })
                            found_categories = True
            
            # 去重
            unique_classes = []
            seen_ids = set()
            for cls in classes:
                if cls['type_id'] not in seen_ids:
                    unique_classes.append(cls)
                    seen_ids.add(cls['type_id'])
            
            # 如果没有找到分类，创建默认分类
            if not unique_classes:
                unique_classes = [
                    {'type_name': '热点关注', 'type_id': '/category/rdgz/'},
                    {'type_name': '抖音', 'type_id': '/category/dy/'},
                    {'type_name': '快手', 'type_id': '/category/ks/'},
                    {'type_name': '斗鱼', 'type_id': '/category/douyu/'},
                    {'type_name': '虎牙', 'type_id': '/category/hy/'},
                    {'type_name': '花椒', 'type_id': '/category/hj/'},
                    {'type_name': '推特', 'type_id': '/category/tt/'},
                    {'type_name': '网红', 'type_id': '/category/wh/'},
                    {'type_name': 'ASMR', 'type_id': '/category/asmr/'},
                    {'type_name': 'X播', 'type_id': '/category/xb/'},
                    {'type_name': '小视频', 'type_id': '/category/xsp/'}
                ]
            
            result['class'] = unique_classes
            result['list'] = self.getlist(data('#index article a, #archive article a'))
            return result
            
        except Exception as e:
            print(f"homeContent error: {e}")
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article a, #archive article a'))}
        except Exception as e:
            print(f"homeVideoContent error: {e}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            # 修复URL构建 - 去除多余的斜杠
            base_url = tid.lstrip('/').rstrip('/')
            if pg and pg != '1':
                url = f"{self.host}{base_url}/{pg}/"
            else:
                url = f"{self.host}{base_url}/"
                
            print(f"分类页面URL: {url}")
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                print(f"分类页面请求失败: {response.status_code}")
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'), tid)
            
            # 如果没有找到视频，尝试其他选择器
            if not videos:
                videos = self.getlist(data('article a, .post a, .entry-title a'), tid)
            
            print(f"找到 {len(videos)} 个视频")
            
            # 改进的页数检测逻辑
            pagecount = self.detect_page_count(data, pg)
            
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def tagContent(self, tid, pg, filter, extend):
        """标签页面内容"""
        try:
            # 修复URL构建 - 去除多余的斜杠
            base_url = tid.lstrip('/').rstrip('/')
            if pg and pg != '1':
                url = f"{self.host}{base_url}/{pg}/"
            else:
                url = f"{self.host}{base_url}/"
                
            print(f"标签页面URL: {url}")
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                print(f"标签页面请求失败: {response.status_code}")
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'), tid)
            
            # 如果没有找到视频，尝试其他选择器
            if not videos:
                videos = self.getlist(data('article a, .post a, .entry-title a'), tid)
            
            print(f"找到 {len(videos)} 个标签相关视频")
            
            # 页数检测
            pagecount = self.detect_page_count(data, pg)
            
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"tagContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def detect_page_count(self, data, current_page):
        """改进的页数检测方法"""
        pagecount = 99999  # 默认大数字，允许无限翻页
        
        # 方法1: 检查分页器中的所有页码链接
        page_numbers = []
        
        # 查找所有可能的页码链接
        page_selectors = [
            '.page-navigator a',
            '.pagination a', 
            '.pages a',
            '.page-numbers a'
        ]
        
        for selector in page_selectors:
            for page_link in data(selector).items():
                href = page_link.attr('href') or ''
                text = page_link.text().strip()
                
                # 从href中提取页码
                if href:
                    # 匹配 /category/dy/2/ 这种格式
                    match = re.search(r'/(\d+)/?$', href.rstrip('/'))
                    if match:
                        page_num = int(match.group(1))
                        if page_num not in page_numbers:
                            page_numbers.append(page_num)
                
                # 从文本中提取数字页码
                if text and text.isdigit():
                    page_num = int(text)
                    if page_num not in page_numbers:
                        page_numbers.append(page_num)
        
        # 如果有找到页码，取最大值
        if page_numbers:
            max_page = max(page_numbers)
            print(f"从分页器检测到最大页码: {max_page}")
            return max_page
        
        # 方法2: 检查是否存在"下一页"按钮
        next_selectors = [
            '.page-navigator .next',
            '.pagination .next',
            '.next-page',
            'a:contains("下一页")'
        ]
        
        for selector in next_selectors:
            if data(selector):
                print("检测到下一页按钮，允许继续翻页")
                return 99999
        
        # 方法3: 如果当前页视频数量很少，可能没有下一页
        if len(data('#archive article, #index article, .post-card')) < 5:
            print("当前页内容较少，可能没有下一页")
            return int(current_page)
        
        print("使用默认页数: 99999")
        return 99999

    def detailContent(self, ids):
        try:
            url = f"{self.host}{ids[0]}" if not ids[0].startswith('http') else ids[0]
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [{'vod_play_from': '今日看料', 'vod_play_url': f'页面加载失败${url}'}]}
                
            data = self.getpq(response.text)
            vod = {'vod_play_from': '今日看料'}
            
            # 获取标题
            title_selectors = ['.post-title', 'h1.entry-title', 'h1', '.post-card-title']
            for selector in title_selectors:
                title_elem = data(selector)
                if title_elem:
                    vod['vod_name'] = title_elem.text().strip()
                    break
            
            if 'vod_name' not in vod:
                vod['vod_name'] = '今日看料视频'
            
            # 获取内容/描述
            try:
                clist = []
                if data('.tags .keywords a'):
                    for k in data('.tags .keywords a').items():
                        title = k.text()
                        href = k.attr('href')
                        if title and href:
                            # 使href相对路径
                            if href.startswith(self.host):
                                href = href.replace(self.host, '')
                            clist.append('[a=cr:' + json.dumps({'id': href, 'name': title}) + '/]' + title + '[/a]')
                vod['vod_content'] = ' '.join(clist) if clist else data('.post-content').text() or vod['vod_name']
            except:
                vod['vod_content'] = vod['vod_name']
            
            # 获取视频URLs
            try:
                plist = []
                used_names = set()
                
                # 查找DPlayer视频
                if data('.dplayer'):
                    for c, k in enumerate(data('.dplayer').items(), start=1):
                        config_attr = k.attr('data-config')
                        if config_attr:
                            try:
                                config = json.loads(config_attr)
                                video_url = config.get('video', {}).get('url', '')
                                if video_url:
                                    name = f"视频{c}"
                                    count = 2
                                    while name in used_names:
                                        name = f"视频{c}_{count}"
                                        count += 1
                                    used_names.add(name)
                                    self.log(f"解析到视频: {name} -> {video_url}")
                                    print(f"解析到视频: {name} -> {video_url}")
                                    plist.append(f"{name}${video_url}")
                            except:
                                continue
                
                # 查找视频标签
                if not plist:
                    video_selectors = ['video source', 'video', 'iframe[src*="video"]', 'a[href*=".m3u8"]', 'a[href*=".mp4"]']
                    for selector in video_selectors:
                        for c, elem in enumerate(data(selector).items(), start=1):
                        