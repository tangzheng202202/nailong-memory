---
name: note-organizer
description: 笔记整理助手 - 自动归档、打标签、生成索引，支持 Markdown
---

# Note Organizer

## 功能

- 自动归档笔记（按年月分类）
- 智能标签提取（基于内容和文件名）
- 生成索引页面（README.md）
- 支持全文检索

## 使用

```bash
# 整理所有笔记
python3 ~/.openclaw/workspace/skills/note-organizer/scripts/organize.py organize

# 生成索引页面
python3 ~/.openclaw/workspace/skills/note-organizer/scripts/organize.py index

# 查看统计
python3 ~/.openclaw/workspace/skills/note-organizer/scripts/organize.py stats
```

## 笔记存放位置

`~/.openclaw/workspace/notes/`

## 自动标签规则

| 关键词 | 标签 |
|--------|------|
| 会议/纪要/讨论 | #会议 |
| 需求/PRD/文档 | #需求 |
| bug/问题/修复 | #bug |
| 想法/灵感/思考 | #想法 |
| 学习/笔记/教程 | #学习 |
| 项目/进度/计划 | #项目 |
| 财务/预算/成本 | #财务 |
| 客户/拜访/销售 | #客户 |
| 技术/代码/架构 | #技术 |
| 生活/日记/随笔 | #生活 |

## 工作流程

1. 把 Markdown 笔记放到 `notes/` 目录
2. 运行 `organize` 自动归档和打标签
3. 运行 `index` 生成索引页面
4. 通过 `README.md` 浏览所有笔记

## 定时整理

```bash
openclaw cron add --name "整理笔记" --schedule "0 2 * * *" \
  --command "python3 ~/.openclaw/workspace/skills/note-organizer/scripts/organize.py organize && python3 ~/.openclaw/workspace/skills/note-organizer/scripts/organize.py index"
```
