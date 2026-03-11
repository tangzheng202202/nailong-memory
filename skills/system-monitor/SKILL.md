---
name: system-monitor
description: 系统监控 - CPU/内存/磁盘实时监控与告警，支持飞书推送
---

# System Monitor

## 功能

- 实时监控 CPU、内存、磁盘使用率
- 可配置告警阈值
- 生成格式化监控报告
- 异常状态返回非零退出码（便于 cron 告警）

## 使用

```bash
# 运行监控检查
python3 ~/.openclaw/workspace/skills/system-monitor/scripts/monitor.py

# 设置定时监控（每30分钟）
openclaw cron add --name "系统监控" --schedule "*/30 * * * *" \
  --command "python3 ~/.openclaw/workspace/skills/system-monitor/scripts/monitor.py"
```

## 告警阈值

| 指标 | 阈值 | 级别 |
|------|------|------|
| CPU | 80% | warning |
| 内存 | 85% | warning |
| 磁盘 | 90% | critical |
| 负载 | 10/核 | warning |

## 输出示例

```
📊 系统监控报告 - 2026-03-10 20:30:00

💻 CPU: 45.2% (8 核)
🧠 内存: 62.5% (16.0G / 32.0G)

💾 磁盘使用:
  /: 72.3% (350.2G / 500.0G)
  /System/Volumes/Data: 68.1% (450.5G / 1.0T)

⚡ 负载: 2.15 2.08 1.95

✅ 系统状态正常
```
