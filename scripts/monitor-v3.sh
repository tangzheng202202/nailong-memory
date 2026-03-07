#!/bin/bash
# 奶龙全网监控 v3 - 支持代理 + 国内源
# 数据源: GitHub(代理) + HackerNews(代理) + 国内源

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

# ========== 代理配置 ==========
# 闪电云 Clash mixed-port: 17890
PROXY_PORT="${PROXY_PORT:-17890}"
PROXY_URL="http://127.0.0.1:${PROXY_PORT}"

# 设置代理环境变量
export http_proxy="$PROXY_URL"
export https_proxy="$PROXY_URL"
export HTTP_PROXY="$PROXY_URL"
export HTTPS_PROXY="$PROXY_URL"
export ALL_PROXY="$PROXY_URL"

echo "🔍 OpenClaw 全网监控 v3 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "代理端口: $PROXY_PORT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ========== 国内源搜索 ==========
echo "🇨🇳 国内源搜索..." >> "$LOG_FILE"

# V2EX 最新话题
echo "📌 V2EX 技术节点..." >> "$LOG_FILE"
V2EX_RESULTS=""
V2EX_JSON=$(curl -s --max-time 15 "https://www.v2ex.com/api/topics/latest.json" 2>/dev/null)
if [ -n "$V2EX_JSON" ]; then
    # 筛选 AI/自动化相关
    V2EX_RESULTS=$(echo "$V2EX_JSON" | jq -r '.[] | select(.title | test("AI|agent|自动化|Claude|OpenAI|大模型|智能体"; "i")) | "\(.title): https://v2ex.com/t/\(.id)"' 2>/dev/null | head -5)
fi

if [ -n "$V2EX_RESULTS" ]; then
    echo "✅ V2EX 发现:" >> "$LOG_FILE"
    echo "$V2EX_RESULTS" >> "$LOG_FILE"
else
    echo "⚠️ V2EX 无匹配结果" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 知乎热榜（技术相关）
echo "📌 知乎热榜..." >> "$LOG_FILE"
ZH_RESULTS=""
ZH_JSON=$(curl -s --max-time 15 "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20" \
    -H "User-Agent: Mozilla/5.0" 2>/dev/null)
if [ -n "$ZH_JSON" ]; then
    ZH_RESULTS=$(echo "$ZH_JSON" | jq -r '.data[] | select(.target.title | test("AI|人工智能|Claude|ChatGPT|自动化|大模型|编程|开发"; "i")) | "\(.target.title): https://zhihu.com/question/\(.target.id)"' 2>/dev/null | head -5)
fi

if [ -n "$ZH_RESULTS" ]; then
    echo "✅ 知乎发现:" >> "$LOG_FILE"
    echo "$ZH_RESULTS" >> "$LOG_FILE"
else
    echo "⚠️ 知乎无匹配结果" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# ========== 代理访问国外源 ==========
echo "🌍 国外源搜索 (via 代理)..." >> "$LOG_FILE"

# GitHub 搜索
if command -v gh &> /dev/null; then
    echo "📦 GitHub 搜索..." >> "$LOG_FILE"
    
    GITHUB_QUERIES=(
        "OpenClaw"
        "MCP server"
        "AI agent automation"
        "claude mcp"
    )
    GITHUB_QUERY=${GITHUB_QUERIES[$RANDOM % ${#GITHUB_QUERIES[@]}]}
    GITHUB_RESULTS=""
    
    # gh 使用代理
    if timeout 10 gh auth status &>/dev/null; then
        RAW_RESULTS=$(timeout 20 gh search repos "$GITHUB_QUERY" --limit 5 --sort updated --json name,url,description,updatedAt 2>/dev/null)
        if [ -n "$RAW_RESULTS" ] && [ "$RAW_RESULTS" != "[]" ]; then
            GITHUB_RESULTS=$(echo "$RAW_RESULTS" | jq -r '.[] | "\(.name): \(.url)"' 2>/dev/null)
        fi
    fi
    
    if [ -n "$GITHUB_RESULTS" ]; then
        echo "✅ GitHub 结果 ($GITHUB_QUERY):" >> "$LOG_FILE"
        echo "$GITHUB_RESULTS" >> "$LOG_FILE"
    else
        echo "⚠️ GitHub 无结果或需登录: gh auth login" >> "$LOG_FILE"
    fi
else
    echo "⚠️ gh CLI 未安装" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# HackerNews
HN_QUERIES=(
    "AI agent"
    "automation"
    "OpenClaw"
    "MCP"
)
HN_QUERY=${HN_QUERIES[$RANDOM % ${#HN_QUERIES[@]}]}
HN_RESULTS=""

HN_JSON=$(curl -s --max-time 20 "https://hn.algolia.com/api/v1/search_by_date?query=$HN_QUERY&hitsPerPage=5&tags=story" 2>/dev/null)
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

# Reddit (代理访问)
REDDIT_SUBS=(
    "selfhosted"
    "LocalLLaMA"
    "ClaudeAI"
)
REDDIT_SUB=${REDDIT_SUBS[$RANDOM % ${#REDDIT_SUBS[@]}]}
REDDIT_RESULTS=""

REDDIT_JSON=$(curl -s --max-time 20 "https://www.reddit.com/r/$REDDIT_SUB/new.json?limit=5" \
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

echo "✅ 监控完成: $(date +%H:%M)" >> "$LOG_FILE"

# 输出 JSON
jq -n \
    --arg date "$DATE" \
    --arg proxy "$PROXY_PORT" \
    --arg v2ex "$V2EX_RESULTS" \
    --arg zhihu "$ZH_RESULTS" \
    --arg gh_query "$GITHUB_QUERY" \
    --arg gh_results "$GITHUB_RESULTS" \
    --arg hn_query "$HN_QUERY" \
    --arg hn_results "$HN_RESULTS" \
    --arg rd_sub "$REDDIT_SUB" \
    --arg rd_results "$REDDIT_RESULTS" \
    --arg log_file "$LOG_FILE" \
    '{
        date: $date,
        proxy: $proxy,
        v2ex: $v2ex,
        zhihu: $zhihu,
        github: {query: $gh_query, results: $gh_results},
        hackernews: {query: $hn_query, results: $hn_results},
        reddit: {sub: $rd_sub, results: $rd_results},
        log_file: $log_file
    }' 2>/dev/null || echo '{"error": "json build failed"}'
