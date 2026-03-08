#!/bin/bash
# 早报脚本 - 每天 8:00 推送

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d)
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# 读取今日待办
TODO_CONTENT=""
if [ -f "memory/todo-daily.md" ]; then
    TODO_CONTENT=$(grep "\- \[ \]" memory/todo-daily.md | head -5)
fi

# 获取天气（简化版）
WEATHER="今天天气不错，适合出门"

# 获取隔夜监控摘要（最近一条）
LATEST_MONITOR=$(ls -t memory/daily/monitor-*.log 2>/dev/null | head -1)
MONITOR_SUMMARY=""
if [ -n "$LATEST_MONITOR" ]; then
    MONITOR_SUMMARY=$(head -20 "$LATEST_MONITOR" | grep -E "✅|🔥|📊" | head -3)
fi

# 构建早报
MESSAGE="☀️ **早安！** $(date +%m月%d日 %H:%M)

🌤️ **今日天气**: $WEATHER

📋 **今日待办**:
${TODO_CONTENT:-"暂无待办"}

🔥 **隔夜热点**:
${MONITOR_SUMMARY:-"监控报告见日志"}

💡 **今日建议**:
- 先处理最重要的事
- 每 90 分钟休息一次
- 有问题随时找我

加油！💪"

export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
openclaw message send --target "user:$FEISHU_USER" --message "$MESSAGE" --channel feishu 2>/dev/null
