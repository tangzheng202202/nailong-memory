#!/bin/bash
# ============================================================
# OpenClaw 每晚安全巡检脚本 v2.8
# 适用: OpenClaw 极简安全实践指南 v2.8
# 频率: 每天凌晨 3:00 (Asia/Shanghai)
# ============================================================
set -uo pipefail

OC="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
REPORT_DIR="$OC/security-reports"
NOW=$(date '+%Y-%m-%d %H:%M:%S')
REPORT="$REPORT_DIR/nightly-audit-$(date '+%Y%m%d').log"

mkdir -p "$REPORT_DIR"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$REPORT"
}

header() {
    echo "" | tee -a "$REPORT"
    echo "===== $1 =====" | tee -a "$REPORT"
}

# ── Canary 1: 配置完整性 ──────────────────────────────────
header "Canary 1: 配置完整性 (哈希基线校验)"
if [ -f "$OC/.config-baseline.sha256" ]; then
    SHA_ACTUAL=$(sha256sum "$OC/openclaw.json" | awk '{print $1}')
    SHA_BASE=$(awk '{print $1}' "$OC/.config-baseline.sha256")
    if [ "$SHA_ACTUAL" = "$SHA_BASE" ]; then
        log "✅ openclaw.json 基线匹配（无变更）"
    else
        log "🔴 警告: openclaw.json 与基线不匹配！疑似未授权修改"
        log "   基线: $SHA_BASE"
        log "   当前: $SHA_ACTUAL"
    fi
else
    log "⚠️  无基线文件，跳过校验"
fi

# ── Canary 2: 文件权限 ─────────────────────────────────────
header "Canary 2: 文件权限"
PERM=$(stat -f "%OLp" "$OC/openclaw.json" 2>/dev/null || stat -c "%a" "$OC/openclaw.json" 2>/dev/null)
if [ "$PERM" = "600" ] || [ "$PERM" = "600" ]; then
    log "✅ openclaw.json 权限正确 (600)"
else
    log "🔴 警告: openclaw.json 权限异常: $PERM"
fi

# ── Canary 3: 新增/修改文件检测 ─────────────────────────
header "Canary 3: 新增文件监控"
RECENT=$(find "$OC" -type f -not -path "*/.git/*" -not -path "*/node_modules/*" \
    -mtime -1 -newer "$OC/.config-baseline.sha256" 2>/dev/null)
if [ -n "$RECENT" ]; then
    COUNT=$(echo "$RECENT" | wc -l | tr -d ' ')
    log "⚠️  发现 $COUNT 个新增/修改文件（过去24小时）"
    echo "$RECENT" | while read f; do
        log "   - $f"
    done
else
    log "✅ 无新增文件"
fi

# ── Canary 4: exec-approvals 检查 ─────────────────────────
header "Canary 4: exec 审批状态"
if [ -f "$OC/exec-approvals.json" ]; then
    PENDING=$(grep -c '"state":"pending"' "$OC/exec-approvals.json" 2>/dev/null || echo "0")
    log "待审批: $PENDING"
else
    log "⚠️  无审批文件"
fi

# ── Canary 5: 异常 cron 任务检测 ─────────────────────────
header "Canary 5: Cron 任务健康"
CRON_COUNT=$(openclaw cron list 2>/dev/null | grep -c "cron" || echo "0")
log "当前活跃 Cron: $CRON_COUNT 个"

# ── Canary 6: Skill 安全检查 ──────────────────────────────
header "Canary 6: Skill 安装审计"
SKILLS_DIR="$OC/skills"
if [ -d "$SKILLS_DIR" ]; then
    DANGEROUS=$(find "$SKILLS_DIR" -type f \( -name "*.sh" -o -name "*.py" \) \
        -exec grep -l "curl.*|.*bash\|eval.*\$\|base64.*-d\|exec.*(" {} \; 2>/dev/null)
    if [ -n "$DANGEROUS" ]; then
        log "⚠️  发现可疑脚本（含危险命令）:"
        echo "$DANGEROUS" | while read f; do
            log "   - $f"
        done
    else
        log "✅ Skill 脚本安全（未发现危险模式）"
    fi
fi

# ── Canary 7: Git 远程连接 ────────────────────────────────
header "Canary 7: Git 灾备状态"
cd "$OC/workspace-smart" 2>/dev/null || cd ~/.openclaw/workspace-smart 2>/dev/null
if git remote -v 2>/dev/null | grep -q "origin"; then
    log "✅ Git remote 已配置"
    git fetch origin 2>/dev/null && log "✅ Git 远端可达"
else
    log "⚠️  Git remote 未配置"
fi

# ── Canary 8: 安全警告项 ─────────────────────────────────
header "Canary 8: 核心安全指标"
log "exec security 模式: $(grep -o '"security":"[^"]*"' "$OC/openclaw.json" | head -1)"
log "dmPolicy: $(grep -o '"dmPolicy":"[^"]*"' "$OC/openclaw.json" | grep -v pair | head -1)"
log "groupPolicy: $(grep -o '"groupPolicy":"[^"]*"' "$OC/openclaw.json" | head -1)"

# ── 报告摘要 ─────────────────────────────────────────────
header "巡检摘要"
log "巡检时间: $NOW"
log "OpenClaw版本: $(openclaw --version 2>/dev/null | head -1)"
log "磁盘使用: $(df -h "$OC" 2>/dev/null | tail -1 | awk '{print $3}')"
log "状态: ✅ 巡检完成"

# 30天轮转
find "$REPORT_DIR" -name "nightly-audit-*.log" -mtime +30 -delete 2>/dev/null
log "旧报告清理完成（保留30天）"

echo ""
echo "========================================" | tee -a "$REPORT"
echo "  🦞 OpenClaw 夜间安全巡检 | $NOW" | tee -a "$REPORT"
echo "========================================" | tee -a "$REPORT"