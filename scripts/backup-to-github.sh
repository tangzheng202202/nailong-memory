#!/bin/bash
# 记忆自动备份到 GitHub
# 每天 9:00 和 21:00 自动执行

WORKSPACE="$HOME/.openclaw/workspace"
DATE=$(date '+%Y-%m-%d %H:%M')

# 进入工作目录
cd "$WORKSPACE" || exit 1

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet; then
    echo "[$DATE] 没有变更，跳过备份"
    exit 0
fi

# 添加所有变更
git add -A

# 提交
git commit -m "$DATE - 自动备份记忆" || exit 0

# 推送到 GitHub
git push origin main

if [ $? -eq 0 ]; then
    echo "[$DATE] 备份成功推送到 GitHub"
else
    echo "[$DATE] 备份推送失败"
fi
