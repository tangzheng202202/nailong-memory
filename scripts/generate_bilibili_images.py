#!/usr/bin/env python3
"""
生成B站调研报告公众号配图
"""
from PIL import Image, ImageDraw, ImageFont
import os

output_dir = os.path.expanduser("~/.openclaw/workspace/images")
os.makedirs(output_dir, exist_ok=True)

COLORS = {
    'bg_dark': '#0f0f23',
    'bg_card': '#1a1a3e',
    'accent': '#ff6b6b',
    'accent2': '#4ecdc4',
    'text_white': '#ffffff',
    'text_gray': '#b0b0b0',
    'yellow': '#ffd93d',
    'purple': '#a855f7'
}

def get_font(size):
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_bilibili_stats():
    """B站数据统计图"""
    width, height = 900, 500
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32)
    font_big = get_font(64)
    font_text = get_font(20)
    font_small = get_font(16)
    
    # 标题
    draw.text((width//2, 40), "B站 OpenClaw 视频调研数据", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 数据卡片
    stats = [
        ("500+", "相关视频", 100, 150, COLORS['accent']),
        ("198.5万", "最高播放", 350, 150, COLORS['yellow']),
        ("50", "深度分析", 600, 150, COLORS['accent2']),
        ("4小时", "调研耗时", 225, 320, COLORS['purple']),
        ("35%", "安装教程占比", 475, 320, COLORS['accent']),
    ]
    
    for value, label, x, y, color in stats:
        # 卡片背景
        draw.rounded_rectangle([x, y, x+200, y+140], radius=15, fill=COLORS['bg_card'], outline=color, width=2)
        # 数值
        draw.text((x+100, y+50), value, fill=color, font=font_big, anchor="mm")
        # 标签
        draw.text((x+100, y+105), label, fill=COLORS['text_gray'], font=font_text, anchor="mm")
    
    img.save(f"{output_dir}/bilibili_stats.png")
    print(f"✅ B站数据统计图已生成")
    return img

def create_user_segments():
    """用户分层图"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    font_label = get_font(16)
    
    # 标题
    draw.text((width//2, 30), "OpenClaw 用户分层", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 三个群体
    segments = [
        ("真香党", "已上手", "帮我写了10篇报告", "20%", COLORS['accent2'], 100),
        ("劝退党", "安装失败", "Docker报错放弃了", "60%", COLORS['accent'], 350),
        ("观望党", "还在看", "不知道自己需不需要", "20%", COLORS['yellow'], 600),
    ]
    
    for name, status, desc, percent, color, x in segments:
        # 人形图标（简化版用圆圈）
        draw.ellipse([x+60, 100, x+140, 180], fill=color, outline=COLORS['text_white'], width=2)
        draw.text((x+100, 140), "👤", fill=COLORS['text_white'], font=get_font(40), anchor="mm")
        
        # 名称
        draw.text((x+100, 200), name, fill=color, font=font_text, anchor="mt")
        # 状态
        draw.text((x+100, 230), status, fill=COLORS['text_gray'], font=font_label, anchor="mt")
        # 描述
        draw.text((x+100, 260), desc, fill=COLORS['text_gray'], font=font_label, anchor="mt")
        # 占比
        draw.text((x+100, 320), percent, fill=color, font=get_font(36), anchor="mt")
    
    img.save(f"{output_dir}/user_segments.png")
    print(f"✅ 用户分层图已生成")
    return img

def create_install_vs_usage():
    """安装vs使用对比"""
    width, height = 900, 350
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    
    # 标题
    draw.text((width//2, 30), "安装教程 vs 实战内容", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 左侧：安装教程
    draw.rounded_rectangle([50, 80, 430, 300], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 110), "安装教程", fill=COLORS['accent'], font=font_title, anchor="mt")
    draw.text((240, 160), "35% 的视频", fill=COLORS['text_white'], font=get_font(32), anchor="mt")
    draw.text((240, 210), "Docker、配置、报错", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 250), "评论区最常见：\"怎么装？\"", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 右侧：实战内容
    draw.rounded_rectangle([470, 80, 850, 300], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 110), "实战内容", fill=COLORS['accent2'], font=font_title, anchor="mt")
    draw.text((660, 160), "仅 12% 提到Memory", fill=COLORS['text_white'], font=get_font(24), anchor="mt")
    draw.text((660, 210), "但完播率明显更高", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((660, 250), "真正从玩具到工具", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    img.save(f"{output_dir}/install_vs_usage.png")
    print(f"✅ 安装vs使用对比图已生成")
    return img

def create_money_truth():
    """赚钱真相图"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    font_big = get_font(48)
    
    # 标题
    draw.text((width//2, 30), "赚钱的真相", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 左侧：你以为的
    draw.rounded_rectangle([50, 80, 430, 350], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 120), "❌ 你以为的", fill=COLORS['accent'], font=font_title, anchor="mt")
    draw.text((240, 180), "用OpenClaw", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 220), "自动炒股", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 260), "月入10万", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 右侧：实际的
    draw.rounded_rectangle([470, 80, 850, 350], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 120), "✅ 实际的", fill=COLORS['accent2'], font=font_title, anchor="mt")
    draw.text((660, 180), "帮人装OpenClaw", fill=COLORS['text_white'], font=font_text, anchor="mt")
    draw.text((660, 230), "500-1000/单", fill=COLORS['yellow'], font=font_big, anchor="mt")
    draw.text((660, 290), "已赚2万+", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 箭头
    draw.polygon([(440, 200), (460, 200), (450, 220)], fill=COLORS['accent'])
    
    img.save(f"{output_dir}/money_truth.png")
    print(f"✅ 赚钱真相图已生成")
    return img

def create_memory_comparison():
    """Memory对比图"""
    width, height = 900, 350
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    
    # 标题
    draw.text((width//2, 30), "Memory 插件：分水岭", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 无Memory
    draw.rounded_rectangle([50, 80, 430, 300], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 110), "🐟 无 Memory", fill=COLORS['accent'], font=font_title, anchor="mt")
    draw.text((240, 160), "每次对话都像是", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 190), "第一次见面", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 240), "玩具", fill=COLORS['accent'], font=get_font(36), anchor="mt")
    
    # 有Memory
    draw.rounded_rectangle([470, 80, 850, 300], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 110), "🧠 有 Memory", fill=COLORS['accent2'], font=font_title, anchor="mt")
    draw.text((660, 160), "记住你是谁、", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((660, 190), "聊过什么、项目进展", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((660, 240), "工具", fill=COLORS['accent2'], font=get_font(36), anchor="mt")
    
    img.save(f"{output_dir}/memory_divide.png")
    print(f"✅ Memory分水岭图已生成")
    return img

if __name__ == "__main__":
    print("🎨 开始生成B站调研报告配图...")
    create_bilibili_stats()
    create_user_segments()
    create_install_vs_usage()
    create_money_truth()
    create_memory_comparison()
    print(f"\n✨ 所有图片已保存到: {output_dir}/")
