#!/usr/bin/env python3
"""
数据库操作模块 - 管理商品和价格历史数据
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_PATH = os.path.join(DB_DIR, 'price_monitor.db')


def init_db():
    """初始化数据库表结构"""
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            sku_id TEXT,
            current_price REAL,
            lowest_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 价格历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_price_history_product_id 
        ON price_history(product_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at 
        ON price_history(recorded_at)
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")


def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def add_product(name: str, url: str, sku_id: Optional[str] = None) -> int:
    """添加新商品"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO products (name, url, sku_id)
            VALUES (?, ?, ?)
        ''', (name, url, sku_id))
        
        product_id = cursor.lastrowid
        conn.commit()
        return product_id
    except sqlite3.IntegrityError:
        print(f"商品已存在: {url}")
        return -1
    finally:
        conn.close()


def delete_product(product_id: int) -> bool:
    """删除商品及其价格历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 先删除价格历史
        cursor.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
        # 再删除商品
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def list_products() -> List[Dict[str, Any]]:
    """列出所有商品"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, url, sku_id, current_price, lowest_price, created_at, updated_at
        FROM products
        ORDER BY created_at DESC
    ''')
    
    columns = [description[0] for description in cursor.description]
    products = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return products


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取商品"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, url, sku_id, current_price, lowest_price, created_at, updated_at
        FROM products WHERE id = ?
    ''', (product_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        columns = ['id', 'name', 'url', 'sku_id', 'current_price', 'lowest_price', 'created_at', 'updated_at']
        return dict(zip(columns, row))
    return None


def get_product_by_url(url: str) -> Optional[Dict[str, Any]]:
    """根据URL获取商品"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, url, sku_id, current_price, lowest_price, created_at, updated_at
        FROM products WHERE url = ?
    ''', (url,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        columns = ['id', 'name', 'url', 'sku_id', 'current_price', 'lowest_price', 'created_at', 'updated_at']
        return dict(zip(columns, row))
    return None


def update_product_price(product_id: int, price: float):
    """更新商品价格"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取当前最低价
    cursor.execute('SELECT lowest_price FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    lowest_price = row[0] if row and row[0] else price
    
    # 更新最低价
    if lowest_price is None or price < lowest_price:
        lowest_price = price
    
    cursor.execute('''
        UPDATE products 
        SET current_price = ?, lowest_price = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (price, lowest_price, product_id))
    
    # 添加价格历史记录
    cursor.execute('''
        INSERT INTO price_history (product_id, price)
        VALUES (?, ?)
    ''', (product_id, price))
    
    conn.commit()
    conn.close()


def get_price_history(product_id: int, limit: int = 30) -> List[Dict[str, Any]]:
    """获取商品价格历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, product_id, price, recorded_at
        FROM price_history
        WHERE product_id = ?
        ORDER BY recorded_at DESC
        LIMIT ?
    ''', (product_id, limit))
    
    columns = [description[0] for description in cursor.description]
    history = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return history


def get_price_stats(product_id: int) -> Dict[str, Any]:
    """获取价格统计信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price) as avg_price,
            COUNT(*) as record_count
        FROM price_history
        WHERE product_id = ?
    ''', (product_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'min_price': row[0],
            'max_price': row[1],
            'avg_price': round(row[2], 2) if row[2] else None,
            'record_count': row[3]
        }
    return {}


if __name__ == '__main__':
    init_db()
    print("数据库初始化完成！")
