#!/usr/bin/env python3
"""
生成公众号配图
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 创建输出目录
output_dir = os.path.expanduser("~/.openclaw/workspace/images")
os.makedirs(output_dir, exist_ok=True)

# 颜色配置
COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_card': '#16213e',
    'accent': '#e94560',
    'text_white': '#ffffff',
    'text_gray': '#a0a0a0',
    'success': '#4ecca3',
    'warning': '#ffc107',
    'danger': '#e94560'
}

def get_font(size):
    """获取字体"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_architecture_diagram():
    """创建系统架构图"""
    width, height = 900, 600
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32)
    font_text = get_font(20)
    font_small = get_font(14)
    
    # 标题
    draw.text((width//2, 30), "OpenClaw 系统架构", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 绘制层级结构
    layers = [
        ("用户层", ["飞书", "Web UI", "API"], 100, COLORS['accent']),
        ("OpenClaw Gateway", ["消息路由", "安全审计", "会话管理"], 220, COLORS['bg_card']),
        ("Agent 层", ["Main Agent", "Coder Agent", "Researcher", "Monitor"], 340, COLORS['bg_card']),
        ("工具层", ["Browser", "Web Fetch", "File System", "Shell"], 460, COLORS['bg_card']),
    ]
    
    y_start = 80
    for i, (title, items, box_height, color) in enumerate(layers):
        y = y_start + i * 120
        # 绘制方框
        draw.rounded_rectangle([50, y, width-50, y+box_height], radius=10, fill=color, outline=COLORS['accent'], width=2)
        # 标题
        draw.text((70, y+15), title, fill=COLORS['text_white'], font=font_text)
        # 子项
        x_offset = 70
        for item in items:
            draw.rounded_rectangle([x_offset, y+50, x_offset+120, y+80], radius=5, fill=COLORS['bg_dark'])
            draw.text((x_offset+60, y+65), item, fill=COLORS['text_gray'], font=font_small, anchor="mm")
            x_offset += 140
    
    # 箭头
    for i in range(3):
        y = y_start + i * 120 + 100
        draw.polygon([(width//2-10, y), (width//2+10, y), (width//2, y+20)], fill=COLORS['accent'])
    
    img.save(f"{output_dir}/architecture.png")
    print(f"✅ 架构图已生成: {output_dir}/architecture.png")
    return img

def create_memory_fix_comparison():
    """Memory 修复前后对比图"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    font_status = get_font(24)
    
    # 标题
    draw.text((width//2, 30), "Memory 插件修复对比", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 修复前
    draw.rounded_rectangle([50, 80, 430, 350], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 110), "修复前", fill=COLORS['danger'], font=font_title, anchor="mt")
    draw.text((240, 160), "❌ Memory unavailable", fill=COLORS['danger'], font=font_status, anchor="mt")
    draw.text((240, 210), "每次对话都像是第一次", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 250), "记不住用户偏好", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((240, 290), "项目进展丢失", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 修复后
    draw.rounded_rectangle([470, 80, 850, 350], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 110), "修复后", fill=COLORS['success'], font=font_title, anchor="mt")
    draw.text((660, 160), "✅ Memory ready", fill=COLORS['success'], font=font_status, anchor="mt")
    draw.text((660, 210), "记住你是谁", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((660, 250), "记得聊过什么", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    draw.text((660, 290), "项目进展不丢失", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 中间箭头
    draw.polygon([(440, 200), (460, 200), (450, 220)], fill=COLORS['accent'])
    draw.polygon([(440, 220), (460, 220), (450, 200)], fill=COLORS['accent'])
    
    img.save(f"{output_dir}/memory_comparison.png")
    print(f"✅ Memory对比图已生成: {output_dir}/memory_comparison.png")
    return img

def create_security_audit_comparison():
    """安全审计对比图"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(18)
    font_big = get_font(48)
    
    # 标题
    draw.text((width//2, 30), "安全审计结果对比", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 修复前
    draw.rounded_rectangle([50, 80, 430, 350], radius=15, fill=COLORS['bg_card'])
    draw.text((240, 110), "修复前", fill=COLORS['danger'], font=font_title, anchor="mt")
    draw.text((240, 180), "3", fill=COLORS['danger'], font=font_big, anchor="mt")
    draw.text((240, 240), "CRITICAL", fill=COLORS['danger'], font=font_text, anchor="mt")
    draw.text((240, 290), "groupPolicy: open", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 修复后
    draw.rounded_rectangle([470, 80, 850, 350], radius=15, fill=COLORS['bg_card'])
    draw.text((660, 110), "修复后", fill=COLORS['success'], font=font_title, anchor="mt")
    draw.text((660, 180), "0", fill=COLORS['success'], font=font_big, anchor="mt")
    draw.text((660, 240), "CRITICAL", fill=COLORS['success'], font=font_text, anchor="mt")
    draw.text((660, 290), "groupPolicy: allowlist", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    # 中间箭头
    draw.polygon([(440, 200), (460, 200), (450, 220)], fill=COLORS['accent'])
    draw.polygon([(440, 220), (460, 220), (450, 200)], fill=COLORS['accent'])
    
    img.save(f"{output_dir}/security_audit.png")
    print(f"✅ 安全审计对比图已生成: {output_dir}/security_audit.png")
    return img

def create_config_table():
    """配置清单表格图"""
    width, height = 900, 500
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_header = get_font(18)
    font_text = get_font(16)
    
    # 标题
    draw.text((width//2, 30), "系统配置清单", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 表头
    headers = ["组件", "用途", "状态"]
    col_widths = [200, 400, 200]
    x_positions = [50, 250, 650]
    
    # 表头背景
    draw.rectangle([50, 70, 850, 110], fill=COLORS['accent'])
    for i, header in enumerate(headers):
        draw.text((x_positions[i] + col_widths[i]//2, 90), header, fill=COLORS['text_white'], font=font_header, anchor="mm")
    
    # 数据行
    data = [
        ("Kimi K2.5", "主力模型（云端）", "✅ 运行中"),
        ("DeepSeek 7B", "代码/推理（本地）", "✅ 运行中"),
        ("Gemma 3 4B", "快速问答（本地）", "✅ 运行中"),
        ("Memory 插件", "跨会话记忆", "✅ 已修复"),
        ("飞书通道", "消息接入", "✅ 安全加固"),
        ("GitHub 备份", "记忆持久化", "✅ 自动同步"),
        ("定时监控", "V2EX/B站/HN/GitHub", "✅ 每4小时"),
        ("RSS 监控", "X/YouTube", "✅ 每小时"),
    ]
    
    row_height = 45
    for i, (comp, usage, status) in enumerate(data):
        y = 110 + i * row_height
        # 交替行背景
        if i % 2 == 0:
            draw.rectangle([50, y, 850, y+row_height], fill=COLORS['bg_card'])
        
        draw.text((x_positions[0] + 10, y + row_height//2), comp, fill=COLORS['text_white'], font=font_text, anchor="lm")
        draw.text((x_positions[1] + 10, y + row_height//2), usage, fill=COLORS['text_gray'], font=font_text, anchor="lm")
        draw.text((x_positions[2] + col_widths[2]//2, y + row_height//2), status, fill=COLORS['success'], font=font_text, anchor="mm")
    
    # 边框
    draw.rectangle([50, 70, 850, 110 + len(data)*row_height], outline=COLORS['accent'], width=2)
    
    img.save(f"{output_dir}/config_table.png")
    print(f"✅ 配置清单表格图已生成: {output_dir}/config_table.png")
    return img

def create_workflow_diagram():
    """工作流程图"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(28)
    font_text = get_font(16)
    font_step = get_font(20)
    
    # 标题
    draw.text((width//2, 30), "定时任务工作流", fill=COLORS['text_white'], font=font_title, anchor="mt")
    
    # 步骤
    steps = [
        ("监控", "V2EX/B站/\nHN/GitHub", 100),
        ("分析", "AI总结\n热点趋势", 300),
        ("生成", "自动撰写\n报告", 500),
        ("推送", "飞书/微信\n通知", 700),
    ]
    
    for i, (title, desc, x) in enumerate(steps):
        # 步骤圆圈
        draw.ellipse([x-40, 120, x+40, 200], fill=COLORS['accent'], outline=COLORS['text_white'], width=3)
        draw.text((x, 160), str(i+1), fill=COLORS['text_white'], font=font_step, anchor="mm")
        
        # 标题
        draw.text((x, 230), title, fill=COLORS['text_white'], font=font_text, anchor="mt")
        
        # 描述
        lines = desc.split('\n')
        for j, line in enumerate(lines):
            draw.text((x, 260 + j*25), line, fill=COLORS['text_gray'], font=font_text, anchor="mt")
        
        # 箭头（除了最后一个）
        if i < len(steps) - 1:
            next_x = steps[i+1][2]
            draw.polygon([(x+50, 160), (next_x-50, 150), (next_x-50, 170)], fill=COLORS['accent'])
    
    # 时间标注
    draw.text((width//2, 350), "每 4 小时自动执行", fill=COLORS['text_gray'], font=font_text, anchor="mt")
    
    img.save(f"{output_dir}/workflow.png")
    print(f"✅ 工作流程图已生成: {output_dir}/workflow.png")
    return img

if __name__ == "__main__":
    print("🎨 开始生成公众号配图...")
    create_architecture_diagram()
    create_memory_fix_comparison()
    create_security_audit_comparison()
    create_config_table()
    create_workflow_diagram()
    print(f"\n✨ 所有图片已保存到: {output_dir}/")
    print("\n生成的文件:")
    for f in os.listdir(output_dir):
        if f.endswith('.png'):
            print(f"  - {f}")
