#!/usr/bin/env python3
"""
公众号文章 HTML 处理工具
功能：
1. 一键替换图片 URL
2. 优化 HTML 格式适应公众号
3. 生成可直接粘贴的 HTML
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime

class WechatArticleProcessor:
    def __init__(self, html_file):
        self.html_file = Path(html_file)
        self.content = self.html_file.read_text(encoding='utf-8')
        self.images = []
        
    def extract_images(self):
        """提取所有图片占位符"""
        # 查找所有 img 标签
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        self.images = re.findall(img_pattern, self.content)
        
        # 去重并保持顺序
        seen = set()
        unique_images = []
        for img in self.images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        self.images = unique_images
        
        return self.images
    
    def replace_images_interactive(self, auto_skip=False):
        """交互式替换图片 URL"""
        print("🖼️  发现 {} 个图片需要替换".format(len(self.images)))
        print("=" * 60)
        
        replacements = {}
        
        for i, old_url in enumerate(self.images, 1):
            print(f"\n[{i}/{len(self.images)}] 当前图片: {old_url[:50]}...")
            
            # 检查是否是占位符
            if 'PLACEHOLDER' in old_url or 'placeholder' in old_url:
                print("  ℹ️  这是占位符，需要替换")
            
            if auto_skip:
                print(f"  ⏭️  自动跳过（使用 --auto 参数）")
                continue
            
            try:
                new_url = input(f"  请输入新URL (直接回车跳过): ").strip()
            except EOFError:
                print(f"  ⏭️  跳过（无输入）")
                continue
            
            if new_url:
                replacements[old_url] = new_url
                print(f"  ✅ 已设置替换")
            else:
                print(f"  ⏭️  跳过")
        
        # 执行替换
        for old_url, new_url in replacements.items():
            self.content = self.content.replace(old_url, new_url)
        
        print(f"\n✅ 完成 {len(replacements)} 个图片替换")
        return len(replacements)
    
    def optimize_for_wechat(self):
        """优化 HTML 适应公众号"""
        
        # 1. 移除不必要的样式，保留核心样式
        # 公众号编辑器会过滤很多 CSS，只保留内联样式
        
        # 2. 简化代码块（公众号代码块支持不好，建议截图）
        # 添加提示注释
        code_blocks = re.findall(r'<div class="code-block">(.*?)</div>', self.content, re.DOTALL)
        for i, code in enumerate(code_blocks, 1):
            placeholder = f'<!-- 代码块 {i}: 建议截图插入 -->'
            self.content = self.content.replace(
                f'<div class="code-block">{code}</div>',
                f'{placeholder}\n<div style="background:#f5f5f5;padding:10px;border-left:3px solid #e94560;font-family:monospace;font-size:14px;overflow-x:auto;">{code}</div>'
            )
        
        # 3. 优化图片样式
        self.content = re.sub(
            r'<div class="image-container">',
            '<div style="text-align:center;margin:20px 0;">',
            self.content
        )
        
        self.content = re.sub(
            r'<div class="image-caption">',
            '<div style="color:#666;font-size:12px;margin-top:10px;text-align:center;">',
            self.content
        )
        
        # 4. 优化引用样式
        self.content = re.sub(
            r'<blockquote>',
            '<blockquote style="border-left:4px solid #e94560;padding:15px 20px;margin:20px 0;background:#f8f9fa;color:#555;font-style:italic;">',
            self.content
        )
        
        # 5. 优化提示框
        self.content = re.sub(
            r'<div class="tip-box">',
            '<div style="background:#fff3cd;border-left:4px solid #ffc107;padding:15px 20px;margin:20px 0;border-radius:0 8px 8px 0;">',
            self.content
        )
        
        self.content = re.sub(
            r'<div class="success-box">',
            '<div style="background:#d4edda;border-left:4px solid #28a745;padding:15px 20px;margin:20px 0;border-radius:0 8px 8px 0;">',
            self.content
        )
        
        # 6. 优化标题样式
        self.content = re.sub(
            r'<h1>',
            '<h1 style="font-size:28px;color:#1a1a2e;text-align:center;margin-bottom:10px;font-weight:700;">',
            self.content
        )
        
        self.content = re.sub(
            r'<h2>',
            '<h2 style="font-size:22px;color:#1a1a2e;margin-top:40px;margin-bottom:20px;padding-bottom:10px;border-bottom:2px solid #e94560;">',
            self.content
        )
        
        # 7. 移除 script 标签（公众号不支持）
        self.content = re.sub(r'<script[^>]*>.*?</script>', '', self.content, flags=re.DOTALL)
        
        # 8. 简化 body 样式
        self.content = re.sub(
            r'<body[^>]*>',
            '<body style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',\'PingFang SC\',sans-serif;line-height:1.8;color:#333;max-width:800px;margin:0 auto;padding:20px;background:#fafafa;">',
            self.content
        )
        
        # 9. 简化 container 样式
        self.content = re.sub(
            r'<div class="container">',
            '<div style="background:#fff;padding:40px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">',
            self.content
        )
        
        print("✅ HTML 已优化适应公众号")
        
    def generate_inline_html(self):
        """生成纯内联样式的 HTML（最兼容）"""
        # 移除所有 class 属性（已转成内联样式）
        self.content = re.sub(r'\s+class="[^"]*"', '', self.content)
        
        # 移除 head 中的 style 标签
        self.content = re.sub(r'<style[^>]*>.*?</style>', '', self.content, flags=re.DOTALL)
        
        # 简化 head
        simple_head = '''<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>文章标题</title>
</head>'''
        
        self.content = re.sub(r'<head>.*?</head>', simple_head, self.content, flags=re.DOTALL)
        
        print("✅ 已生成纯内联样式 HTML")
        
    def save(self, suffix="_optimized"):
        """保存处理后的文件"""
        output_file = self.html_file.with_stem(self.html_file.stem + suffix)
        output_file.write_text(self.content, encoding='utf-8')
        print(f"\n💾 已保存到: {output_file}")
        return output_file
    
    def generate_copy_paste_version(self):
        """生成可直接复制粘贴的版本（只保留 body 内容）"""
        # 提取 body 内容
        body_match = re.search(r'<body[^>]*>(.*?)</body>', self.content, re.DOTALL)
        if body_match:
            body_content = body_match.group(1)
            
            # 移除 container div 包裹
            body_content = re.sub(r'^\s*<div[^>]*>\s*', '', body_content)
            body_content = re.sub(r'\s*</div>\s*$', '', body_content)
            
            output_file = self.html_file.with_stem(self.html_file.stem + "_paste")
            output_file.write_text(body_content.strip(), encoding='utf-8')
            print(f"💾 粘贴版已保存: {output_file}")
            return output_file
        return None

def main():
    if len(sys.argv) < 2:
        print("用法: python3 wechat_html_processor.py <html文件> [--auto]")
        print("示例: python3 wechat_html_processor.py wechat-article-html.html")
        print("       python3 wechat_html_processor.py wechat-article-html.html --auto")
        sys.exit(1)
    
    html_file = sys.argv[1]
    auto_skip = '--auto' in sys.argv
    
    print("=" * 60)
    print("📝 公众号文章 HTML 处理工具")
    print("=" * 60)
    
    processor = WechatArticleProcessor(html_file)
    
    # 步骤 1: 提取并替换图片
    images = processor.extract_images()
    if images:
        processor.replace_images_interactive(auto_skip=auto_skip)
    else:
        print("ℹ️  未发现需要替换的图片")
    
    # 步骤 2: 优化 HTML
    print("\n" + "=" * 60)
    print("🔧 优化 HTML 格式...")
    processor.optimize_for_wechat()
    
    # 步骤 3: 生成内联样式版本
    print("\n" + "=" * 60)
    print("🎨 生成内联样式版本...")
    processor.generate_inline_html()
    
    # 步骤 4: 保存文件
    print("\n" + "=" * 60)
    print("💾 保存文件...")
    optimized_file = processor.save("_optimized")
    paste_file = processor.generate_copy_paste_version()
    
    print("\n" + "=" * 60)
    print("✅ 处理完成！")
    print("=" * 60)
    print(f"\n📄 优化版 HTML: {optimized_file}")
    print(f"   用浏览器打开，复制全部内容粘贴到公众号")
    if paste_file:
        print(f"\n📄 粘贴版 HTML: {paste_file}")
        print(f"   直接复制内容粘贴到公众号编辑器")
    
    print("\n💡 提示：")
    print("   1. 代码块建议截图后插入")
    print("   2. 粘贴后在公众号编辑器微调样式")
    print("   3. 发表前务必手机预览检查")

if __name__ == "__main__":
    main()
