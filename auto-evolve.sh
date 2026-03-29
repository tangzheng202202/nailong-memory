#!/bin/bash
# auto-evolve.sh - Workspace 每日自进化脚本

WORKSPACE="/Users/mac/.openclaw/workspace-smart"
DATE=$(date "+%Y-%m-%d")
YESTERDAY=$(date -v-1d "+%Y-%m-%d")

echo "===== Workspace 自进化分析 ====="
echo "日期: $DATE"
echo ""

echo "1. 读取昨日活动数据..."
echo "   - 检查 memory 目录"
if [ -f "$WORKSPACE/memory/$YESTERDAY.md" ]; then
    echo "   ✓ 昨日记忆: $YESTERDAY.md"
    cat "$WORKSPACE/memory/$YESTERDAY.md"
else
    echo "   ○ 昨日无记忆记录"
fi

echo ""
echo "2. 分析工作区状态..."
echo "   - 检查文件变更"
cd "$WORKSPACE"
FILE_COUNT=$(find . -maxdepth 1 -type f ! -name '.*' | wc -l)
echo "   - 顶层文件数: $FILE_COUNT"

echo ""
echo "3. 检查 MEMORY.md..."
cat "$WORKSPACE/MEMORY.md" 2>/dev/null || echo "   (空)"

echo ""
echo "4. 生成改进建议..."
echo "   - 检查 IDENTITY.md"
if grep -q "pick something" "$WORKSPACE/IDENTITY.md" 2>/dev/null; then
    echo "   ! 建议: 填充 IDENTITY.md 身份信息"
fi

echo ""
echo "5. 汇总报告..."
echo "   日期: $DATE"
echo "   工作区文件: $FILE_COUNT"
echo "   昨日记忆: $([ -f "$WORKSPACE/memory/$YESTERDAY.md" ] && echo '有' || echo '无')"

echo ""
echo "===== 分析完成 ====="