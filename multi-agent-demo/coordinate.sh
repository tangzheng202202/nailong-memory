#!/bin/bash
# 多 Agent 工作台协调脚本
# 演示如何并行使用多个 AI 工具

echo "🚀 多 Agent 工作台演示"
echo "========================"
echo ""

# 显示所有工作区
echo "📁 可用工作区:"
git worktree list | grep workspace | awk '{print "  • " $1}'
echo ""

# 显示每个 Agent 的任务
echo "🤖 Agent 任务分配:"
echo ""

echo "【Claude Agent】- 前端开发"
echo "  目录: ../workspace-claude"
echo "  任务: 写前端登录页面"
if [ -f ../workspace-claude/TASK.md ]; then
    echo "  状态: 📝 待开始"
fi
echo ""

echo "【Codex Agent】- 后端开发"  
echo "  目录: ../workspace-codex"
echo "  任务: 写后端登录 API"
if [ -f ../workspace-codex/TASK.md ]; then
    echo "  状态: 📝 待开始"
fi
echo ""

echo "【Gemini Agent】- 测试+文档"
echo "  目录: ../workspace-gemini"
echo "  任务: 写测试用例和文档"
if [ -f ../workspace-gemini/TASK.md ]; then
    echo "  状态: 📝 待开始"
fi
echo ""

echo "========================"
echo ""
echo "使用方法:"
echo ""
echo "1. 启动 Claude 开发前端:"
echo "   cd ../workspace-claude"
echo "   claude '根据 TASK.md 创建登录页面'"
echo ""
echo "2. 启动 Codex 开发后端:"
echo "   cd ../workspace-codex"
echo "   codex '根据 TASK.md 创建登录 API'"
echo ""
echo "3. 启动 Gemini 写测试:"
echo "   cd ../workspace-gemini"
echo "   gemini '根据 TASK.md 创建测试'"
echo ""
echo "4. 完成后合并到 main:"
echo "   git merge claude-branch"
echo "   git merge codex-branch"
echo "   git merge gemini-branch"
echo ""
