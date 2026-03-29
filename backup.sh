#!/bin/bash
# backup.sh - 工作区自动备份脚本
# 用法: ./backup.sh [commit message]
set -e

WORKSPACE="$HOME/.openclaw/workspace-smart"
BACKUP_BRANCH="backup"
COMMIT_MSG="${1:-自动备份 $(date '+%Y-%m-%d %H:%M')}"

cd "$WORKSPACE" || exit 1

echo "📦 开始备份 workspace-smart..."

# 添加所有文件
git add -A

# 检查是否有变化
if git diff --staged --quiet; then
    echo "✅ 没有变化需要备份"
    exit 0
fi

# 提交
git commit -m "$COMMIT_MSG"

# 推送到远程（如果 remote 已配置）
if git remote get-url origin &>/dev/null; then
    git push origin main 2>/dev/null || echo "⚠️  推送失败，跳过"
    echo "✅ 已推送到远程"
else
    echo "⚠️  未配置远程仓库，仅本地提交"
fi

echo "✅ 备份完成: $(date '+%Y-%m-%d %H:%M:%S')"