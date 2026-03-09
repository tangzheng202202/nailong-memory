#!/bin/bash
# 记忆自动备份脚本
# 用法: ./backup-memory.sh

BACKUP_DIR="$HOME/.openclaw/backups"
WORKSPACE="$HOME/.openclaw/workspace"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 打包关键记忆文件
tar czf "$BACKUP_DIR/memory-backup-$DATE.tar.gz" \
    -C "$WORKSPACE" \
    AGENTS.md \
    SOUL.md \
    USER.md \
    MEMORY.md \
    memory/ \
    2>/dev/null

# 保留最近 10 个备份
ls -t "$BACKUP_DIR"/memory-backup-*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

echo "备份完成: $BACKUP_DIR/memory-backup-$DATE.tar.gz"
echo "备份列表:"
ls -lh "$BACKUP_DIR"/memory-backup-*.tar.gz 2>/dev/null | tail -5
