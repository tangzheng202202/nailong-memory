#!/usr/bin/env python3
"""
系统监控脚本 - CPU/内存/磁盘告警
推送告警到飞书
"""

import psutil
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 告警阈值
THRESHOLDS = {
    "cpu_percent": 80,      # CPU 使用率 %
    "memory_percent": 85,   # 内存使用率 %
    "disk_percent": 90,     # 磁盘使用率 %
    "load_average": 10,     # 1分钟负载（按CPU核心数比例）
}

# 飞书推送配置
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

def get_system_stats():
    """获取系统状态"""
    stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        },
        "memory": psutil.virtual_memory()._asdict(),
        "disk": {},
        "load": os.getloadavg() if hasattr(os, 'getloadavg') else None,
    }
    
    # 磁盘信息
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            stats["disk"][partition.mountpoint] = {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }
        except:
            pass
    
    return stats

def check_alerts(stats):
    """检查是否触发告警"""
    alerts = []
    
    # CPU 告警
    if stats["cpu"]["percent"] > THRESHOLDS["cpu_percent"]:
        alerts.append({
            "level": "warning",
            "type": "CPU",
            "message": f"CPU 使用率过高: {stats['cpu']['percent']:.1f}%",
            "value": stats["cpu"]["percent"],
            "threshold": THRESHOLDS["cpu_percent"],
        })
    
    # 内存告警
    mem = stats["memory"]
    if mem["percent"] > THRESHOLDS["memory_percent"]:
        alerts.append({
            "level": "warning",
            "type": "内存",
            "message": f"内存使用率过高: {mem['percent']:.1f}%",
            "value": mem["percent"],
            "threshold": THRESHOLDS["memory_percent"],
        })
    
    # 磁盘告警
    for mount, disk in stats["disk"].items():
        if disk["percent"] > THRESHOLDS["disk_percent"]:
            alerts.append({
                "level": "critical",
                "type": "磁盘",
                "message": f"磁盘 [{mount}] 使用率过高: {disk['percent']:.1f}%",
                "value": disk["percent"],
                "threshold": THRESHOLDS["disk_percent"],
            })
    
    # 负载告警
    if stats["load"] and stats["cpu"]["count"] > 0:
        load_per_cpu = stats["load"][0] / stats["cpu"]["count"]
        if load_per_cpu > THRESHOLDS["load_average"] / 100:
            alerts.append({
                "level": "warning",
                "type": "负载",
                "message": f"系统负载过高: {stats['load'][0]:.2f}",
                "value": stats["load"][0],
                "threshold": THRESHOLDS["load_average"],
            })
    
    return alerts

def format_report(stats, alerts):
    """格式化报告"""
    lines = [
        f"📊 系统监控报告 - {stats['timestamp']}",
        "",
        f"💻 CPU: {stats['cpu']['percent']:.1f}% ({stats['cpu']['count']} 核)",
        f"🧠 内存: {stats['memory']['percent']:.1f}% "
        f"({stats['memory']['used'] / 1024**3:.1f}G / {stats['memory']['total'] / 1024**3:.1f}G)",
        "",
        "💾 磁盘使用:",
    ]
    
    for mount, disk in stats["disk"].items():
        lines.append(f"  {mount}: {disk['percent']:.1f}% "
                    f"({disk['used'] / 1024**3:.1f}G / {disk['total'] / 1024**3:.1f}G)")
    
    if stats["load"]:
        lines.append(f"")
        lines.append(f"⚡ 负载: {stats['load'][0]:.2f} {stats['load'][1]:.2f} {stats['load'][2]:.2f}")
    
    if alerts:
        lines.append("")
        lines.append("🚨 告警:")
        for alert in alerts:
            emoji = "🔴" if alert["level"] == "critical" else "🟡"
            lines.append(f"  {emoji} [{alert['type']}] {alert['message']}")
    else:
        lines.append("")
        lines.append("✅ 系统状态正常")
    
    return "\n".join(lines)

def save_report(report):
    """保存报告到文件"""
    log_dir = Path.home() / ".openclaw" / "logs" / "system-monitor"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    filename = datetime.now().strftime("%Y-%m-%d-%H%M%S") + ".log"
    filepath = log_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(report)
    
    return filepath

def main():
    """主函数"""
    # 获取系统状态
    stats = get_system_stats()
    
    # 检查告警
    alerts = check_alerts(stats)
    
    # 生成报告
    report = format_report(stats, alerts)
    
    # 输出报告
    print(report)
    
    # 保存报告
    filepath = save_report(report)
    print(f"\n📁 报告已保存: {filepath}")
    
    # 返回码：有告警返回1，正常返回0
    return 1 if alerts else 0

if __name__ == "__main__":
    sys.exit(main())
