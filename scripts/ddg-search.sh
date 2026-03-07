#!/bin/bash
# DuckDuckGo 搜索脚本 - 免 API key

QUERY="$1"
if [ -z "$QUERY" ]; then
    echo "用法: ./ddg-search.sh '搜索关键词'"
    exit 1
fi

# URL encode
ENCODED_QUERY=$(echo "$QUERY" | sed 's/ /+/g')

# 使用 DuckDuckGo HTML 版
curl -s "https://html.duckduckgo.com/html/?q=$ENCODED_QUERY" \
    -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    --max-time 15 2>/dev/null | \
    grep -oE 'class="result__a"[^>]*href="[^"]*"[^>]*>[^<]+' | \
    sed 's/.*href="//; s/">/ | /; s/<\/a>//' | \
    head -10
