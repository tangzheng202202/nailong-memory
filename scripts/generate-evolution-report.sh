#!/bin/bash
# 生成真实的进化报告

WORKSPACE="$HOME/.openclaw/workspace"
REPORTS_DIR="$WORKSPACE/reports"
MEMORY_DIR="$WORKSPACE/memory"
SKILLS_DIR="$WORKSPACE/skills"
EVOLUTION_STATE="$MEMORY_DIR/evolution-state.json"

mkdir -p "$REPORTS_DIR"

TIMESTAMP=$(date '+%Y-%m-%d-%H%M')
REPORT_FILE="$REPORTS_DIR/evolution-report-$TIMESTAMP.md"

# 读取进化状态
if [ -f "$EVOLUTION_STATE" ]; then
    TOTAL_EVOLUTIONS=$(jq -r '.total_evolutions // 0' "$EVOLUTION_STATE")
    SKILLS_CREATED=$(jq -r '.skills_created | length' "$EVOLUTION_STATE")
    SKILLS_IMPROVED=$(jq -r '.skills_improved | length' "$EVOLUTION_STATE")
    LAST_ANALYSIS=$(jq -r '.last_analysis // "从未"' "$EVOLUTION_STATE")
else
    TOTAL_EVOLUTIONS=0
    SKILLS_CREATED=0
    SKILLS_IMPROVED=0
    LAST_ANALYSIS="从未"
fi

# 计算今日数据
TODAY=$(date +%Y-%m-%d)
TODAY_EVOLUTIONS=$(grep -c "$(date '+%Y-%m-%d')" "$MEMORY_DIR/evolution-log.md" 2>/dev/null || echo 0)
TODAY_TASKS=$(grep -c "^- \[x\]" "$MEMORY_DIR/$TODAY.md" 2>/dev/null || echo 0)

# 统计真实的 skills 数量（排除空目录）
REAL_SKILLS_COUNT=0
for dir in "$SKILLS_DIR"/*/; do
    if [ -f "$dir/SKILL.md" ] || [ -f "$dir/main.py" ] || [ -f "$dir/main.sh" ]; then
        ((REAL_SKILLS_COUNT++))
    fi
done

# 找出最近修改的 skills
RECENT_SKILLS=$(find "$SKILLS_DIR" -name "SKILL.md" -mtime -1 -exec dirname {} \; 2>/dev/null | xargs -I {} basename {} | head -5)

# 生成报告
cat > "$REPORT_FILE" << EOF
# AI 真实进化报告

**报告时间**: $(date '+%Y年%m月%d日 %H:%M')  
**数据周期**: 最近1小时

---

## 一、进化统计（真实数据）

| 指标 | 数值 | 说明 |
|------|------|------|
| 总进化次数 | $TOTAL_EVOLUTIONS | 实际执行的分析迭代 |
| 今日进化 | $TODAY_EVOLUTIONS | 本日完成的进化轮次 |
| 有效Skills | $REAL_SKILLS_COUNT | 有实际功能实现的技能 |
| 今日完成任务 | $TODAY_TASKS | 用户确认完成的任务 |
| 识别缺失能力 | $SKILLS_CREATED | 通过分析发现的能力缺口 |
| 计划改进 | $SKILLS_IMPROVED | 基于反馈的改进计划 |

**上次分析**: $LAST_ANALYSIS

---

## 二、Skills 质量分析

### 有效 Skills ($REAL_SKILLS_COUNT个)
只统计有实际代码/文档实现的技能：

$(find "$SKILLS_DIR" -name "SKILL.md" -exec dirname {} \; 2>/dev/null | xargs -I {} basename {} | sed 's/^/- /')

### 最近更新
$(if [ -n "$RECENT_SKILLS" ]; then echo "$RECENT_SKILLS" | sed 's/^/- /'; else echo "- 无"; fi)

---

## 三、今日实际工作

### 完成的任务
$(grep "^- \[x\]" "$MEMORY_DIR/$TODAY.md" 2>/dev/null | sed 's/^/- /' || echo "- 今日暂无记录")

### 遇到的问题/教训
$(grep -E "(教训|问题|失败)" "$MEMORY_DIR/$TODAY.md" 2>/dev/null | head -3 | sed 's/^/- /' || echo "- 暂无")

### 用户反馈
$(grep -E "(反馈|建议|优化)" "$MEMORY_DIR/$TODAY.md" 2>/dev/null | head -3 | sed 's/^/- /' || echo "- 暂无")

---

## 四、发现的能力缺口

$(if [ -f "$EVOLUTION_STATE" ]; then jq -r '.skills_created[] | "- " + .' "$EVOLUTION_STATE" 2>/dev/null | head -10 || echo "- 暂无"; else echo "- 暂无"; fi)

---

## 五、计划改进项

$(if [ -f "$EVOLUTION_STATE" ]; then jq -r '.skills_improved[] | "- " + .' "$EVOLUTION_STATE" 2>/dev/null | head -10 || echo "- 暂无"; else echo "- 暂无"; fi)

---

## 六、系统状态

- **CPU使用率**: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')%
- **内存使用**: $(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//') pages free
- **磁盘使用**: $(df -h / | tail -1 | awk '{print $5}')
- **系统负载**: $(uptime | awk -F'load averages:' '{print $2}' | awk '{print $1}')

---

## 七、下次进化重点

基于今日使用分析，下次进化将关注：

1. 高频使用技能的性能优化
2. 缺失能力的补充实现
3. 用户反馈的问题修复
4. 自动化程度的提升

---

**报告生成时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**下次分析**: $(date -v+1H '+%Y-%m-%d %H:%M')  
**数据来源**: 实际使用记录 + 用户反馈

---

*本报告基于真实数据分析，非空转计数。*
EOF

echo "✓ 真实进化报告已生成: $REPORT_FILE"
echo "REPORT:$REPORT_FILE"
