#!/usr/bin/env python3
"""
快捷文件搜索 - 全文索引，比 Spotlight 快
支持文件名和内容搜索
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from fnmatch import fnmatch

# 配置
INDEX_DB = Path.home() / ".openclaw" / "index" / "file_index.db"
SCAN_DIRS = [
    Path.home() / "Documents",
    Path.home() / "Desktop", 
    Path.home() / "Downloads",
    Path.home() / ".openclaw" / "workspace",
]
EXCLUDE_PATTERNS = [
    "*.tmp", "*.temp", "*.log", "*.cache",
    "node_modules", ".git", ".svn", "__pycache__",
    ".DS_Store", "Thumbs.db",
    "*.exe", "*.dll", "*.so", "*.dylib",
]
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml',
    '.xml', '.html', '.css', '.sh', '.bash', '.zsh', '.conf',
    '.cfg', '.ini', '.log', '.csv', '.sql', '.c', '.cpp', '.h',
    '.java', '.go', '.rs', '.rb', '.php', '.swift', '.kt',
}

class FileIndex:
    def __init__(self):
        INDEX_DB.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(INDEX_DB))
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                name TEXT,
                content_hash TEXT,
                content_preview TEXT,
                size INTEGER,
                mtime REAL,
                indexed_at REAL
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON files(name)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_path ON files(path)")
        self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(path, content)")
        self.conn.commit()
    
    def should_index(self, filepath):
        """检查是否应该索引该文件"""
        # 检查排除模式
        for pattern in EXCLUDE_PATTERNS:
            if pattern in str(filepath) or fnmatch(filepath.name, pattern):
                return False
        
        # 检查文件大小（最大 10MB）
        try:
            if filepath.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            return False
        
        return True
    
    def is_text_file(self, filepath):
        """检查是否是文本文件"""
        ext = filepath.suffix.lower()
        if ext in TEXT_EXTENSIONS:
            return True
        
        # 尝试读取前 1024 字节检测
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' not in chunk
        except:
            return False
    
    def read_content(self, filepath, max_chars=5000):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_chars)
        except:
            return ""
    
    def index_file(self, filepath):
        """索引单个文件"""
        try:
            stat = filepath.stat()
            content = ""
            content_hash = ""
            
            if self.is_text_file(filepath):
                content = self.read_content(filepath)
                content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
            
            # 插入或更新
            self.conn.execute("""
                INSERT OR REPLACE INTO files 
                (path, name, content_hash, content_preview, size, mtime, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(filepath),
                filepath.name,
                content_hash,
                content[:500] if content else "",
                stat.st_size,
                stat.st_mtime,
                datetime.now().timestamp()
            ))
            
            # 更新 FTS
            if content:
                self.conn.execute("""
                    INSERT OR REPLACE INTO content_fts (path, content)
                    VALUES (?, ?)
                """, (str(filepath), content))
            
            return True
        except Exception as e:
            return False
    
    def scan(self, force=False):
        """扫描目录建立索引"""
        print("🔍 开始扫描文件...")
        count = 0
        updated = 0
        
        for scan_dir in SCAN_DIRS:
            if not scan_dir.exists():
                continue
            
            for root, dirs, files in os.walk(scan_dir):
                # 过滤目录
                dirs[:] = [d for d in dirs if not any(p in d for p in EXCLUDE_PATTERNS)]
                
                for filename in files:
                    filepath = Path(root) / filename
                    
                    if not self.should_index(filepath):
                        continue
                    
                    # 检查是否需要更新
                    if not force:
                        try:
                            stat = filepath.stat()
                            cursor = self.conn.execute(
                                "SELECT mtime FROM files WHERE path = ?",
                                (str(filepath),)
                            )
                            row = cursor.fetchone()
                            if row and row[0] >= stat.st_mtime:
                                continue
                        except:
                            pass
                    
                    if self.index_file(filepath):
                        count += 1
                        updated += 1
                        if count % 100 == 0:
                            print(f"  已索引 {count} 个文件...")
        
        self.conn.commit()
        print(f"✅ 索引完成: 新增/更新 {updated} 个文件")
        return count
    
    def search(self, keyword, search_content=False, limit=20):
        """搜索文件"""
        results = []
        keyword_lower = keyword.lower()
        
        # 文件名搜索
        cursor = self.conn.execute(
            "SELECT path, name, size, mtime FROM files WHERE name LIKE ? LIMIT ?",
            (f"%{keyword}%", limit)
        )
        
        for row in cursor:
            results.append({
                "path": row[0],
                "name": row[1],
                "size": row[2],
                "mtime": datetime.fromtimestamp(row[3]).strftime("%Y-%m-%d %H:%M"),
                "match_type": "filename"
            })
        
        # 内容搜索
        if search_content and len(results) < limit:
            try:
                cursor = self.conn.execute(
                    "SELECT path, content FROM content_fts WHERE content MATCH ? LIMIT ?",
                    (keyword, limit - len(results))
                )
                
                for row in cursor:
                    # 避免重复
                    if not any(r["path"] == row[0] for r in results):
                        filepath = Path(row[0])
                        try:
                            stat = filepath.stat()
                            results.append({
                                "path": row[0],
                                "name": filepath.name,
                                "size": stat.st_size,
                                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                                "match_type": "content",
                                "preview": row[1][:200] if row[1] else ""
                            })
                        except:
                            pass
            except:
                pass
        
        return results
    
    def stats(self):
        """获取索引统计"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM content_fts")
        indexed_content = cursor.fetchone()[0]
        
        cursor = self.conn.execute(
            "SELECT MAX(indexed_at) FROM files"
        )
        last_update = cursor.fetchone()[0]
        
        return {
            "total_files": total_files,
            "indexed_content": indexed_content,
            "last_update": datetime.fromtimestamp(last_update).strftime("%Y-%m-%d %H:%M:%S") if last_update else "Never"
        }

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} scan [--force]     # 扫描建立索引")
        print(f"  {sys.argv[0]} search <关键词> [--content]  # 搜索文件")
        print(f"  {sys.argv[0]} stats              # 查看索引统计")
        sys.exit(1)
    
    index = FileIndex()
    command = sys.argv[1]
    
    if command == "scan":
        force = "--force" in sys.argv
        index.scan(force=force)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("错误: 请提供搜索关键词")
            sys.exit(1)
        
        keyword = sys.argv[2]
        search_content = "--content" in sys.argv
        
        print(f"🔍 搜索: '{keyword}'")
        results = index.search(keyword, search_content=search_content)
        
        if not results:
            print("❌ 未找到匹配文件")
        else:
            print(f"\n找到 {len(results)} 个结果:\n")
            for i, r in enumerate(results[:20], 1):
                match_icon = "📄" if r["match_type"] == "filename" else "📝"
                print(f"{i}. {match_icon} {r['name']}")
                print(f"   📁 {r['path']}")
                print(f"   📅 {r['mtime']} | 📦 {r['size'] / 1024:.1f} KB")
                if "preview" in r:
                    print(f"   👁️  {r['preview'][:100]}...")
                print()
    
    elif command == "stats":
        stats = index.stats()
        print("📊 索引统计:")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  内容索引: {stats['indexed_content']}")
        print(f"  最后更新: {stats['last_update']}")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
