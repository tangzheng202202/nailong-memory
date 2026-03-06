#!/bin/bash
# 奶龙每日 Skill 推荐
# 运行时间: 每天 21:00

cd /Users/mac/.openclaw/workspace

# 创建日志目录
mkdir -p memory/daily

DATE=$(date +%Y-%m-%d)
LOG_FILE="memory/daily/clawhub-rec-$DATE.log"

echo "🎯 奶龙 Skill 推荐 - $DATE" > "$LOG_FILE"
echo "================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 随机选一个搜索词
QUERIES=("content" "video" "social" "automation" "analytics" "marketing" "creator" "trending")
QUERY=${QUERIES[$RANDOM % ${#QUERIES[@]}]}

echo "🔍 今日搜索: $QUERY" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 搜索并取前3个
clawhub search "$QUERY" --limit 3 2>&1 >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "✅ 完成: $(date +%H:%M)" >> "$LOG_FILE"

# 输出到 stdout 用于飞书推送
cat "$LOG_FILE"
