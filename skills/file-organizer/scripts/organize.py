#!/usr/bin/env python3
"""
文件整理助手 - 自动整理下载文件夹、重复文件检测
"""

import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
DOWNLOADS_DIR = Path.home() / "Downloads"
ORGANIZED_DIR = Path.home() / "Downloads" / "_organized"
DUPLICATES_DIR = Path.home() / "Downloads" / "_duplicates"

# 文件类型映射
FILE_CATEGORIES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "文档": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv"],
    "视频": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "压缩": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "程序": [".exe", ".dmg", ".pkg", ".deb", ".rpm", ".app"],
    "代码": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml"],
}

class FileOrganizer:
    def __init__(self):
        ORGANIZED_DIR.mkdir(exist_ok=True)
        DUPLICATES_DIR.mkdir(exist_ok=True)
    
    def _get_file_hash(self, filepath, chunk_size=8192):
        """计算文件 MD5"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def _get_category(self, filepath):
        """获取文件分类"""
        ext = filepath.suffix.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return "其他"
    
    def _safe_move(self, src, dst):
        """安全移动文件"""
        try:
            # 如果目标已存在，添加数字后缀
            if dst.exists():
                stem = dst.stem
                suffix = dst.suffix
                counter = 1
                while dst.exists():
                    dst = dst.with_name(f"{stem}_{counter}{suffix}")
                    counter += 1
            
            shutil.move(str(src), str(dst))
            return True
        except Exception as e:
            print(f"  ❌ 移动失败 {src}: {e}")
            return False
    
    def organize_downloads(self, dry_run=False):
        """整理下载文件夹"""
        print(f"📂 整理下载文件夹: {DOWNLOADS_DIR}")
        
        stats = defaultdict(int)
        
        for filepath in DOWNLOADS_DIR.iterdir():
            # 跳过目录和隐藏文件
            if not filepath.is_file() or filepath.name.startswith("."):
                continue
            
            # 跳过已整理的目录
            if filepath.parent in [ORGANIZED_DIR, DUPLICATES_DIR]:
                continue
            
            category = self._get_category(filepath)
            
            # 创建分类目录
            category_dir = ORGANIZED_DIR / category
            category_dir.mkdir(exist_ok=True)
            
            # 按年月创建子目录
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            subdir = category_dir / f"{mtime.year}-{mtime.month:02d}"
            subdir.mkdir(exist_ok=True)
            
            # 移动文件
            dst = subdir / filepath.name
            
            if dry_run:
                print(f"  [预览] {filepath.name} -> {subdir}")
            else:
                if self._safe_move(filepath, dst):
                    print(f"  ✅ {filepath.name} -> {category}/{subdir.name}")
                    stats[category] += 1
                else:
                    stats["失败"] += 1
        
        if not dry_run:
            print(f"\n📊 整理完成:")
            for category, count in sorted(stats.items()):
                print(f"  {category}: {count} 个文件")
        
        return stats
    
    def find_duplicates(self, scan_dir=None):
        """查找重复文件"""
        if scan_dir is None:
            scan_dir = DOWNLOADS_DIR
        
        print(f"🔍 扫描重复文件: {scan_dir}")
        
        # 按大小分组
        size_map = defaultdict(list)
        for filepath in Path(scan_dir).rglob("*"):
            if filepath.is_file() and not filepath.name.startswith("."):
                try:
                    size = filepath.stat().st_size
                    size_map[size].append(filepath)
                except:
                    pass
        
        # 只检查大小相同的文件
        duplicates = []
        total_scanned = 0
        
        for size, files in size_map.items():
            if len(files) < 2:
                continue
            
            # 计算哈希
            hash_map = defaultdict(list)
            for filepath in files:
                file_hash = self._get_file_hash(filepath)
                total_scanned += 1
                if file_hash:
                    hash_map[file_hash].append(filepath)
            
            # 找出重复
            for file_hash, file_list in hash_map.items():
                if len(file_list) > 1:
                    duplicates.append(file_list)
        
        print(f"  扫描了 {total_scanned} 个文件")
        
        if not duplicates:
            print("  ✅ 未发现重复文件")
            return []
        
        print(f"\n🗂️  发现 {len(duplicates)} 组重复文件:")
        for i, group in enumerate(duplicates, 1):
            print(f"\n  组 {i} ({len(group)} 个文件):")
            for filepath in group:
                size = filepath.stat().st_size / 1024
                print(f"    - {filepath} ({size:.1f} KB)")
        
        return duplicates
    
    def remove_duplicates(self, duplicates, keep_oldest=True):
        """删除重复文件，保留一个"""
        if not duplicates:
            return
        
        removed = 0
        freed_space = 0
        
        for group in duplicates:
            # 按修改时间排序
            sorted_files = sorted(group, key=lambda p: p.stat().st_mtime)
            
            if keep_oldest:
                # 保留最老的，删除其他的
                to_remove = sorted_files[1:]
            else:
                # 保留最新的，删除其他的
                to_remove = sorted_files[:-1]
            
            for filepath in to_remove:
                try:
                    size = filepath.stat().st_size
                    
                    # 移动到重复文件目录（而不是直接删除，安全起见）
                    dst = DUPLICATES_DIR / filepath.name
                    shutil.move(str(filepath), str(dst))
                    
                    removed += 1
                    freed_space += size
                    print(f"  🗑️  {filepath.name}")
                except Exception as e:
                    print(f"  ❌ 无法处理 {filepath}: {e}")
        
        print(f"\n📊 清理完成:")
        print(f"  移动文件: {removed} 个")
        print(f"  释放空间: {freed_space / 1024 / 1024:.2f} MB")
        print(f"  文件位置: {DUPLICATES_DIR}")
    
    def clean_old_files(self, days=30, dry_run=False):
        """清理旧文件"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        print(f"🧹 清理 {days} 天前的旧文件...")
        
        removed = 0
        for filepath in DOWNLOADS_DIR.rglob("*"):
            if not filepath.is_file():
                continue
            
            try:
                if filepath.stat().st_mtime < cutoff:
                    if dry_run:
                        print(f"  [预览] 删除: {filepath}")
                    else:
                        filepath.unlink()
                        print(f"  🗑️  删除: {filepath.name}")
                        removed += 1
            except:
                pass
        
        print(f"  {'预览' if dry_run else '清理'}完成: {removed} 个文件")
        return removed

def main():
    import sys
    
    organizer = FileOrganizer()
    
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} organize [--dry-run]   # 整理下载文件夹")
        print(f"  {sys.argv[0]} duplicates             # 查找重复文件")
        print(f"  {sys.argv[0]} clean-duplicates       # 清理重复文件")
        print(f"  {sys.argv[0]} clean-old [天数]       # 清理旧文件")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "organize":
        dry_run = "--dry-run" in sys.argv
        organizer.organize_downloads(dry_run=dry_run)
    
    elif command == "duplicates":
        organizer.find_duplicates()
    
    elif command == "clean-duplicates":
        dups = organizer.find_duplicates()
        if dups:
            organizer.remove_duplicates(dups)
    
    elif command == "clean-old":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        dry_run = "--dry-run" in sys.argv
        organizer.clean_old_files(days=days, dry_run=dry_run)
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
