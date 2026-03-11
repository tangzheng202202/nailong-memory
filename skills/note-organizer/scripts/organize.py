#!/usr/bin/env python3
"""
笔记整理助手 - 自动归档、打标签、生成索引
支持 Markdown 文件
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
NOTES_DIR = Path.home() / ".openclaw" / "workspace" / "notes"
ARCHIVE_DIR = NOTES_DIR / "archive"
INDEX_FILE = NOTES_DIR / ".index.json"

# 标签规则（关键词 -> 标签）
TAG_RULES = {
    "会议|纪要|讨论": "#会议",
    "需求|PRD|文档": "#需求",
    "bug|问题|修复": "#bug",
    "想法|灵感|思考": "#想法",
    "学习|笔记|教程": "#学习",
    "项目|进度|计划": "#项目",
    "财务|预算|成本": "#财务",
    "客户|拜访|销售": "#客户",
    "技术|代码|架构": "#技术",
    "生活|日记|随笔": "#生活",
}

class NoteOrganizer:
    def __init__(self):
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVE_DIR.mkdir(exist_ok=True)
        self.index = self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"files": {}, "tags": defaultdict(list)}
    
    def _save_index(self):
        """保存索引"""
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _extract_tags(self, content, filename):
        """提取标签"""
        tags = set()
        
        # 从文件名提取
        for pattern, tag in TAG_RULES.items():
            if re.search(pattern, filename, re.I):
                tags.add(tag)
        
        # 从内容提取
        for pattern, tag in TAG_RULES.items():
            if re.search(pattern, content, re.I):
                tags.add(tag)
        
        # 提取已有标签 (#tag 格式)
        existing = re.findall(r'#\w+', content)
        tags.update(existing)
        
        return sorted(list(tags))
    
    def _extract_title(self, content):
        """提取标题"""
        # 尝试提取第一个 # 标题
        match = re.search(r'^#\s+(.+)$', content, re.M)
        if match:
            return match.group(1).strip()
        
        # 尝试提取第一个非空行
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:50]
        
        return "无标题"
    
    def _get_summary(self, content, max_len=200):
        """获取摘要"""
        # 移除 Markdown 标记
        text = re.sub(r'[#*`\[\]()!]', '', content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_len] + "..." if len(text) > max_len else text
    
    def organize_file(self, filepath):
        """整理单个文件"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return None
        
        # 提取信息
        title = self._extract_title(content)
        tags = self._extract_tags(content, filepath.name)
        summary = self._get_summary(content)
        stat = filepath.stat()
        
        # 确定归档目录（按年月）
        date = datetime.fromtimestamp(stat.st_mtime)
        archive_subdir = ARCHIVE_DIR / f"{date.year}" / f"{date.month:02d}"
        archive_subdir.mkdir(parents=True, exist_ok=True)
        
        # 生成新文件名（添加日期前缀）
        new_name = f"{date.strftime('%Y%m%d')}-{filepath.name}"
        new_path = archive_subdir / new_name
        
        # 如果文件不在归档目录，移动它
        if filepath.parent != archive_subdir:
            shutil.copy2(filepath, new_path)
            print(f"📁 归档: {filepath.name} -> {new_path}")
        else:
            new_path = filepath
        
        # 更新索引
        file_info = {
            "original_path": str(filepath),
            "archive_path": str(new_path),
            "title": title,
            "tags": tags,
            "summary": summary,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "organized_at": datetime.now().isoformat(),
        }
        
        self.index["files"][str(new_path)] = file_info
        
        # 更新标签索引
        for tag in tags:
            if str(new_path) not in self.index["tags"][tag]:
                self.index["tags"][tag].append(str(new_path))
        
        return file_info
    
    def organize_all(self):
        """整理所有笔记"""
        print("📝 开始整理笔记...")
        count = 0
        
        for filepath in NOTES_DIR.rglob("*.md"):
            # 跳过归档目录
            if ARCHIVE_DIR in filepath.parents or filepath.parent == ARCHIVE_DIR:
                continue
            
            if self.organize_file(filepath):
                count += 1
        
        self._save_index()
        print(f"✅ 整理完成: {count} 个文件")
        return count
    
    def generate_index_page(self):
        """生成索引页面"""
        index_md = NOTES_DIR / "README.md"
        
        lines = [
            "# 笔记索引",
            "",
            f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 按标签分类",
            "",
        ]
        
        # 按标签组织
        for tag in sorted(self.index["tags"].keys()):
            lines.append(f"### {tag}")
            lines.append("")
            
            for filepath in self.index["tags"][tag][:20]:  # 最多显示20个
                info = self.index["files"].get(filepath, {})
                title = info.get("title", Path(filepath).name)
                summary = info.get("summary", "")[:80]
                lines.append(f"- [{title}]({filepath}) - {summary}")
            
            if len(self.index["tags"][tag]) > 20:
                lines.append(f"- ... 还有 {len(self.index['tags'][tag]) - 20} 个")
            
            lines.append("")
        
        # 最近更新
        lines.extend([
            "## 最近更新",
            "",
        ])
        
        recent = sorted(
            self.index["files"].items(),
            key=lambda x: x[1].get("mtime", 0),
            reverse=True
        )[:10]
        
        for filepath, info in recent:
            date = datetime.fromtimestamp(info.get("mtime", 0)).strftime("%m-%d")
            title = info.get("title", Path(filepath).name)
            lines.append(f"- [{date}] [{title}]({filepath})")
        
        with open(index_md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"📑 索引已生成: {index_md}")
        return index_md
    
    def stats(self):
        """统计信息"""
        return {
            "total_files": len(self.index["files"]),
            "total_tags": len(self.index["tags"]),
            "tag_counts": {tag: len(files) for tag, files in self.index["tags"].items()}
        }

def main():
    import sys
    
    organizer = NoteOrganizer()
    
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} organize     # 整理所有笔记")
        print(f"  {sys.argv[0]} index        # 生成索引页面")
        print(f"  {sys.argv[0]} stats        # 查看统计")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "organize":
        organizer.organize_all()
    elif command == "index":
        organizer.generate_index_page()
    elif command == "stats":
        stats = organizer.stats()
        print("📊 笔记统计:")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  标签数量: {stats['total_tags']}")
        print("\n标签分布:")
        for tag, count in sorted(stats['tag_counts'].items(), key=lambda x: -x[1]):
            print(f"  {tag}: {count}")
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
