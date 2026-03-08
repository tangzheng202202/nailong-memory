#!/bin/bash
# 奶龙全网监控 v5 - 国内源优先 + 国际源备选
# 数据源: 微博/知乎/B站/V2EX/掘金/HackerNews/GitHub

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# 代理配置（国外源使用）
PROXY_PORT="${PROXY_PORT:-17890}"
PROXY_URL="http://127.0.0.1:${PROXY_PORT}"
export http_proxy="$PROXY_URL"
export https_proxy="$PROXY_URL"

echo "🔍 OpenClaw 全网监控 v5 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "数据源: 国内优先" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

TOTAL_FOUND=0

# ========== 国内源（无需代理）==========

# 微博热搜
echo "🔥 微博热搜..." >> "$LOG_FILE"
WEIBO_HTML=$(curl -s --max-time 15 "https://s.weibo.com/top/summary" \
    -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" 2>/dev/null)
if [ -n "$WEIBO_HTML" ]; then
    WEIBO_RESULTS=$(echo "$WEIBO_HTML" | grep -oE 'class="td-02"[^>]*>[^<]+<a[^>]*href="[^"]*"[^>]*>[^<]+' | \
        head -10 | \
        sed 's/.*>\([^<]*\)<.*/\1/' | \
        nl -w2 -s'. ')
    if [ -n "$WEIBO_RESULTS" ]; then
        echo "✅ 微博热搜 TOP10:" >> "$LOG_FILE"
        echo "$WEIBO_RESULTS" >> "$LOG_FILE"
        COUNT=$(echo "$WEIBO_RESULTS" | wc -l | tr -d ' ')
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    else
        echo "⚠️ 微博热搜解析失败" >> "$LOG_FILE"
    fi
else
    echo "⚠️ 微博热搜获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 知乎热榜
echo "📖 知乎热榜..." >> "$LOG_FILE"
ZHIHU_JSON=$(curl -s --max-time 15 "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20" \
    -H "User-Agent: Mozilla/5.0" \
    -H "Referer: https://www.zhihu.com/" 2>/dev/null)
if [ -n "$ZHIHU_JSON" ]; then
    ZHIHU_RESULTS=$(echo "$ZHIHU_JSON" | jq -r '.data[0:10] | .[] | "\(.target.title) (\(.target.answer_count)回答)"' 2>/dev/null)
    if [ -n "$ZHIHU_RESULTS" ]; then
        echo "✅ 知乎热榜 TOP10:" >> "$LOG_FILE"
        echo "$ZHIHU_RESULTS" >> "$LOG_FILE"
        COUNT=$(echo "$ZHIHU_RESULTS" | wc -l | tr -d ' ')
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    else
        echo "⚠️ 知乎热榜解析失败" >> "$LOG_FILE"
    fi
else
    echo "⚠️ 知乎热榜获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# B站热门
echo "📺 B站热门..." >> "$LOG_FILE"
BILI_JSON=$(curl -s --max-time 15 "https://api.bilibili.com/x/web-interface/popular?ps=10" \
    -H "User-Agent: Mozilla/5.0" \
    -H "Referer: https://www.bilibili.com" 2>/dev/null)
if [ -n "$BILI_JSON" ]; then
    BILI_RESULTS=$(echo "$BILI_JSON" | jq -r '.data.list[0:10] | .[] | "\(.title) [\(.owner.name)] (\(.stat.view)播放)"' 2>/dev/null)
    if [ -n "$BILI_RESULTS" ]; then
        echo "✅ B站热门 TOP10:" >> "$LOG_FILE"
        echo "$BILI_RESULTS" >> "$LOG_FILE"
        COUNT=$(echo "$BILI_RESULTS" | wc -l | tr -d ' ')
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    else
        echo "⚠️ B站热门解析失败" >> "$LOG_FILE"
    fi
else
    echo "⚠️ B站热门获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# V2EX 热榜
echo "💬 V2EX 热榜..." >> "$LOG_FILE"
V2EX_JSON=$(curl -s --max-time 15 "https://www.v2ex.com/api/topics/hot.json" 2>/dev/null)
if [ -n "$V2EX_JSON" ]; then
    V2EX_RESULTS=$(echo "$V2EX_JSON" | jq -r '.[0:10] | .[] | "[\(.replies)回复] \(.title): https://v2ex.com/t/\(.id)"' 2>/dev/null)
    COUNT=$(echo "$V2EX_RESULTS" | grep -c "v2ex.com" || echo "0")
    if [ "$COUNT" -gt 0 ]; then
        echo "✅ V2EX 热榜 ($COUNT 条):" >> "$LOG_FILE"
        echo "$V2EX_RESULTS" >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    else
        echo "⚠️ V2EX 无数据" >> "$LOG_FILE"
    fi
else
    echo "⚠️ V2EX 获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 掘金热门
echo "📚 掘金热门..." >> "$LOG_FILE"
JUJIN_JSON=$(curl -s --max-time 15 "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed?aid=2608" \
    -H "User-Agent: Mozilla/5.0" 2>/dev/null)
if [ -n "$JUJIN_JSON" ]; then
    JUJIN_RESULTS=$(echo "$JUJIN_JSON" | jq -r '.data[0:8] | .[] | select(.item_info.article_info) | "[\(.item_info.article_info.view_count)阅读] \(.item_info.article_info.title)"' 2>/dev/null)
    COUNT=$(echo "$JUJIN_RESULTS" | wc -l | tr -d ' ')
    if [ "$COUNT" -gt 0 ]; then
        echo "✅ 掘金热门 ($COUNT 条):" >> "$LOG_FILE"
        echo "$JUJIN_RESULTS" >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    else
        echo "⚠️ 掘金无数据" >> "$LOG_FILE"
    fi
else
    echo "⚠️ 掘金获取失败" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 国际源（走代理）==========

echo "🌍 国际源（代理）..." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# HackerNews
echo "📰 HackerNews..." >> "$LOG_FILE"
HN_JSON=$(curl -s --max-time 20 "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null)
if [ -n "$HN_JSON" ]; then
    TOP_IDS=$(echo "$HN_JSON" | jq -r '.[0:5] | .[]' 2>/dev/null)
    HN_RESULTS=""
    for ID in $TOP_IDS; do
        ITEM=$(curl -s --max-time 10 "https://hacker-news.firebaseio.com/v0/item/$ID.json" 2>/dev/null)
        if [ -n "$ITEM" ]; then
            TITLE=$(echo "$ITEM" | jq -r '.title' 2>/dev/null)
            SCORE=$(echo "$ITEM" | jq -r '.score // 0' 2>/dev/null)
            HN_RESULTS="$HN_RESULTS
[$SCORE分] $TITLE"
        fi
    done
    COUNT=$(echo "$HN_RESULTS" | grep -c "\[" || echo "0")
    if [ "$COUNT" -gt 0 ]; then
        echo "✅ HN 热门 ($COUNT 条):" >> "$LOG_FILE"
        echo "$HN_RESULTS" >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    fi
else
    echo "⚠️ HN 获取失败（代理问题）" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# GitHub Trending
echo "🐙 GitHub Trending..." >> "$LOG_FILE"
# 使用代理访问
GITHUB_HTML=$(curl -s --max-time 20 "https://github.com/trending?since=daily" 2>/dev/null)
if [ -n "$GITHUB_HTML" ]; then
    GITHUB_REPOS=$(echo "$GITHUB_HTML" | grep -oE 'href="/[^/]+/[^"]+"' | grep -vE 'sponsors|trending' | head -10 | sed 's/href="//;s/"//' | sort -u | awk '{print "https://github.com" $1}')
    COUNT=$(echo "$GITHUB_REPOS" | wc -l | tr -d ' ')
    if [ "$COUNT" -gt 0 ]; then
        echo "✅ GitHub Trending ($COUNT 条):" >> "$LOG_FILE"
        echo "$GITHUB_REPOS" >> "$LOG_FILE"
        TOTAL_FOUND=$((TOTAL_FOUND + COUNT))
    fi
else
    echo "⚠️ GitHub 获取失败（代理问题）" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 总结 ==========
echo "======================================" >> "$LOG_FILE"
echo "✅ 监控完成: $(date +%H:%M)" >> "$LOG_FILE"
echo "总计发现: $TOTAL_FOUND 条内容" >> "$LOG_FILE"

# 推送到飞书
MESSAGE="🔍 **监控报告 v5** ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

📊 总计发现: **$TOTAL_FOUND 条** 热门内容

**国内源**: 微博/知乎/B站/V2EX/掘金
**国际源**: HN/GitHub (代理)

📄 完整报告: \`$LOG_FILE\`"

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
