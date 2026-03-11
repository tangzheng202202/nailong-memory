---
name: file-organizer
description: 文件整理助手 - 自动整理下载文件夹、重复文件检测、清理旧文件
---

# File Organizer

## 功能

- 自动整理下载文件夹（按类型和日期分类）
- 重复文件检测（基于 MD5）
- 安全清理重复文件（移动到隔离目录）
- 清理旧文件（支持预览模式）

## 使用

```bash
# 整理下载文件夹
python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py organize

# 预览整理（不实际移动）
python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py organize --dry-run

# 查找重复文件
python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py duplicates

# 清理重复文件（保留最老的）
python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py clean-duplicates

# 清理30天前的旧文件（预览）
python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py clean-old 30 --dry-run

# 真正清理旧文件
python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py clean-old 30
```

## 文件分类

| 分类 | 扩展名 |
|------|--------|
| 图片 | .jpg, .png, .gif, .svg, .webp |
| 文档 | .pdf, .doc, .xls, .ppt, .txt, .md |
| 视频 | .mp4, .avi, .mov, .mkv |
| 音频 | .mp3, .wav, .flac |
| 压缩 | .zip, .rar, .7z |
| 程序 | .exe, .dmg, .pkg |
| 代码 | .py, .js, .html, .json |

## 目录结构

```
~/Downloads/
├── _organized/          # 整理后的文件
│   ├── 图片/
│   │   ├── 2024-03/
│   │   └── 2024-04/
│   ├── 文档/
│   └── ...
└── _duplicates/         # 重复文件（隔离区）
```

## 安全设计

- 重复文件先移动到隔离区，不直接删除
- 支持 `--dry-run` 预览所有操作
- 文件名冲突自动添加序号

## 定时整理

```bash
# 每周日凌晨2点整理
openclaw cron add --name "整理下载文件夹" --schedule "0 2 * * 0" \
  --command "python3 ~/.openclaw/workspace/skills/file-organizer/scripts/organize.py organize"
```
