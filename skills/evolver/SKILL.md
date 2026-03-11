---
name: evolver
description: EvoMap 自我进化引擎 - 用于 OpenClaw 基础运行与故障修复。基于 GEP (Genome Evolution Protocol) 协议，自动检测和修复 OpenClaw 启动错误、网关服务不稳定等问题。
---

# EvoMap OpenClaw 配置

基于 [EvoMap/evolver](https://github.com/EvoMap/evolver) 的 OpenClaw 专用配置。

## 功能

- **网关修复**: 自动检测和修复 OpenClaw 网关启动错误
- **配置修复**: 修复配置文件错误和加载问题
- **Skill 修复**: 修复 Skill 加载失败和运行时错误
- **稳定性加固**: 提升服务稳定性和可靠性
- **日志清理**: 自动清理过期日志文件

## Capsules（胶囊）

| Capsule ID | 名称 | 类别 | 用途 |
|------------|------|------|------|
| openclaw-gateway-repair | Gateway 修复 | repair | 修复网关启动错误 |
| openclaw-config-repair | 配置修复 | repair | 修复配置文件错误 |
| openclaw-skill-repair | Skill 修复 | repair | 修复 Skill 加载失败 |
| openclaw-stability-harden | 稳定性加固 | harden | 提升服务稳定性 |
| openclaw-log-cleanup | 日志清理 | maintenance | 清理过期日志 |

## Genes（基因）

| Gene ID | 名称 | 对应 Capsule | 操作 |
|---------|------|--------------|------|
| gateway-restart-gene | 网关重启修复 | openclaw-gateway-repair | 重启网关服务 |
| config-backup-restore-gene | 配置备份恢复 | openclaw-config-repair | 恢复配置备份 |
| skill-reload-gene | Skill 重新加载 | openclaw-skill-repair | 重新加载 Skills |
| memory-optimize-gene | 内存优化 | openclaw-stability-harden | 优化内存使用 |
| log-cleanup-gene | 日志清理 | openclaw-log-cleanup | 清理过期日志 |

## 使用

### 手动运行进化

```bash
cd ~/.openclaw/workspace/skills/evolver
node index.js
```

### 持续监控模式

```bash
cd ~/.openclaw/workspace/skills/evolver
node index.js --loop
```

### 使用 OpenClaw 配置

```bash
cd ~/.openclaw/workspace/skills/evolver
source .env.openclaw
node index.js
```

### 检查进化事件

```bash
cat ~/.openclaw/workspace/skills/evolver/assets/gep/events.jsonl
```

## 配置

配置文件: `.env.openclaw`

关键配置项：
- `EVOLVE_STRATEGY=repair-only` - 仅修复模式
- `A2A_NODE_ID=openclaw-main` - 节点标识
- `WORKER_ENABLED=0` - 禁用网络模式（本地运行）

## 信号检测

EvoMap 会自动检测以下信号：
- `gateway start failed` - 网关启动失败
- `config error` - 配置错误
- `skill load failed` - Skill 加载失败
- `service unstable` - 服务不稳定
- `disk full` - 磁盘已满

## 安全

- 所有修复操作都有验证步骤
- 支持回滚操作
- 保护关键文件不被修改
- 验证命令白名单限制

## 文件结构

```
evolver/
├── assets/gep/
│   ├── capsules.json    # Capsules 配置
│   ├── genes.json       # Genes 配置
│   └── events.jsonl     # 进化事件日志
├── .env.openclaw        # OpenClaw 专用配置
└── SKILL.md             # 本文件
```

## 依赖

- Node.js >= 18
- Git
- OpenClaw CLI

## 许可证

MIT
