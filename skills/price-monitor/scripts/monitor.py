#!/usr/bin/env python3
"""
主监控脚本 - 定时检查商品价格并发送通知
"""

import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, list_products, get_product_by_id, update_product_price, get_price_history
from jd_scraper import fetch_jd_price
from notifier import (
    send_price_drop_notification, 
    send_lowest_price_notification,
    send_monitor_summary
)


def check_single_product(product: dict) -> dict:
    """
    检查单个商品的价格
    
    Returns:
        检查结果字典
    """
    result = {
        'product_id': product['id'],
        'name': product['name'],
        'url': product['url'],
        'success': False,
        'price_changed': False,
        'is_lowest': False,
        'old_price': product.get('current_price'),
        'new_price': None,
        'error': None
    }
    
    print(f"\n检查商品: {product['name']}")
    print(f"链接: {product['url']}")
    
    try:
        # 获取当前价格
        price_info = fetch_jd_price(product['url'])
        
        if not price_info or price_info.get('price') is None:
            result['error'] = "无法获取价格"
            print(f"  ❌ 无法获取价格")
            return result
        
        new_price = price_info['price']
        result['new_price'] = new_price
        result['success'] = True
        
        print(f"  ✅ 当前价格: ¥{new_price:.2f}")
        
        old_price = product.get('current_price')
        
        # 更新价格到数据库
        update_product_price(product['id'], new_price)
        
        # 检查是否降价
        if old_price and new_price < old_price:
            result['price_changed'] = True
            drop_amount = old_price - new_price
            print(f"  🎉 降价了！降了 ¥{drop_amount:.2f}")
            
            # 发送降价通知
            send_price_drop_notification(
                product_name=product['name'],
                old_price=old_price,
                new_price=new_price,
                url=product['url']
            )
        
        # 检查是否历史最低价
        history = get_price_history(product['id'])
        if history:
            prices = [h['price'] for h in history]
            if prices and new_price <= min(prices):
                result['is_lowest'] = True
                print(f"  🔥 历史最低价！")
                
                # 发送历史最低价通知
                send_lowest_price_notification(
                    product_name=product['name'],
                    current_price=new_price,
                    lowest_price=new_price,
                    url=product['url']
                )
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        print(f"  ❌ 检查失败: {e}")
        return result


def run_monitor():
    """运行价格监控"""
    print("=" * 60)
    print("🚀 开始价格监控")
    print(f"⏰ 时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 初始化数据库
    init_db()
    
    # 获取所有监控商品
    products = list_products()
    
    if not products:
        print("\n⚠️ 监控列表为空，请先添加商品")
        print("使用: python add_product.py --url <京东链接> --name <商品名称>")
        return
    
    print(f"\n📦 共 {len(products)} 个商品需要检查\n")
    
    # 统计
    stats = {
        'checked': 0,
        'updated': 0,
        'price_drops': 0,
        'errors': 0
    }
    
    # 检查每个商品
    for product in products:
        result = check_single_product(product)
        
        stats['checked'] += 1
        if result['success']:
            stats['updated'] += 1
            if result['price_changed']:
                stats['price_drops'] += 1
        else:
            stats['errors'] += 1
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("📊 监控完成摘要")
    print("=" * 60)
    print(f"✅ 检查商品: {stats['checked']} 个")
    print(f"📝 更新价格: {stats['updated']} 个")
    print(f"🎉 发现降价: {stats['price_drops']} 个")
    print(f"❌ 检查失败: {stats['errors']} 个")
    
    # 发送摘要通知
    send_monitor_summary(
        products_checked=stats['checked'],
        products_updated=stats['updated'],
        price_drops=stats['price_drops']
    )
    
    print("\n✨ 监控完成！")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='价格监控 - 检查商品价格变化',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--product', '-p', type=int, metavar='ID',
                        help='只检查指定ID的商品')
    
    args = parser.parse_args()
    
    if args.product:
        # 只检查单个商品
        init_db()
        product = get_product_by_id(args.product)
        if product:
            check_single_product(product)
        else:
            print(f"错误: 找不到 ID 为 {args.product} 的商品")
    else:
        # 运行完整监控
        run_monitor()


if __name__ == '__main__':
    main()
