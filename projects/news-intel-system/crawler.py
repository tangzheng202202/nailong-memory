#!/usr/bin/env python3
"""
新闻热点爬虫 - MVP版本
抓取各平台热搜，输出JSON供后续处理
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_weibo_hot():
    """抓取微博热搜"""
    url = "https://s.weibo.com/top/summary"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        items = []
        tbody = soup.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr')[1:]:  # 跳过表头
                tds = tr.find_all('td')
                if len(tds) >= 3:
                    rank = tds[0].text.strip()
                    title_elem = tds[1].find('a')
                    if title_elem:
                        title = title_elem.text.strip()
                        link = "https://s.weibo.com" + title_elem.get('href', '')
                        hot = tds[2].text.strip() if len(tds) > 2 else ""
                        
                        items.append({
                            "platform": "微博",
                            "rank": int(rank) if rank.isdigit() else 0,
                            "title": title,
                            "link": link,
                            "hot_value": hot,
                            "category": classify_content(title),
                            "crawled_at": datetime.now().isoformat()
                        })
        return items
    except Exception as e:
        print(f"微博抓取失败: {e}")
        return []

def fetch_zhihu_hot():
    """抓取知乎热榜"""
    url = "https://www.zhihu.com/hot"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        items = []
        # 知乎热榜在特定的div结构中
        hot_list = soup.find_all('div', class_='HotList-item')
        
        for idx, item in enumerate(hot_list[:20], 1):
            title_elem = item.find('h2', class_='HotList-itemTitle')
            if title_elem:
                title = title_elem.text.strip()
                link_elem = item.find('a')
                link = link_elem.get('href', '') if link_elem else ''
                
                items.append({
                    "platform": "知乎",
                    "rank": idx,
                    "title": title,
                    "link": link if link.startswith('http') else f"https://www.zhihu.com{link}",
                    "hot_value": "",
                    "category": classify_content(title),
                    "crawled_at": datetime.now().isoformat()
                })
        return items
    except Exception as e:
        print(f"知乎抓取失败: {e}")
        return []

def fetch_baidu_hot():
    """抓取百度热搜"""
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        items = []
        # 百度热搜在content_1yDPv类中
        hot_items = soup.find_all('div', class_=re.compile('content_'))
        
        for idx, item in enumerate(hot_items[:20], 1):
            title_elem = item.find('div', class_=re.compile('title_'))
            if title_elem:
                title = title_elem.text.strip()
                link_elem = item.find('a')
                link = link_elem.get('href', '') if link_elem else ''
                hot_elem = item.find('div', class_=re.compile('hot_'))
                hot = hot_elem.text.strip() if hot_elem else ""
                
                items.append({
                    "platform": "百度",
                    "rank": idx,
                    "title": title,
                    "link": link,
                    "hot_value": hot,
                    "category": classify_content(title),
                    "crawled_at": datetime.now().isoformat()
                })
        return items
    except Exception as e:
        print(f"百度抓取失败: {e}")
        return []

def classify_content(title):
    """简单内容分类"""
    keywords = {
        "娱乐": ["明星", "电影", "电视剧", "综艺", "演唱", "爆料", "恋情", "离婚", "结婚", "出轨"],
        "科技": ["手机", "AI", "人工智能", "芯片", "华为", "苹果", "特斯拉", "小米", "发布"],
        "社会": ["事故", "火灾", "地震", "疫情", "医院", "学校", "政府", "政策"],
        "财经": ["股市", "A股", "基金", "理财", "房价", "经济", "公司", "财报"],
        "体育": ["足球", "篮球", "NBA", "世界杯", "奥运", "冠军", "比赛", "运动员"]
    }
    
    for category, words in keywords.items():
        if any(word in title for word in words):
            return category
    return "其他"

def main():
    """主函数"""
    print(f"开始抓取热点数据... {datetime.now()}")
    
    all_data = []
    
    # 抓取各平台
    print("抓取微博热搜...")
    all_data.extend(fetch_weibo_hot())
    
    print("抓取知乎热榜...")
    all_data.extend(fetch_zhihu_hot())
    
    print("抓取百度热搜...")
    all_data.extend(fetch_baidu_hot())
    
    # 保存结果
    output = {
        "crawled_at": datetime.now().isoformat(),
        "total": len(all_data),
        "data": all_data
    }
    
    output_file = f"/Users/mac/.openclaw/workspace/projects/news-intel-system/data/hot_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"抓取完成: {len(all_data)} 条数据")
    print(f"保存至: {output_file}")
    
    # 输出TOP10摘要
    print("\n=== TOP 10 热点 ===")
    for item in all_data[:10]:
        print(f"[{item['platform']}] {item['rank']}. {item['title']} ({item['category']})")

if __name__ == "__main__":
    main()
