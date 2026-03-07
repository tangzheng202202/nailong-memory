#!/bin/bash
# 奶龙全网监控 - 供 agent 调用

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

echo "🔍 OpenClaw 全网监控 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ========== GitHub 搜索 ==========
echo "📦 GitHub 搜索..." >> "$LOG_FILE"

GITHUB_QUERIES=(
    "OpenClaw"
    "MCP server"
    "AI agent automation"
    "claude mcp"
    "AI workflow automation"
)

GITHUB_QUERY=${GITHUB_QUERIES[$RANDOM % ${#GITHUB_QUERIES[@]}]}
GITHUB_RESULTS=""

if command -v gh &> /dev/null && timeout 5 gh auth status &>/dev/null; then
    RAW_RESULTS=$(timeout 15 gh search repos "$GITHUB_QUERY" --limit 5 --sort updated --json name,url,description,updatedAt 2>/dev/null)
    if [ -n "$RAW_RESULTS" ] && [ "$RAW_RESULTS" != "[]" ]; then
        GITHUB_RESULTS=$(echo "$RAW_RESULTS" | jq -r '.[] | "\(.name): \(.url)"' 2>/dev/null)
    fi
fi

if [ -n "$GITHUB_RESULTS" ]; then
    echo "✅ GitHub 结果 ($GITHUB_QUERY):" >> "$LOG_FILE"
    echo "$GITHUB_RESULTS" >> "$LOG_FILE"
else
    echo "⚠️ GitHub 无结果或需要登录" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== HackerNews 搜索 ==========
echo "📰 HackerNews 搜索..." >> "$LOG_FILE"

HN_QUERIES=(
    "AI agent"
    "automation"
    "OpenClaw"
    "MCP"
    "LLM workflow"
)

HN_QUERY=${HN_QUERIES[$RANDOM % ${#HN_QUERIES[@]}]}
HN_RESULTS=""

HN_JSON=$(curl -s --max-time 10 "https://hn.algolia.com/api/v1/search_by_date?query=$HN_QUERY&hitsPerPage=5&tags=story" 2>/dev/null)
if [ -n "$HN_JSON" ]; then
    HN_RESULTS=$(echo "$HN_JSON" | jq -r '.hits[] | "\(.title): https://news.ycombinator.com/item?id=\(.objectID)"' 2>/dev/null)
fi

if [ -n "$HN_RESULTS" ]; then
    echo "✅ HN 结果 ($HN_QUERY):" >> "$LOG_FILE"
    echo "$HN_RESULTS" >> "$LOG_FILE"
else
    echo "⚠️ HN 无结果" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== Reddit 搜索 ==========
echo "🗣️ Reddit 搜索..." >> "$LOG_FILE"

REDDIT_SUBS=(
    "selfhosted"
    "LocalLLaMA"
    "ClaudeAI"
    "ChatGPT"
    "MachineLearning"
)

REDDIT_SUB=${REDDIT_SUBS[$RANDOM % ${#REDDIT_SUBS[@]}]}
REDDIT_RESULTS=""

REDDIT_JSON=$(curl -s --max-time 15 "https://www.reddit.com/r/$REDDIT_SUB/new.json?limit=5" \
    -H "User-Agent: OpenClawBot/1.0" 2>/dev/null || echo "")

if [ -n "$REDDIT_JSON" ]; then
    REDDIT_RESULTS=$(echo "$REDDIT_JSON" | jq -r '.data.children[].data | "\(.title): https://reddit.com\(.permalink)"' 2>/dev/null | head -5)
fi

if [ -n "$REDDIT_RESULTS" ]; then
    echo "✅ Reddit r/$REDDIT_SUB:" >> "$LOG_FILE"
    echo "$REDDIT_RESULTS" >> "$LOG_FILE"
else
    echo "⚠️ Reddit 无结果或被限流" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 输出结果 ==========
echo "✅ 监控完成: $(date +%H:%M)" >> "$LOG_FILE"

# 输出 JSON 给调用者
jq -n \
    --arg date "$DATE" \
    --arg gh_query "$GITHUB_QUERY" \
    --arg gh_results "$GITHUB_RESULTS" \
    --arg hn_query "$HN_QUERY" \
    --arg hn_results "$HN_RESULTS" \
    --arg rd_sub "$REDDIT_SUB" \
    --arg rd_results "$REDDIT_RESULTS" \
    --arg log_file "$LOG_FILE" \
    '{
        date: $date,
        github: {query: $gh_query, results: $gh_results},
        hackernews: {query: $hn_query, results: $hn_results},
        reddit: {sub: $rd_sub, results: $rd_results},
        log_file: $log_file
    }' 2>/dev/null || echo '{"error": "json build failed"}'
