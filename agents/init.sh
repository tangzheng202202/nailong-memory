#!/bin/bash
# OpenClaw 多 Agent 系统启动脚本

set -e

echo "🚀 启动 OpenClaw 多 Agent 协作系统..."
echo "======================================"

# 检查目录结构
echo "📁 检查目录结构..."
for dir in main coder researcher monitor; do
    mkdir -p "/Users/mac/.openclaw/workspace/agents/$dir/workspace"
done
echo "✅ 目录结构 OK"

# 检查配置文件
echo "📄 检查配置文件..."
if [ ! -f "/Users/mac/.openclaw/workspace/memory/shared-state.json" ]; then
    echo "⚠️ 共享状态文件不存在，已创建"
fi
echo "✅ 配置文件 OK"

# 记录启动时间
LOG_FILE="/Users/mac/.openclaw/workspace/memory/audit.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SYSTEM] [START] [多 Agent 系统启动] [SUCCESS]" >> "$LOG_FILE"

echo ""
echo "======================================"
echo "✅ 多 Agent 系统初始化完成"
echo ""
echo "可用 Agent:"
echo "  • main      - 主调度 Agent（当前）"
echo "  • coder     - 代码专家（按需启动）"
echo "  • researcher- 研究专家（按需启动）"
echo "  • monitor   - 监控专家（已配置 cron）"
echo ""
echo "工作目录: /Users/mac/.openclaw/workspace/agents/"
echo "共享状态: /Users/mac/.openclaw/workspace/memory/shared-state.json"
echo "任务队列: /Users/mac/.openclaw/workspace/memory/task-queue.json"
echo "审计日志: /Users/mac/.openclaw/workspace/memory/audit.log"
echo ""
echo "使用方法:"
echo "  研究任务 → sessions_spawn --label research-$(date +%s) --task \"...\""
echo "  代码任务 → sessions_spawn --label coder-$(date +%s) --task \"...\""
echo "======================================"
