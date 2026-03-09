#!/bin/bash
# RSS 监控 v3 - 使用替代数据源
# 不依赖 Nitter/RSSHub

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/rss-monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# 代理配置
PROXY_PORT="${PROXY_PORT:-17890}"
PROXY_URL="http://127.0.0.1:${PROXY_PORT}"
export http_proxy="$PROXY_URL"
export https_proxy="$PROXY_URL"

echo "📡 RSS 监控 v3 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

TOTAL_FOUND=0

# ========== 获取 X 热门话题（通过 Trends API）==========
echo "🐦 X (Twitter) 热门话题..." >> "$LOG_FILE"
# 使用代理访问 trends 页面
X_TRENDS=$(curl -s --max-time 15 -x "$PROXY_URL" "https://trends24.in/united-states/" 2>/dev/null | \
    grep -oE 'data-trend-name="[^"]+"' | \
    sed 's/data-trend-name="//;s/"//' | \
    head -10)

if [ -n "$X_TRENDS" ]; then
    echo "✅ X 热门话题 (10条):" >> "$LOG_FILE"
    echo "$X_TRENDS" | sed 's/^/  - /' >> "$LOG_FILE"
    TOTAL_FOUND=$((TOTAL_FOUND + 10))
else
    echo "⚠️ X 热门获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== YouTube 热门（通过 trending 页面）==========
echo "📺 YouTube 热门..." >> "$LOG_FILE"
YT_TRENDS=$(curl -s --max-time 15 -x "$PROXY_URL" "https://www.youtube.com/feed/trending" 2>/dev/null | \
    grep -oE 'title":{"runs":\[{"text":"[^"]+"\}' | \
    sed 's/title":{"runs":\[{"text":"//;s/"\}]//' | \
    head -10)

if [ -n "$YT_TRENDS" ]; then
    echo "✅ YouTube 热门 (10条):" >> "$LOG_FILE"
    echo "$YT_TRENDS" | sed 's/^/  - /' >> "$LOG_FILE"
    TOTAL_FOUND=$((TOTAL_FOUND + 10))
else
    echo "⚠️ YouTube 热门获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 国内 RSS 源（备用）==========
echo "📱 即刻热门..." >> "$LOG_FILE"
JIKAN_RSS=$(curl -s --max-time 10 "https://rsshub.app/jike/trending" 2>/dev/null)
if [ -n "$JIKAN_RSS" ] && echo "$JIKAN_RSS" | grep -q "<item>"; then
    JIKAN_ITEMS=$(echo "$JIKAN_RSS" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -5)
    if [ -n "$JIKAN_ITEMS" ]; then
        echo "✅ 即刻热门 (5条):" >> "$LOG_FILE"
        echo "$JIKAN_ITEMS" | sed 's/^/  - /' >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + 5))
    fi
else
    echo "⚠️ 即刻 RSS 失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 总结 ==========
echo "======================================" >> "$LOG_FILE"
echo "✅ RSS 监控完成: $(date +%H:%M)" >> "$LOG_FILE"
echo "总计发现: $TOTAL_FOUND 条内容" >> "$LOG_FILE"

if [ $TOTAL_FOUND -gt 0 ]; then
    MESSAGE="📡 **RSS 监控 v3** ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

📊 总计发现: **$TOTAL_FOUND 条**

📄 完整报告: \`$LOG_FILE\`"
    
    export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
    openclaw message send --target "user:$FEISHU_USER" --message "$MESSAGE" --channel feishu 2>/dev/null || echo "⚠️ 推送失败" >> "$LOG_FILE"
fi

jq -n --arg date "$DATE" --arg found "$TOTAL_FOUND" --arg log "$LOG_FILE" '{date: $date, found: $found, log_file: $log}'
