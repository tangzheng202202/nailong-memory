#!/usr/bin/env python3
"""
京东价格抓取模块 - 使用 Playwright 获取商品价格
"""

import re
import time
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def extract_sku_id(url: str) -> Optional[str]:
    """从京东URL中提取SKU ID"""
    # 匹配 item.jd.com/12345678.html 格式
    match = re.search(r'item\.jd\.com/(\d+)\.html', url)
    if match:
        return match.group(1)
    
    # 匹配 item.jd.com/12345678.html 格式（带www）
    match = re.search(r'item\.jd\.\w+/(\d+)\.html', url)
    if match:
        return match.group(1)
    
    return None


def fetch_price_with_playwright(url: str) -> Optional[Dict[str, Any]]:
    """使用 Playwright 获取商品价格"""
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright 未安装，请先运行: pip install playwright && playwright install chromium")
        return None
    
    sku_id = extract_sku_id(url)
    if not sku_id:
        print(f"无法从URL提取SKU ID: {url}")
        return None
    
    try:
        with sync_playwright() as p:
            # 启动浏览器（无头模式）
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # 访问商品页面
            print(f"正在访问: {url}")
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待页面加载
            time.sleep(2)
            
            result = {
                'sku_id': sku_id,
                'name': None,
                'price': None,
                'original_price': None
            }
            
            # 尝试获取商品名称
            try:
                # 京东商品标题选择器
                title_selectors = [
                    '.sku-name',
                    '.p-name',
                    'h1',
                    '[data-hook="product_title"]',
                    '.itemInfo-wrap h1'
                ]
                
                for selector in title_selectors:
                    try:
                        title_elem = page.query_selector(selector)
                        if title_elem:
                            result['name'] = title_elem.inner_text().strip()
                            break
                    except:
                        continue
            except Exception as e:
                print(f"获取商品名称失败: {e}")
            
            # 尝试获取价格
            try:
                # 京东价格选择器
                price_selectors = [
                    '.price-now .p-price .price',
                    '.p-price .price',
                    '.summary-price .price',
                    '[data-hook="price"]',
                    '.dd .p-price .price',
                    '.price-current',
                    '.J-p-price'
                ]
                
                for selector in price_selectors:
                    try:
                        price_elem = page.query_selector(selector)
                        if price_elem:
                            price_text = price_elem.inner_text().strip()
                            # 提取数字
                            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                            if price_match:
                                result['price'] = float(price_match.group())
                                break
                    except:
                        continue
                
                # 如果上面的选择器都没找到，尝试通过JavaScript获取
                if result['price'] is None:
                    try:
                        price = page.evaluate('''() => {
                            // 尝试从页面变量中获取价格
                            if (typeof pageConfig !== 'undefined' && pageConfig.product) {
                                return pageConfig.product.price || pageConfig.product.skuid;
                            }
                            // 尝试从DOM中查找
                            const priceEl = document.querySelector('.price-now .p-price .price') ||
                                          document.querySelector('.p-price .price') ||
                                          document.querySelector('[class*="price"]');
                            return priceEl ? priceEl.textContent : null;
                        }''')
                        if price:
                            price_match = re.search(r'[\d,]+\.?\d*', str(price).replace(',', ''))
                            if price_match:
                                result['price'] = float(price_match.group())
                    except Exception as e:
                        print(f"JavaScript获取价格失败: {e}")
                
            except Exception as e:
                print(f"获取价格失败: {e}")
            
            browser.close()
            
            if result['price'] is None:
                print("无法获取价格，可能需要登录或页面结构已改变")
                return None
            
            return result
            
    except Exception as e:
        print(f"Playwright 抓取失败: {e}")
        return None


def fetch_price_api(sku_id: str) -> Optional[float]:
    """
    通过京东API获取价格（备用方案）
    注意：此API可能需要特定的请求头或Cookie
    """
    import requests
    
    try:
        url = f"https://p.3.cn/prices/mgets?skuIds=J_{sku_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://item.jd.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data and len(data) > 0:
            price_str = data[0].get('p', '0')
            return float(price_str) if price_str else None
            
    except Exception as e:
        print(f"API获取价格失败: {e}")
    
    return None


def fetch_jd_price(url: str) -> Optional[Dict[str, Any]]:
    """
    获取京东商品价格的主函数
    先尝试Playwright，失败则尝试API
    """
    # 首先尝试 Playwright
    result = fetch_price_with_playwright(url)
    
    if result and result['price']:
        return result
    
    # Playwright 失败，尝试 API
    sku_id = extract_sku_id(url)
    if sku_id:
        price = fetch_price_api(sku_id)
        if price:
            return {
                'sku_id': sku_id,
                'name': None,
                'price': price,
                'original_price': None
            }
    
    return None


if __name__ == '__main__':
    # 测试
    test_url = "https://item.jd.com/100012043978.html"  # iPhone 示例
    print(f"测试抓取: {test_url}")
    
    result = fetch_jd_price(test_url)
    if result:
        print(f"SKU ID: {result['sku_id']}")
        print(f"商品名称: {result['name']}")
        print(f"当前价格: ¥{result['price']}")
    else:
        print("抓取失败")
