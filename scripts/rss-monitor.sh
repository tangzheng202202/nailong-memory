#!/bin/bash
# RSS 订阅监控脚本
# 数据源: X/YouTube/其他 RSS

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/rss-monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# 代理配置
PROXY_PORT="${PROXY_PORT:-17890}"
PROXY_URL="http://127.0.0.1:${PROXY_PORT}"
export http_proxy="$PROXY_URL"
export https_proxy="$PROXY_URL"
export HTTP_PROXY="$PROXY_URL"
export HTTPS_PROXY="$PROXY_URL"

echo "📡 RSS 订阅监控 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "代理端口: $PROXY_PORT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

TOTAL_FOUND=0

# ========== X (Twitter) - 通过 Nitter RSS ==========
echo "🐦 X (Twitter) 热门..." >> "$LOG_FILE"
# Nitter 实例（可能需要更换）
RSSHub_URL="http://localhost:1200"

# 监控的技术账号（可通过 RSS 订阅）
X_ACCOUNTS=("elonmusk" "sama" "ylecun" "paulg")

# 使用自建 RSSHub 获取 Twitter
for ACCOUNT in "${X_ACCOUNTS[@]}"; do
    RSS_URL="$RSSHub_URL/twitter/user/$ACCOUNT"
    RSS_CONTENT=$(curl -s --max-time 10 "$RSS_URL" 2>/dev/null)
    if [ -n "$RSS_CONTENT" ] && echo "$RSS_CONTENT" | grep -q "<item>"; then
        TWEETS=$(echo "$RSS_CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -3)
        if [ -n "$TWEETS" ]; then
            echo "[@$ACCOUNT]:" >> "$LOG_FILE"
            echo "$TWEETS" | sed 's/^/  - /' >> "$LOG_FILE"
            TOTAL_FOUND=$((TOTAL_FOUND + 3))
        fi
    fi
done

if [ "$TOTAL_FOUND" -eq 0 ]; then
    echo "⚠️ X RSS 获取失败（Nitter 可能被封）" >> "$LOG_FILE"
    echo "替代方案: 使用 RSSHub 自建服务" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== YouTube - 官方 RSS ==========
echo "📺 YouTube 热门..." >> "$LOG_FILE"
# YouTube 有官方 RSS，但需要频道 ID
# 使用 RSSHub 聚合 trending
YOUTUBE_RSS="$RSSHub_URL/youtube/trending"
YT_CONTENT=$(curl -s --max-time 15 -x "$PROXY_URL" "$YOUTUBE_RSS" 2>/dev/null)

if [ -n "$YT_CONTENT" ] && echo "$YT_CONTENT" | grep -q "<item>"; then
    YT_VIDEOS=$(echo "$YT_CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -5)
    echo "✅ YouTube 热门 (5条):" >> "$LOG_FILE"
    echo "$YT_VIDEOS" | sed 's/^/  - /' >> "$LOG_FILE"
    TOTAL_FOUND=$((TOTAL_FOUND + 5))
else
    echo "⚠️ YouTube RSS 获取失败" >> "$LOG_FILE"
    echo "替代方案: 使用 YouTube Data API" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 其他 RSS 源 ==========
# 可以添加更多 RSS 源

echo "======================================" >> "$LOG_FILE"
echo "✅ RSS 监控完成: $(date +%H:%M)" >> "$LOG_FILE"
echo "总计发现: $TOTAL_FOUND 条内容" >> "$LOG_FILE"

# 推送到飞书（仅当有新内容时）
if [ $TOTAL_FOUND -gt 0 ]; then
    MESSAGE="📡 **RSS 订阅报告** ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

📊 总计发现: **$TOTAL_FOUND 条**

📄 完整报告: \`$LOG_FILE\`"
    
    export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
    /Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin/openclaw message send \
        --target "user:$FEISHU_USER" \
        --message "$MESSAGE" \
        --channel feishu 2>/dev/null || echo "⚠️ 推送失败" >> "$LOG_FILE"
fi

jq -n --arg date "$DATE" --arg found "$TOTAL_FOUND" --arg log "$LOG_FILE" '{date: $date, found: $found, log_file: $log}'
