#!/bin/bash
# 晚报脚本 - 每天 21:00 推送

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d)
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# 统计今日完成/未完成
COMPLETED=$(grep "\- \[x\]" memory/todo-daily.md 2>/dev/null | wc -l | tr -d ' ')
PENDING=$(grep "\- \[ \]" memory/todo-daily.md 2>/dev/null | wc -l | tr -d ' ')

# 获取最近监控
LATEST_MONITOR=$(ls -t memory/daily/monitor-*.log 2>/dev/null | head -1)
MONITOR_COUNT=""
if [ -n "$LATEST_MONITOR" ]; then
    MONITOR_COUNT=$(grep -oE "发现: [0-9]+" "$LATEST_MONITOR" | head -1)
fi

# 明日待办（未完成的移过去）
TOMORROW_TODO=$(grep "\- \[ \]" memory/todo-daily.md 2>/dev/null | head -5)

# 构建晚报
MESSAGE="🌙 **晚安！** $(date +%m月%d日 %H:%M)

📊 **今日统计**:
- ✅ 已完成: $COMPLETED 项
- ⏳ 未完成: $PENDING 项
- 🔍 监控发现: ${MONITOR_COUNT:-"见日志"}

📋 **明日待办**:
${TOMORROW_TODO:-"暂无待办"}

💤 **睡前建议**:
- 回顾今日收获
- 准备好明天要用的东西
- 23:00 前睡觉

明天见！🌟"

export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
openclaw message send --target "user:$FEISHU_USER" --message "$MESSAGE" --channel feishu 2>/dev/null

# 清空今日待办，准备明天
echo "# 每日待办提醒
# 创建于: $(date +%Y-%m-%d)
# 提醒时间: 每天 21:00

## 今日待办 ($(date -v+1d +%Y-%m-%d))

$(grep "\- \[ \]" memory/todo-daily.md 2>/dev/null | sed 's/\[ \]/[ ]/')

## 说明

从昨日延续的待办事项。
" > memory/todo-daily.md
