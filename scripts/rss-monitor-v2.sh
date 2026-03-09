#!/bin/bash
# RSS 监控 v2 - 国内可访问源

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/rss-monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

echo "📡 RSS 监控 v2 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "使用国内可访问 RSS 源" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

TOTAL_FOUND=0

# ========== 即刻 RSS ==========
echo "📱 即刻热门..." >> "$LOG_FILE"
JIKAN_RSS="https://rsshub.app/jike/trending"
JIKAN_CONTENT=$(curl -s --max-time 15 "$JIKAN_RSS" 2>/dev/null)
if [ -n "$JIKAN_CONTENT" ] && echo "$JIKAN_CONTENT" | grep -q "<item>"; then
    JIKAN_ITEMS=$(echo "$JIKAN_CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -5)
    if [ -n "$JIKAN_ITEMS" ]; then
        echo "✅ 即刻热门 (5条):" >> "$LOG_FILE"
        echo "$JIKAN_ITEMS" | sed 's/^/  - /' >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + 5))
    fi
else
    echo "⚠️ 即刻 RSS 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 36氪 RSS ==========
echo "💼 36氪快讯..." >> "$LOG_FILE"
KR36_RSS="https://rsshub.app/36kr/newsflashes"
KR36_CONTENT=$(curl -s --max-time 15 "$KR36_RSS" 2>/dev/null)
if [ -n "$KR36_CONTENT" ] && echo "$KR36_CONTENT" | grep -q "<item>"; then
    KR36_ITEMS=$(echo "$KR36_CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -5)
    if [ -n "$KR36_ITEMS" ]; then
        echo "✅ 36氪快讯 (5条):" >> "$LOG_FILE"
        echo "$KR36_ITEMS" | sed 's/^/  - /' >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + 5))
    fi
else
    echo "⚠️ 36氪 RSS 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 阮一峰博客 ==========
echo "📚 阮一峰周刊..." >> "$LOG_FILE"
RUANYF_RSS="https://rsshub.app/ruanyf/weekly"
RUANYF_CONTENT=$(curl -s --max-time 15 "$RUANYF_RSS" 2>/dev/null)
if [ -n "$RUANYF_CONTENT" ] && echo "$RUANYF_CONTENT" | grep -q "<item>"; then
    RUANYF_ITEMS=$(echo "$RUANYF_CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -3)
    if [ -n "$RUANYF_ITEMS" ]; then
        echo "✅ 阮一峰周刊 (3条):" >> "$LOG_FILE"
        echo "$RUANYF_ITEMS" | sed 's/^/  - /' >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + 3))
    fi
else
    echo "⚠️ 阮一峰 RSS 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 少数派 RSS ==========
echo "📝 少数派热门..." >> "$LOG_FILE"
SSPAI_RSS="https://rsshub.app/sspai/index"
SSPAI_CONTENT=$(curl -s --max-time 15 "$SSPAI_RSS" 2>/dev/null)
if [ -n "$SSPAI_CONTENT" ] && echo "$SSPAI_CONTENT" | grep -q "<item>"; then
    SSPAI_ITEMS=$(echo "$SSPAI_CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -5)
    if [ -n "$SSPAI_ITEMS" ]; then
        echo "✅ 少数派热门 (5条):" >> "$LOG_FILE"
        echo "$SSPAI_ITEMS" | sed 's/^/  - /' >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + 5))
    fi
else
    echo "⚠️ 少数派 RSS 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 总结 ==========
echo "======================================" >> "$LOG_FILE"
echo "✅ RSS 监控完成: $(date +%H:%M)" >> "$LOG_FILE"
echo "总计发现: $TOTAL_FOUND 条内容" >> "$LOG_FILE"

if [ $TOTAL_FOUND -gt 0 ]; then
    MESSAGE="📡 **RSS 监控 v2** ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

📊 总计发现: **$TOTAL_FOUND 条**

使用国内可访问 RSS 源

📄 完整报告: \`$LOG_FILE\`"
    
    export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
    openclaw message send --target "user:$FEISHU_USER" --message "$MESSAGE" --channel feishu 2>/dev/null || echo "⚠️ 推送失败" >> "$LOG_FILE"
fi

jq -n --arg date "$DATE" --arg found "$TOTAL_FOUND" --arg log "$LOG_FILE" '{date: $date, found: $found, log_file: $log}'
