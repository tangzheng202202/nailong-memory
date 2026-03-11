#!/bin/bash
# OpenClaw 快速修复脚本
# 使用 EvoMap Capsules 修复常见问题

set -e

EVOLVER_DIR="$HOME/.openclaw/workspace/skills/evolver"
LOG_FILE="$HOME/.openclaw/logs/evolver-repair.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查 EvoMap 是否安装
check_evolver() {
    if [ ! -d "$EVOLVER_DIR" ]; then
        log "❌ EvoMap evolver 未安装"
        exit 1
    fi
    
    if [ ! -f "$EVOLVER_DIR/assets/gep/capsules.json" ]; then
        log "❌ Capsules 配置不存在"
        exit 1
    fi
    
    log "✅ EvoMap 检查通过"
}

# 修复网关
repair_gateway() {
    log "🔧 尝试修复 OpenClaw Gateway..."
    
    # 停止网关
    openclaw gateway stop 2>/dev/null || true
    sleep 2
    
    # 清理残留进程
    pkill -f 'openclaw.*gateway' 2>/dev/null || true
    sleep 1
    
    # 启动网关
    if openclaw gateway start; then
        log "✅ Gateway 启动成功"
        sleep 2
        
        # 验证
        if openclaw gateway status | grep -qi 'running\|active'; then
            log "✅ Gateway 运行正常"
            return 0
        else
            log "⚠️ Gateway 状态异常"
            return 1
        fi
    else
        log "❌ Gateway 启动失败"
        return 1
    fi
}

# 修复配置
repair_config() {
    log "🔧 检查 OpenClaw 配置..."
    
    CONFIG_FILE="$HOME/.openclaw/config.json"
    BACKUP_FILE="$CONFIG_FILE.backup"
    
    # 备份当前配置
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "$BACKUP_FILE"
        log "📦 配置已备份"
        
        # 验证 JSON
        if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
            log "✅ 配置格式正确"
            return 0
        else
            log "⚠️ 配置格式错误，尝试恢复备份..."
            if [ -f "$BACKUP_FILE" ]; then
                cp "$BACKUP_FILE" "$CONFIG_FILE"
                log "✅ 配置已恢复"
            fi
        fi
    else
        log "⚠️ 配置文件不存在"
    fi
}

# 修复 Skills
repair_skills() {
    log "🔧 检查 OpenClaw Skills..."
    
    SKILLS_DIR="$HOME/.openclaw/workspace/skills"
    
    if [ -d "$SKILLS_DIR" ]; then
        skill_count=$(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l)
        log "📦 发现 $skill_count 个 Skills"
        
        # 检查关键 Skills
        for skill in cli-anything evolver system-monitor; do
            if [ -d "$SKILLS_DIR/$skill" ]; then
                log "  ✅ $skill"
            else
                log "  ⚠️ $skill 缺失"
            fi
        done
    fi
}

# 清理日志
cleanup_logs() {
    log "🧹 清理过期日志..."
    
    LOGS_DIR="$HOME/.openclaw/logs"
    
    if [ -d "$LOGS_DIR" ]; then
        # 删除 7 天前的日志
        find "$LOGS_DIR" -name '*.log' -mtime +7 -delete 2>/dev/null || true
        find "$LOGS_DIR" -name '*.json' -mtime +7 -delete 2>/dev/null || true
        
        # 显示清理后大小
        size=$(du -sh "$LOGS_DIR" 2>/dev/null | cut -f1)
        log "📊 日志目录大小: $size"
    fi
}

# 主函数
main() {
    log "🚀 OpenClaw EvoMap 修复工具启动"
    
    check_evolver
    
    case "${1:-all}" in
        gateway)
            repair_gateway
            ;;
        config)
            repair_config
            ;;
        skills)
            repair_skills
            ;;
        cleanup)
            cleanup_logs
            ;;
        all)
            repair_gateway || true
            repair_config || true
            repair_skills || true
            cleanup_logs || true
            ;;
        *)
            echo "用法: $0 [gateway|config|skills|cleanup|all]"
            exit 1
            ;;
    esac
    
    log "✅ 修复完成"
}

main "$@"
