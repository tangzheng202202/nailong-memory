#!/bin/bash

# 每日进化报告生成脚本

DATE=$(date +%Y年%m月%d日)
LEARNINGS_DIR="/Users/mac/.openclaw/skills/self-improving-agent/.learnings"

echo "📊 每日进化报告 - $DATE"
echo ""
echo "=== 错误修复 ==="
if [ -f "$LEARNINGS_DIR/ERRORS.md" ]; then
    ERRORS=$(wc -l < "$LEARNINGS_DIR/ERRORS.md" 2>/dev/null || echo "0")
    echo "已记录 $ERRORS 条错误"
else
    echo "暂无错误记录"
fi

echo ""
echo "=== 新知识 ==="
if [ -f "$LEARNINGS_DIR/LEARNINGS.md" ]; then
    KNOWLEDGE=$(wc -l < "$LEARNINGS_DIR/LEARNINGS.md" 2>/dev/null || echo "0")
    echo "已记录 $KNOWLEDGE 条学习"
else
    echo "暂无学习记录"
fi

echo ""
echo "=== 功能请求 ==="
if [ -f "$LEARNINGS_DIR/FEATURE_REQUESTS.md" ]; then
    FEATURES=$(wc -l < "$LEARNINGS_DIR/FEATURE_REQUESTS.md" 2>/dev/null || echo "0")
    echo "已记录 $FEATURES 条功能请求"
else
    echo "暂无功能请求"
fi

echo ""
echo "=== 技能更新 ==="
SKILLS=$(ls -d /Users/mac/.openclaw/skills/*/ 2>/dev/null | wc -l)
echo "当前加载 $SKILLS 个技能"

echo ""
echo "=== 模型使用统计 ==="
if [ -f "/Users/mac/.openclaw/agents/main/agent/auth-profiles.json" ]; then
    echo "活跃模型: moonshot/kimi-k2.5"
fi

echo ""
echo "=== 工作区文件 ==="
WORKSPACE_FILES=$(find /Users/mac/.openclaw/workspace -type f 2>/dev/null | wc -l)
echo "工作区文件数: $WORKSPACE_FILES"

echo ""
echo "---"
echo "报告生成时间: $(date +%H:%M:%S)"
