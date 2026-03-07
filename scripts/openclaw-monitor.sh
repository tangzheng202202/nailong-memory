#!/bin/bash
# 奶龙全网监控 - OpenClaw能力提升与赚钱玩法
# 每2小时执行一次

cd /Users/mac/.openclaw/workspace
DATE=$(date +%Y-%m-%d-%H%M)
LOG_FILE="memory/daily/monitor-${DATE}.log"
FEISHU_USER="ou_5eb1253df17d5f9135a4fc537e365203"

echo "🔍 OpenClaw 全网监控 - ${DATE}" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 搜索关键词列表 - 中英文混合，覆盖 OpenClaw、AI Agent、MCP、自动化、赚钱等
SEARCH_TERMS=(
    # OpenClaw 生态
    "OpenClaw"
    "OpenClaw skills"
    "OpenClaw automation"
    "clawhub"
    "OpenClaw tutorial"
    "OpenClaw 教程"
    "OpenClaw 技能"
    
    # AI Agent / MCP
    "AI Agent"
    "MCP server"
    "Model Context Protocol"
    "Claude MCP"
    "AI agent workflow"
    "AI智能体"
    "智能体教程"
    "AI代理"
    
    # 自动化/效率
    "automation tools"
    "workflow automation"
    "no code automation"
    "AI automation"
    "自动化工具"
    "自动化脚本"
    "效率工具"
    "RPA自动化"
    
    # 赚钱/副业/商业化
    "AI赚钱"
    "AI副业"
    "自动化赚钱"
    "AI变现"
    "AI被动收入"
    "passive income AI"
    "AI side hustle"
    "AI创业"
    
    # 教程/资源
    "AI tools tutorial"
    "LLM automation"
    "cursor AI tutorial"
    "windsurf tutorial"
    "AI编程"
    "AI开发"
    
    # 垂直场景
    "AI写代码"
    "AI做视频"
    "AI做内容"
    "AI客服"
    "AI销售"
    "AI营销"
    "AI电商"
)

# 随机选一个词搜索（避免每次都一样）
QUERY=${SEARCH_TERMS[$RANDOM % ${#SEARCH_TERMS[@]}]}

echo "🎯 本次搜索: $QUERY" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 用 DuckDuckGo 搜索（不需要API key）
RESULTS=$(curl -s "https://html.duckduckgo.com/html/?q=$QUERY" 2>/dev/null | \
    sed -n 's/.*class="result__a"[^>]*href="\([^"]*\)"[^>]*>\([^<]*\).*/\2 - \1/p' | \
    head -5)

if [ -n "$RESULTS" ]; then
    echo "$RESULTS" >> "$LOG_FILE"
    MESSAGE="🔍 **OpenClaw 监控报告** - ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

🎯 搜索词: \`$QUERY\`

📋 发现结果:
\`\`\`
$RESULTS
\`\`\`

📄 完整日志: \`$LOG_FILE\`"
else
    echo "(无新结果)" >> "$LOG_FILE"
    MESSAGE="🔍 **OpenClaw 监控报告** - ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}

🎯 搜索词: \`$QUERY\`

📋 发现结果: 无新内容

📄 日志: \`$LOG_FILE\`"
fi

echo "" >> "$LOG_FILE"
echo "✅ 监控完成: $(date +%H:%M)" >> "$LOG_FILE"

# 推送到飞书
export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin/openclaw message send --target "user:$FEISHU_USER" --message "$MESSAGE" --channel feishu 2>/dev/null || echo "⚠️ 推送失败" >> "$LOG_FILE"

# 输出给调用者
cat "$LOG_FILE"
