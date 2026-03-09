#!/usr/bin/env python3
"""
生成YouTube调研报告配图
"""
from PIL import Image, ImageDraw, ImageFont
import os

output_dir = os.path.expanduser("~/.openclaw/workspace/images")
os.makedirs(output_dir, exist_ok=True)

COLORS = {
    'bg_dark': '#0a0a1a',
    'bg_card': '#12122a',
    'accent_red': '#ff4757',
    'accent_blue': '#3742fa',
    'text_white': '#ffffff',
    'text_gray': '#a4b0be',
    'yellow': '#ffa502',
    'green': '#2ed573'
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

def create_youtube_vs_bilibili():
    """YouTube vs B站对比图"""
    width, height = 900, 500
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32)
    font_text = get_font(20)
    font_big = get_font(48)
    
    # 标题
    draw.text((width//2, 30), "YouTube vs B站 内容差异", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # YouTube
    draw.rounded_rectangle([50, 80, 430, 450], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 110), "🌎 YouTube", fill=COLORS['accent_blue'], font=font_title, anchor="mt")
    
    youtube_points = [
        "多Agent协作",
        "架构设计",
        "商业应用",
        "安全合规",
        "生产工具"
    ]
    y = 160
    for point in youtube_points:
        draw.text((240, y), f"✓ {point}", fill=COLORS['text_gray'], font=font_text, anchor="mt")
        y += 45
    
    draw.text((240, 400), "管理公司", fill=COLORS['accent_blue'], font=font_big, anchor="mt")
    
    # B站
    draw.rounded_rectangle([470, 80, 850, 450], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 110), "🇨🇳 B站", fill=COLORS['accent_red'], font=font_title, anchor="mt")
    
    bilibili_points = [
        "安装教程",
        "技能配置",
        "实用工具",
        "踩坑记录",
        "效率工具"
    ]
    y = 160
    for point in bilibili_points:
        draw.text((660, y), f"✓ {point}", fill=COLORS['text_gray'], font=font_text, anchor="mt")
        y += 45
    
    draw.text((660, 400), "个人使用", fill=COLORS['accent_red'], font=font_big, anchor="mt")
    
    img.save(f"{output_dir}/youtube_vs_bilibili.png")
    print(f"✅ YouTube vs B站对比图已生成")
    return img

def create_top_videos_comparison():
    """热门视频对比"""
    width, height = 900, 450
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(16)
    
    # 标题
    draw.text((width//2, 30), "热门视频播放量对比", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 数据
    videos = [
        ("Fireship", "The wild rise...", 179, COLORS['accent_blue']),
        ("Lex Fridman", "OpenClaw Podcast", 98, COLORS['accent_blue']),
        ("Brian Casel", "Multi-Agent Team", 48, COLORS['accent_blue']),
        ("林亦LYi", "一个视频搞懂", 35, COLORS['accent_red']),
        ("AI学长小林", "保姆级教学", 18, COLORS['accent_red']),
    ]
    
    max_views = 179
    bar_height = 50
    y_start = 100
    
    for i, (channel, title, views, color) in enumerate(videos):
        y = y_start + i * 65
        bar_width = (views / max_views) * 500
        
        # 频道名
        draw.text((60, y + 25), channel, fill=COLORS['text_white'], font=font_text, anchor="lm")
        
        # 条形图
        draw.rounded_rectangle([200, y, 200 + bar_width, y + bar_height], radius=5, fill=color)
        
        # 播放量
        draw.text((210 + bar_width, y + 25), f"{views}万", fill=COLORS['text_white'], font=font_text, anchor="lm")
        
        # 标题
        draw.text((210, y + bar_height + 5), title, fill=COLORS['text_gray'], font=get_font(12))
    
    img.save(f"{output_dir}/top_videos_comparison.png")
    print(f"✅ 热门视频对比图已生成")
    return img

def create_ai_team_concept():
    """AI团队概念图"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    
    # 标题
    draw.text((width//2, 30), "Brian Casel 的 AI 团队", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 4个Agent
    agents = [
        ("👨‍💻", "开发Agent", "写代码、修bug", 100),
        ("🎨", "设计Agent", "做图、改UI", 300),
        ("✍️", "内容Agent", "写文章、发社媒", 500),
        ("📊", "分析Agent", "看数据、出报告", 700),
    ]
    
    for emoji, name, desc, x in agents:
        # 圆圈
        draw.ellipse([x-50, 100, x+50, 200], fill=COLORS['bg_card'], outline=COLORS['accent_blue'], width=3)
        draw.text((x, 150), emoji, fill=COLORS['text_white'], font=get_font(40), anchor="mm")
        
        # 名称
        draw.text((x, 230), name, fill=COLORS['accent_blue'], font=font_text, anchor="mt")
        
        # 描述
        draw.text((x, 260), desc, fill=COLORS['text_gray'], font=get_font(14), anchor="mt")
    
    # 中心：协调者
    draw.ellipse([400, 300, 500, 400], fill=COLORS['accent_blue'])
    draw.text((450, 350), "🦞", fill=COLORS['text_white'], font=get_font(50), anchor="mm")
    draw.text((450, 420), "OpenClaw", fill=COLORS['text_white'], font=font_text, anchor="mt")
    draw.text((450, 450), "协调者", fill=COLORS['text_gray'], font=get_font(14), anchor="mt")
    
    # 连线
    for _, _, _, x in agents:
        draw.line([(x, 200), (450, 300)], fill=COLORS['accent_blue'], width=2)
    
    img.save(f"{output_dir}/ai_team_concept.png")
    print(f"✅ AI团队概念图已生成")
    return img

def create_gap_analysis():
    """差距分析图"""
    width, height = 900, 350
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    
    # 标题
    draw.text((width//2, 30), "国内外差距 = 机会", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 左侧：国外在做
    draw.rounded_rectangle([50, 80, 430, 300], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 110), "国外在做", fill=COLORS['accent_blue'], font=font_title, anchor="mt")
    
    gaps = [
        "多Agent协作",
        "企业级安全",
        "工作流自动化",
        "AI团队管理"
    ]
    y = 150
    for gap in gaps:
        draw.text((240, y), f"• {gap}", fill=COLORS['text_gray'], font=font_text, anchor="mt")
        y += 35
    
    # 右侧：国内机会
    draw.rounded_rectangle([470, 80, 850, 300], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 110), "国内机会", fill=COLORS['green'], font=font_title, anchor="mt")
    
    opportunities = [
        "本地化集成",
        "垂直场景",
        "成本优化",
        "中文社区"
    ]
    y = 150
    for opp in opportunities:
        draw.text((660, y), f"• {opp}", fill=COLORS['text_gray'], font=font_text, anchor="mt")
        y += 35
    
    img.save(f"{output_dir}/gap_analysis.png")
    print(f"✅ 差距分析图已生成")
    return img

if __name__ == "__main__":
    print("🎨 开始生成YouTube调研报告配图...")
    create_youtube_vs_bilibili()
    create_top_videos_comparison()
    create_ai_team_concept()
    create_gap_analysis()
    print(f"\n✨ 所有图片已保存到: {output_dir}/")
