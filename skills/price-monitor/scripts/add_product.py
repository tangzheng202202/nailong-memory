#!/usr/bin/env python3
"""
添加/删除/列出监控商品
"""

import os
import sys
import argparse
from urllib.parse import urlparse

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, add_product, delete_product, list_products, get_product_by_url
from jd_scraper import extract_sku_id, fetch_jd_price


def validate_jd_url(url: str) -> bool:
    """验证是否为有效的京东商品链接"""
    try:
        parsed = urlparse(url)
        return 'jd.com' in parsed.netloc or 'jd.hk' in parsed.netloc
    except:
        return False


def cmd_add(url: str, name: str = None):
    """添加商品到监控列表"""
    if not validate_jd_url(url):
        print(f"错误: 无效的京东链接: {url}")
        print("链接必须包含 jd.com 或 jd.hk")
        return False
    
    # 检查是否已存在
    existing = get_product_by_url(url)
    if existing:
        print(f"商品已存在于监控列表中 (ID: {existing['id']})")
        print(f"名称: {existing['name']}")
        return False
    
    # 尝试获取商品信息
    print(f"正在获取商品信息: {url}")
    product_info = fetch_jd_price(url)
    
    if product_info and product_info.get('name'):
        product_name = name or product_info['name']
    else:
        product_name = name or "未知商品"
        if not name:
            print("警告: 无法获取商品名称，将使用默认名称")
            product_name = input("请输入商品名称（或按回车使用'未知商品'）: ").strip() or "未知商品"
    
    sku_id = extract_sku_id(url)
    
    # 添加到数据库
    product_id = add_product(product_name, url, sku_id)
    
    if product_id > 0:
        print(f"✅ 商品添加成功！")
        print(f"   ID: {product_id}")
        print(f"   名称: {product_name}")
        print(f"   链接: {url}")
        if product_info and product_info.get('price'):
            print(f"   当前价格: ¥{product_info['price']:.2f}")
        return True
    else:
        print("❌ 商品添加失败")
        return False


def cmd_delete(product_id: int):
    """从监控列表删除商品"""
    from db import get_product_by_id
    
    product = get_product_by_id(product_id)
    if not product:
        print(f"错误: 找不到 ID 为 {product_id} 的商品")
        return False
    
    confirm = input(f"确认删除商品 '{product['name']}'? (y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消删除")
        return False
    
    if delete_product(product_id):
        print(f"✅ 商品已删除: {product['name']}")
        return True
    else:
        print("❌ 删除失败")
        return False


def cmd_list():
    """列出所有监控商品"""
    products = list_products()
    
    if not products:
        print("监控列表为空")
        return
    
    print(f"\n📦 共监控 {len(products)} 个商品:\n")
    print(f"{'ID':<6} {'名称':<40} {'当前价格':<12} {'最低价':<12} {'更新时间'}")
    print("-" * 100)
    
    for p in products:
        name = p['name'][:37] + '...' if len(p['name']) > 40 else p['name']
        current = f"¥{p['current_price']:.2f}" if p['current_price'] else "未获取"
        lowest = f"¥{p['lowest_price']:.2f}" if p['lowest_price'] else "未获取"
        updated = p['updated_at'][:16] if p['updated_at'] else "-"
        
        print(f"{p['id']:<6} {name:<40} {current:<12} {lowest:<12} {updated}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description='价格监控 - 管理监控商品',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 添加商品
  python add_product.py --url "https://item.jd.com/12345678.html" --name "iPhone 15"
  
  # 列出所有商品
  python add_product.py --list
  
  # 删除商品
  python add_product.py --delete 1
        """
    )
    
    parser.add_argument('--url', '-u', help='京东商品链接')
    parser.add_argument('--name', '-n', help='商品名称（可选）')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有监控商品')
    parser.add_argument('--delete', '-d', type=int, metavar='ID', help='删除指定ID的商品')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    
    args = parser.parse_args()
    
    # 初始化数据库
    if args.init:
        init_db()
        return
    
    # 确保数据库已初始化
    init_db()
    
    # 处理命令
    if args.list:
        cmd_list()
    elif args.delete:
        cmd_delete(args.delete)
    elif args.url:
        cmd_add(args.url, args.name)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
