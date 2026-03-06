#!/bin/bash
# 奶龙每日记忆备份

cd /Users/mac/.openclaw/workspace

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet; then
    echo "$(date): 无变更，跳过备份"
    exit 0
fi

# 添加所有变更
git add -A

# 提交（带时间戳）
git commit -m "🧠 记忆备份 - $(date '+%Y-%m-%d %H:%M')" --quiet

echo "$(date): 备份完成 - $(git rev-parse --short HEAD)"
