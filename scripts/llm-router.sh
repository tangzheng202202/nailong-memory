#!/bin/bash
# LLM Router - 智能模型选择脚本
# 用法: ./llm-router.sh "你的问题"

QUERY="$1"

# 简单规则路由
code_patterns="(代码|编程|code|debug|fix|函数|脚本|python|javascript|js|ts|go|rust|java|c\+\+|写.*程序)"
simple_patterns="^(hello|hi|你好|在吗|简单|快速|ok|好的|谢谢)"
analysis_patterns="(分析|总结|解释|详细|长文|报告|研究|深度)"

if echo "$QUERY" | grep -qiE "$code_patterns"; then
    echo "路由到: DeepSeek-7B-Local (代码任务)"
    # 使用本地 DeepSeek
    curl -s http://127.0.0.1:11434/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"deepseek-r1:7b\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$QUERY\"}]
        }" | jq -r '.choices[0].message.content'
        
elif echo "$QUERY" | grep -qiE "$simple_patterns"; then
    echo "路由到: Gemma-Local (简单任务)"
    # 使用本地 Gemma
    curl -s http://127.0.0.1:11434/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"gemma3:4b\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$QUERY\"}]
        }" | jq -r '.choices[0].message.content'
        
else
    echo "路由到: Kimi K2.5 (通用任务)"
    # 使用云端 Kimi (需要通过 OpenClaw 或 API)
    echo "请使用 OpenClaw 默认会话处理此请求"
fi
