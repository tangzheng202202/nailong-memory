#!/usr/bin/env python3
"""
飞书通知模块 - 发送降价通知
"""

import os
import json
import requests
from typing import Optional

# 飞书 Webhook URL（需要在环境变量或配置中设置）
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK', '')


def send_feishu_notification(title: str, content: str, webhook_url: Optional[str] = None) -> bool:
    """
    发送飞书通知
    
    Args:
        title: 通知标题
        content: 通知内容（支持Markdown）
        webhook_url: 飞书机器人Webhook URL，如果不传则使用环境变量
    
    Returns:
        是否发送成功
    """
    webhook = webhook_url or FEISHU_WEBHOOK
    
    if not webhook:
        print("警告: 未配置飞书 Webhook URL，跳过通知发送")
        print(f"通知内容: {title}\n{content}")
        return False
    
    try:
        # 构建消息体
        message = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": content
                                }
                            ]
                        ]
                    }
                }
            }
        }
        
        response = requests.post(
            webhook,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(message),
            timeout=10
        )
        
        result = response.json()
        
        if result.get('code') == 0:
            print(f"飞书通知发送成功: {title}")
            return True
        else:
            print(f"飞书通知发送失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"发送飞书通知时出错: {e}")
        return False


def send_price_drop_notification(product_name: str, old_price: float, new_price: float, 
                                  url: str, webhook_url: Optional[str] = None) -> bool:
    """
    发送降价通知
    
    Args:
        product_name: 商品名称
        old_price: 原价
        new_price: 新价格
        url: 商品链接
        webhook_url: 飞书机器人Webhook URL
    
    Returns:
        是否发送成功
    """
    drop_amount = old_price - new_price
    drop_percent = (drop_amount / old_price) * 100 if old_price > 0 else 0
    
    title = f"🎉 降价提醒: {product_name}"
    
    content = f"""商品降价啦！

📦 商品: {product_name}
💰 原价: ¥{old_price:.2f}
🔥 现价: ¥{new_price:.2f}
📉 降幅: ¥{drop_amount:.2f} ({drop_percent:.1f}%)

🔗 购买链接: {url}

快去抢购吧！🏃‍♂️"""
    
    return send_feishu_notification(title, content, webhook_url)


def send_lowest_price_notification(product_name: str, current_price: float, 
                                    lowest_price: float, url: str,
                                    webhook_url: Optional[str] = None) -> bool:
    """
    发送历史最低价通知
    
    Args:
        product_name: 商品名称
        current_price: 当前价格
        lowest_price: 历史最低价
        url: 商品链接
        webhook_url: 飞书机器人Webhook URL
    
    Returns:
        是否发送成功
    """
    title = f"🔥 历史最低价: {product_name}"
    
    content = f"""商品达到历史最低价！

📦 商品: {product_name}
💰 当前价格: ¥{current_price:.2f}
🏆 历史最低: ¥{lowest_price:.2f}

🔗 购买链接: {url}

这是入手的好时机！💪"""
    
    return send_feishu_notification(title, content, webhook_url)


def send_monitor_summary(products_checked: int, products_updated: int, 
                         price_drops: int, webhook_url: Optional[str] = None) -> bool:
    """
    发送监控摘要通知
    
    Args:
        products_checked: 检查的商品数量
        products_updated: 更新的商品数量
        price_drops: 降价的商品数量
        webhook_url: 飞书机器人Webhook URL
    
    Returns:
        是否发送成功
    """
    title = "📊 价格监控日报"
    
    content = f"""本次监控完成！

✅ 检查商品: {products_checked} 个
📝 更新价格: {products_updated} 个
🎉 发现降价: {price_drops} 个

监控时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    return send_feishu_notification(title, content, webhook_url)


if __name__ == '__main__':
    # 测试通知
    print("测试飞书通知...")
    
    # 如果没有配置webhook，只打印消息
    if not FEISHU_WEBHOOK:
        print("未配置 FEISHU_WEBHOOK 环境变量")
    
    send_price_drop_notification(
        "iPhone 15 Pro",
        8999.00,
        7999.00,
        "https://item.jd.com/100012043978.html"
    )
