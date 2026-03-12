#!/bin/bash
# 真正的自我进化系统 - 基于实际使用和学习

WORKSPACE="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SKILLS_DIR="$WORKSPACE/skills"
LOGS_DIR="$WORKSPACE/logs"
EVOLUTION_STATE="$MEMORY_DIR/evolution-state.json"

mkdir -p "$LOGS_DIR"

echo "=== 真正的自我进化启动 ==="
echo "时间: $(date)"

# 初始化或读取进化状态
if [ ! -f "$EVOLUTION_STATE" ]; then
    cat > "$EVOLUTION_STATE" << 'EOF'
{
  "total_evolutions": 0,
  "skills_created": [],
  "skills_improved": [],
  "learnings": [],
  "last_analysis": "",
  "patterns": {
    "frequent_tasks": [],
    "failed_attempts": [],
    "user_corrections": []
  }
}
EOF
fi

# 1. 分析今日实际使用记录
echo ""
echo "=== 1. 分析今日使用记录 ==="
TODAY=$(date +%Y-%m-%d)
TODAY_LOG="$LOGS_DIR/usage-$TODAY.log"

# 从 memory 文件分析今天的互动
if [ -f "$MEMORY_DIR/$TODAY.md" ]; then
    echo "分析今日记忆文件..."
    
    # 提取今天完成的任务
    COMPLETED_TASKS=$(grep -E "^- \[x\]" "$MEMORY_DIR/$TODAY.md" 2>/dev/null | wc -l)
    echo "✓ 今日完成任务: $COMPLETED_TASKS"
    
    # 提取遇到的问题/教训
    LESSONS=$(grep -E "(教训|问题|失败|错误|bug)" "$MEMORY_DIR/$TODAY.md" 2>/dev/null)
    if [ -n "$LESSONS" ]; then
        echo "✓ 发现需要改进的点:"
        echo "$LESSONS" | head -5
    fi
    
    # 提取用户反馈
    FEEDBACK=$(grep -E "(反馈|建议|优化|改进)" "$MEMORY_DIR/$TODAY.md" 2>/dev/null)
    if [ -n "$FEEDBACK" ]; then
        echo "✓ 用户反馈:"
        echo "$FEEDBACK" | head -3
    fi
else
    echo "⚠ 今日无记忆记录"
fi

# 2. 检查 skills 实际使用情况
echo ""
echo "=== 2. 分析 Skills 使用情况 ==="

# 统计每个 skill 被调用的次数（通过检查日志）
echo "高频使用 Skills:"
for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    # 检查是否有使用记录
    usage_count=$(grep -r "$skill_name" "$LOGS_DIR" 2>/dev/null | wc -l)
    if [ "$usage_count" -gt 0 ]; then
        echo "  - $skill_name: 使用 $usage_count 次"
    fi
done

# 3. 发现缺失的能力
echo ""
echo "=== 3. 发现缺失能力 ==="

# 检查常用任务是否有对应 skill
MISSING_SKILLS=()

# 检查是否有 git 相关 skill
if [ ! -d "$SKILLS_DIR/git-assistant" ] && [ -d "$WORKSPACE/.git" ]; then
    MISSING_SKILLS+=("git-assistant:自动化git操作")
fi

# 检查是否有代码搜索 skill  
if [ ! -d "$SKILLS_DIR/code-search" ]; then
    MISSING_SKILLS+=("code-search:代码全文搜索")
fi

# 检查是否有 API 文档 skill
if [ ! -d "$SKILLS_DIR/api-docs" ]; then
    MISSING_SKILLS+=("api-docs:API文档查询")
fi

if [ ${#MISSING_SKILLS[@]} -gt 0 ]; then
    echo "发现缺失 Skills:"
    for missing in "${MISSING_SKILLS[@]}"; do
        echo "  - $missing"
    done
else
    echo "✓ 核心能力已覆盖"
fi

# 4. 基于实际使用创建改进计划
echo ""
echo "=== 4. 生成改进计划 ==="

IMPROVEMENTS=()

# 分析哪些 skill 需要改进
if [ -d "$SKILLS_DIR/system-monitor" ]; then
    # 检查 system-monitor 是否有飞书推送功能
    if ! grep -q "feishu" "$SKILLS_DIR/system-monitor/scripts/monitor.py" 2>/dev/null; then
        IMPROVEMENTS+=("system-monitor:添加飞书告警推送")
    fi
fi

if [ -d "$SKILLS_DIR/file-organizer" ]; then
    # 检查是否有智能分类功能
    if [ ! -f "$SKILLS_DIR/file-organizer/scripts/classify.py" ]; then
        IMPROVEMENTS+=("file-organizer:添加AI智能分类")
    fi
fi

if [ ${#IMPROVEMENTS[@]} -gt 0 ]; then
    echo "计划改进:"
    for imp in "${IMPROVEMENTS[@]}"; do
        echo "  - $imp"
    done
else
    echo "✓ 现有 Skills 功能完整"
fi

# 5. 记录真正的进化
echo ""
echo "=== 5. 记录进化 ==="

EVOLUTION_COUNT=$(jq '.total_evolutions' "$EVOLUTION_STATE")
NEW_COUNT=$((EVOLUTION_COUNT + 1))

# 更新进化状态
jq --arg date "$(date -Iseconds)" \
   --argjson count "$NEW_COUNT" \
   --arg tasks "$COMPLETED_TASKS" \
   --argjson missing "$(printf '%s\n' "${MISSING_SKILLS[@]}" | jq -R . | jq -s .)" \
   --argjson improvements "$(printf '%s\n' "${IMPROVEMENTS[@]}" | jq -R . | jq -s .)" \
   '.total_evolutions = $count |
    .last_analysis = $date |
    .patterns.frequent_tasks += [$tasks] |
    .skills_created += $missing |
    .skills_improved += $improvements' \
   "$EVOLUTION_STATE" > "$EVOLUTION_STATE.tmp" && mv "$EVOLUTION_STATE.tmp" "$EVOLUTION_STATE"

# 写入进化日志（真实内容）
cat >> "$MEMORY_DIR/evolution-log.md" << EOF

## $(date '+%Y-%m-%d %H:%M:%S') - 进化 #$NEW_COUNT

### 实际分析
- 今日完成任务: $COMPLETED_TASKS
- 发现问题: $(echo "$LESSONS" | wc -l)
- 用户反馈: $(echo "$FEEDBACK" | wc -l)

### 缺失能力
$(printf '%s\n' "${MISSING_SKILLS[@]}" | sed 's/^/- /')

### 改进计划
$(printf '%s\n' "${IMPROVEMENTS[@]}" | sed 's/^/- /')

### 状态
- 总进化次数: $NEW_COUNT
- 分析时间: $(date '+%H:%M:%S')
EOF

echo "✓ 进化 #$NEW_COUNT 已记录"
echo ""
echo "=== 进化完成 ==="
echo "下次进化将基于新的使用数据分析"
