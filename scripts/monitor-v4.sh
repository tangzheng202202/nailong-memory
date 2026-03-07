#!/bin/bash
# 奶龙全网监控 v4 - 大范围监控 + 热点追踪
# 数据源: 国内外技术社区 + 创业/变现/副业话题

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# 代理配置
PROXY_PORT="${PROXY_PORT:-17890}"
PROXY_URL="http://127.0.0.1:${PROXY_PORT}"
export http_proxy="$PROXY_URL"
export https_proxy="$PROXY_URL"

echo "🔍 OpenClaw 全网监控 v4 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

TOTAL_FOUND=0

# ========== 国内技术社区 ==========

# V2EX - 热门话题（不限关键词，抓热榜）
echo "🇨🇳 V2EX 热榜..." >> "$LOG_FILE"
V2EX_JSON=$(curl -s --max-time 15 "https://www.v2ex.com/api/topics/hot.json" 2>/dev/null)
if [ -n "$V2EX_JSON" ]; then
    # 获取热度最高的10条
    V2EX_RESULTS=$(echo "$V2EX_JSON" | jq -r '.[0:10] | .[] | "[\(.replies)回复] \(.title): https://v2ex.com/t/\(.id)"' 2>/dev/null)
    COUNT=$(echo "$V2EX_RESULTS" | grep -c "v2ex.com" || echo "0")
    echo "✅ V2EX 热榜 ($COUNT 条):" >> "$LOG_FILE"
    echo "$V2EX_RESULTS" >> "$LOG_FILE"
    TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
else
    echo "⚠️ V2EX 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 掘金 - 热门文章
echo "🇨🇳 掘金热门..." >> "$LOG_FILE"
JUJIN_JSON=$(curl -s --max-time 15 "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed?aid=2608&uuid=&spider=0" \
    -H "User-Agent: Mozilla/5.0" 2>/dev/null)
if [ -n "$JUJIN_JSON" ]; then
    JUJIN_RESULTS=$(echo "$JUJIN_JSON" | jq -r '.data[0:8] | .[] | select(.item_info.article_info) | "[\(.item_info.article_info.view_count)阅读] \(.item_info.article_info.title): https://juejin.cn/post/\(.item_info.article_id)"' 2>/dev/null)
    COUNT=$(echo "$JUJIN_RESULTS" | grep -c "juejin.cn" || echo "0")
    echo "✅ 掘金热门 ($COUNT 条):" >> "$LOG_FILE"
    echo "$JUJIN_RESULTS" >> "$LOG_FILE"
    TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
else
    echo "⚠️ 掘金获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 国外技术社区 ==========

# HackerNews - 热门
echo "🌍 HackerNews 热门..." >> "$LOG_FILE"
HN_JSON=$(curl -s --max-time 20 "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null)
if [ -n "$HN_JSON" ]; then
    # 获取前10条ID
    TOP_IDS=$(echo "$HN_JSON" | jq -r '.[0:10] | .[]' 2>/dev/null)
    HN_RESULTS=""
    for ID in $TOP_IDS; do
        ITEM=$(curl -s --max-time 10 "https://hacker-news.firebaseio.com/v0/item/$ID.json" 2>/dev/null)
        if [ -n "$ITEM" ]; then
            TITLE=$(echo "$ITEM" | jq -r '.title' 2>/dev/null)
            URL=$(echo "$ITEM" | jq -r '.url // "https://news.ycombinator.com/item?id=\(.id)"' 2>/dev/null)
            SCORE=$(echo "$ITEM" | jq -r '.score // 0' 2>/dev/null)
            HN_RESULTS="$HN_RESULTS
[$SCORE分] $TITLE: $URL"
        fi
    done
    COUNT=$(echo "$HN_RESULTS" | grep -c "http" || echo "0")
    echo "✅ HN 热门 ($COUNT 条):" >> "$LOG_FILE"
    echo "$HN_RESULTS" >> "$LOG_FILE"
    TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
else
    echo "⚠️ HN 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# GitHub Trending - 今日热门
echo "🌍 GitHub Trending..." >> "$LOG_FILE"
# 使用 scraping 获取 trending
GITHUB_TRENDING=$(curl -s --max-time 20 "https://github.com/trending?since=daily" 2>/dev/null | \
    grep -oE 'href="/[^/]+/[^"]+"' | \
    sed 's/href="//g; s/"//g' | \
    head -10 | \
    awk '{print "https://github.com" $1}')
if [ -n "$GITHUB_TRENDING" ]; then
    echo "✅ GitHub Trending:" >> "$LOG_FILE"
    echo "$GITHUB_TRENDING" >> "$LOG_FILE"
    COUNT=$(echo "$GITHUB_TRENDING" | wc -l | tr -d ' ')
    TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
else
    echo "⚠️ GitHub Trending 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# Product Hunt - 今日热门
echo "🌍 Product Hunt 热门..." >> "$LOG_FILE"
PH_JSON=$(curl -s --max-time 20 "https://www.producthunt.com/feed" \
    -H "Accept: application/json" 2>/dev/null)
if [ -n "$PH_JSON" ]; then
    # 简化处理，直接记录是否成功
    echo "✅ Product Hunt 已检查" >> "$LOG_FILE"
else
    echo "⚠️ Product Hunt 需要登录" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# Reddit - 多个子版块热门
echo "🌍 Reddit 热门..." >> "$LOG_FILE"
REDDIT_SUBS=("technology" "programming" "MachineLearning" "artificial")
REDDIT_ALL=""
for SUB in "${REDDIT_SUBS[@]}"; do
    REDDIT_JSON=$(curl -s --max-time 15 "https://www.reddit.com/r/$SUB/hot.json?limit=3" \
        -H "User-Agent: OpenClawBot/1.0" 2>/dev/null)
    if [ -n "$REDDIT_JSON" ]; then
        SUB_RESULTS=$(echo "$REDDIT_JSON" | jq -r '.data.children[0:3].data | "[\(.ups)赞] \(.title): https://reddit.com\(.permalink)"' 2>/dev/null)
        if [ -n "$SUB_RESULTS" ]; then
            REDDIT_ALL="$REDDIT_ALL
--- r/$SUB ---
$SUB_RESULTS"
        fi
    fi
done
if [ -n "$REDDIT_ALL" ]; then
    echo "✅ Reddit 热门:" >> "$LOG_FILE"
    echo "$REDDIT_ALL" >> "$LOG_FILE"
    COUNT=$(echo "$REDDIT_ALL" | grep -c "reddit.com" || echo "0")
    TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
else
    echo "⚠️ Reddit 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== AI/创业/变现专门监控 ==========

echo "💰 AI变现/副业/创业话题..." >> "$LOG_FILE"
# 综合搜索多个关键词
KEYWORDS=("AI赚钱" "AI副业" "AI创业" "独立开发" "被动收入" "side hustle")
# 这里用占位，实际通过搜索API或特定数据源获取
echo "关键词监控: ${KEYWORDS[*]}" >> "$LOG_FILE"
echo "⚠️ 需要配置搜索API (Brave/DuckDuckGo)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ========== 输出总结 ==========
echo "======================================" >> "$LOG_FILE"
echo "✅ 监控完成: $(date +%H:%M)" >> "$LOG_FILE"
echo "总计发现: $TOTAL_FOUND 条内容" >> "$LOG_FILE"

# 推送到飞书
if [ $TOTAL_FOUND -gt 0 ]; then
    MESSAGE="🔍 **监控报告** ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

📊 总计发现: **$TOTAL_FOUND 条** 热门内容

📄 查看完整报告: \`$LOG_FILE\`"
else
    MESSAGE="🔍 **监控报告** ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

⚠️ 本次监控未发现新内容

可能原因:
• 数据源限流
• 网络连接问题
• 需要配置搜索API

📄 日志: \`$LOG_FILE\`"
fi

export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin/openclaw message send \
    --target "user:$FEISHU_USER" \
    --message "$MESSAGE" \
    --channel feishu 2>/dev/null || echo "⚠️ 推送失败" >> "$LOG_FILE"

# 输出
jq -n \
    --arg date "$DATE" \
    --arg found "$TOTAL_FOUND" \
    --arg log "$LOG_FILE" \
    '{date: $date, found: $found, log_file: $log}'
