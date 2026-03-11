---
name: quick-search
description: 快捷文件搜索 - 全文索引，比 Spotlight 快，支持文件名和内容搜索
---

# Quick Search

## 功能

- 快速全文文件搜索
- 支持文件名和内容搜索
- SQLite + FTS5 索引，比 Spotlight 快
- 自动排除临时文件和目录

## 使用

```bash
# 建立索引（首次运行）
python3 ~/.openclaw/workspace/skills/quick-search/scripts/search.py scan

# 强制重建索引
python3 ~/.openclaw/workspace/skills/quick-search/scripts/search.py scan --force

# 搜索文件名
python3 ~/.openclaw/workspace/skills/quick-search/scripts/search.py search "预算"

# 搜索内容（较慢）
python3 ~/.openclaw/workspace/skills/quick-search/scripts/search.py search "OpenClaw" --content

# 查看索引统计
python3 ~/.openclaw/workspace/skills/quick-search/scripts/search.py stats
```

## 索引范围

默认索引目录：
- ~/Documents
- ~/Desktop
- ~/Downloads
- ~/.openclaw/workspace

## 排除项

自动排除：node_modules, .git, __pycache__, *.tmp, *.log 等

## 定时更新

建议设置定时任务自动更新索引：
```bash
openclaw cron add --name "更新文件索引" --schedule "0 */6 * * *" \
  --command "python3 ~/.openclaw/workspace/skills/quick-search/scripts/search.py scan"
```
