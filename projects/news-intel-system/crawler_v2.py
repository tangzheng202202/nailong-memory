#!/usr/bin/env python3
"""
新闻热点爬虫 - Playwright版本
渲染动态页面抓取热搜
"""

import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import os

async def fetch_weibo(page):
    """抓取微博热搜"""
    items = []
    try:
        await page.goto("https://s.weibo.com/top/summary", timeout=30000)
        await page.wait_for_load_state("networkidle")
        
        # 等待热搜表格加载
        await page.wait_for_selector("tbody tr", timeout=10000)
        
        rows = await page.query_selector_all("tbody tr")
        for row in rows[1:21]:  # TOP20
            tds = await row.query_selector_all("td")
            if len(tds) >= 2:
                rank_elem = await tds[0].text_content()
                link_elem = await tds[1].query_selector("a")
                hot_elem = await tds[2].text_content() if len(tds) > 2 else None
                
                if link_elem:
                    title = await link_elem.text_content()
                    href = await link_elem.get_attribute("href")
                    rank = rank_elem.strip() if rank_elem else "0"
                    hot = hot_elem.strip() if hot_elem else ""
                    
                    items.append({
                        "platform": "微博",
                        "rank": int(rank) if rank.isdigit() else 0,
                        "title": title.strip(),
                        "link": f"https://s.weibo.com{href}" if href else "",
                        "hot_value": hot,
                        "category": classify(title),
                        "crawled_at": datetime.now().isoformat()
                    })
    except Exception as e:
        print(f"微博抓取错误: {e}")
    return items

async def fetch_zhihu(page):
    """抓取知乎热榜"""
    items = []
    try:
        await page.goto("https://www.zhihu.com/hot", timeout=30000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # 等待JS渲染
        
        hot_items = await page.query_selector_all("[data-za-detail-view-id='3942']")
        for idx, item in enumerate(hot_items[:20], 1):
            try:
                title_elem = await item.query_selector("h2")
                if title_elem:
                    title = await title_elem.text_content()
                    link_elem = await item.query_selector("a")
                    href = await link_elem.get_attribute("href") if link_elem else ""
                    
                    items.append({
                        "platform": "知乎",
                        "rank": idx,
                        "title": title.strip(),
                        "link": href if href.startswith("http") else f"https://www.zhihu.com{href}",
                        "hot_value": "",
                        "category": classify(title),
                        "crawled_at": datetime.now().isoformat()
                    })
            except:
                continue
    except Exception as e:
        print(f"知乎抓取错误: {e}")
    return items

def classify(title):
    """简单分类"""
    keywords = {
        "娱乐": ["明星", "电影", "电视剧", "综艺", "演唱", "爆料", "恋情", "离婚", "结婚", "出轨", "八卦"],
        "科技": ["手机", "AI", "人工智能", "芯片", "华为", "苹果", "特斯拉", "小米", "发布", "马斯克", "OpenAI"],
        "社会": ["事故", "火灾", "地震", "疫情", "医院", "学校", "政府", "政策", "警方", "去世"],
        "财经": ["股市", "A股", "基金", "理财", "房价", "经济", "公司", "财报", "涨停", "暴跌"],
        "体育": ["足球", "篮球", "NBA", "世界杯", "奥运", "冠军", "比赛", "运动员", "国乒", "CBA"]
    }
    for cat, words in keywords.items():
        if any(w in title for w in words):
            return cat
    return "其他"

async def main():
    print(f"🚀 开始抓取热点... {datetime.now()}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        all_data = []
        
        print("📱 抓取微博热搜...")
        weibo_data = await fetch_weibo(page)
        all_data.extend(weibo_data)
        print(f"   ✓ 获取 {len(weibo_data)} 条")
        
        print("💡 抓取知乎热榜...")
        zhihu_data = await fetch_zhihu(page)
        all_data.extend(zhihu_data)
        print(f"   ✓ 获取 {len(zhihu_data)} 条")
        
        await browser.close()
    
    # 保存数据
    os.makedirs("data", exist_ok=True)
    filename = f"data/hot_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    
    output = {
        "crawled_at": datetime.now().isoformat(),
        "total": len(all_data),
        "data": all_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成: {len(all_data)} 条数据 → {filename}")
    
    # 输出摘要
    print("\n🔥 TOP 10 热点:")
    print("-" * 60)
    for i, item in enumerate(all_data[:10], 1):
        print(f"{i:2}. [{item['platform']}] {item['title'][:40]}... ({item['category']})")
    
    return all_data

if __name__ == "__main__":
    asyncio.run(main())
