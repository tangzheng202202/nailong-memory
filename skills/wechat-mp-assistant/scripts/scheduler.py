#!/usr/bin/env python3
"""
定时任务模块
支持定时群发消息、定时发布文章
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

# 路径配置
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "wechat_mp.db"


class SchedulerManager:
    """定时任务管理器"""
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path or CONFIG_PATH)
        self.scheduler = BackgroundScheduler()
        self._init_db()
        self._load_scheduled_jobs()
    
    def _load_config(self, path):
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    def _init_db(self):
        """初始化数据库表"""
        DATA_DIR.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建定时任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                media_id TEXT,
                target_openids TEXT,
                cron_expression TEXT,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'pending',
                executed_at TIMESTAMP,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建群发记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mass_send_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id TEXT,
                msg_data_id TEXT,
                msg_type TEXT,
                content TEXT,
                status TEXT,
                total_count INTEGER,
                filter_count INTEGER,
                sent_count INTEGER,
                error_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_scheduled_jobs(self):
        """从数据库加载待执行的任务"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, job_type, scheduled_time, cron_expression FROM scheduled_jobs WHERE status = 'pending'"
        )
        jobs = cursor.fetchall()
        conn.close()
        
        for job_id, job_type, scheduled_time, cron_expr in jobs:
            if cron_expr:
                # 周期性任务
                self._schedule_cron_job(job_id, job_type, cron_expr)
            elif scheduled_time:
                # 一次性任务
                exec_time = datetime.fromisoformat(scheduled_time)
                if exec_time > datetime.now():
                    self._schedule_once_job(job_id, job_type, exec_time)
    
    def _schedule_once_job(self, job_id, job_type, exec_time):
        """调度一次性任务"""
        self.scheduler.add_job(
            self._execute_job,
            trigger=DateTrigger(run_date=exec_time),
            args=[job_id, job_type],
            id=f"job_{job_id}",
            replace_existing=True
        )
    
    def _schedule_cron_job(self, job_id, job_type, cron_expr):
        """调度周期性任务"""
        try:
            # 解析 cron 表达式 (分 时 日 月 周)
            parts = cron_expr.split()
            if len(parts) == 5:
                self.scheduler.add_job(
                    self._execute_job,
                    trigger=CronTrigger(
                        minute=parts[0],
                        hour=parts[1],
                        day=parts[2],
                        month=parts[3],
                        day_of_week=parts[4]
                    ),
                    args=[job_id, job_type],
                    id=f"job_{job_id}",
                    replace_existing=True
                )
        except Exception as e:
            print(f"调度任务失败: {e}")
    
    def _execute_job(self, job_id, job_type):
        """执行任务"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scheduled_jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        
        if not job:
            conn.close()
            return
        
        # 更新状态为执行中
        cursor.execute(
            "UPDATE scheduled_jobs SET status = 'running', executed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), job_id)
        )
        conn.commit()
        
        try:
            result = None
            if job_type == "mass_send":
                result = self._do_mass_send(job)
            elif job_type == "preview":
                result = self._do_preview(job)
            
            # 更新状态为完成
            cursor.execute(
                "UPDATE scheduled_jobs SET status = 'completed', result = ? WHERE id = ?",
                (json.dumps(result, ensure_ascii=False), job_id)
            )
        except Exception as e:
            cursor.execute(
                "UPDATE scheduled_jobs SET status = 'failed', result = ? WHERE id = ?",
                (str(e), job_id)
            )
        
        conn.commit()
        conn.close()
    
    def _do_mass_send(self, job):
        """执行群发"""
        # 这里调用微信 API 进行群发
        # 需要实现具体的群发逻辑
        # 参考: https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Batch_Sends_and_Originality_Checks.html
        
        # 简化示例
        return {
            "status": "success",
            "msg": "群发任务已提交",
            "job_id": job[0]
        }
    
    def _do_preview(self, job):
        """执行预览发送"""
        # 发送预览给指定用户
        return {
            "status": "success",
            "msg": "预览已发送",
            "job_id": job[0]
        }
    
    def add_scheduled_job(self, job_type, title=None, content=None, media_id=None,
                          target_openids=None, scheduled_time=None, cron_expression=None):
        """添加定时任务"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scheduled_jobs (job_type, title, content, media_id, target_openids, scheduled_time, cron_expression)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_type,
            title,
            content,
            media_id,
            json.dumps(target_openids) if target_openids else None,
            scheduled_time.isoformat() if scheduled_time else None,
            cron_expression
        ))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 调度任务
        if cron_expression:
            self._schedule_cron_job(job_id, job_type, cron_expression)
        elif scheduled_time:
            self._schedule_once_job(job_id, job_type, scheduled_time)
        
        return job_id
    
    def cancel_job(self, job_id):
        """取消定时任务"""
        # 从调度器中移除
        try:
            self.scheduler.remove_job(f"job_{job_id}")
        except:
            pass
        
        # 更新数据库状态
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scheduled_jobs SET status = 'cancelled' WHERE id = ? AND status = 'pending'",
            (job_id,)
        )
        conn.commit()
        conn.close()
        return True
    
    def list_jobs(self, status=None):
        """列出定时任务"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM scheduled_jobs WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            cursor.execute("SELECT * FROM scheduled_jobs ORDER BY created_at DESC")
        
        columns = [desc[0] for desc in cursor.description]
        jobs = []
        for row in cursor.fetchall():
            job = dict(zip(columns, row))
            jobs.append(job)
        
        conn.close()
        return jobs
    
    def start(self):
        """启动调度器"""
        self.scheduler.start()
        print("定时任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        print("定时任务调度器已停止")


def main():
    """CLI 入口"""
    import sys
    import time
    
    manager = SchedulerManager()
    
    if len(sys.argv) < 2:
        print("用法: python scheduler.py <command> [args]")
        print("\n命令:")
        print("  list [status]            - 列出定时任务")
        print("  add <type> <title> <time> - 添加定时任务")
        print("  cancel <job_id>          - 取消任务")
        print("  start                    - 启动调度器")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        jobs = manager.list_jobs(status)
        if jobs:
            print(f"{'ID':<5} {'类型':<12} {'标题':<20} {'计划时间':<20} {'状态'}")
            print("-" * 80)
            for job in jobs:
                scheduled = job.get('scheduled_time', 'N/A') or 'N/A'
                if scheduled != 'N/A':
                    scheduled = scheduled[:16]
                print(f"{job['id']:<5} {job['job_type']:<12} {job.get('title','')[:18]:<20} {scheduled:<20} {job['status']}")
        else:
            print("暂无定时任务")
    
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("请提供任务类型、标题和执行时间")
            print("示例: python scheduler.py add mass_send '测试群发' '2024-01-01 10:00:00'")
            return
        job_type = sys.argv[2]
        title = sys.argv[3]
        time_str = sys.argv[4]
        
        try:
            exec_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            job_id = manager.add_scheduled_job(job_type, title=title, scheduled_time=exec_time)
            print(f"已添加定时任务，ID: {job_id}")
        except ValueError:
            print("时间格式错误，请使用: YYYY-MM-DD HH:MM:SS")
    
    elif cmd == "cancel":
        if len(sys.argv) < 3:
            print("请提供任务 ID")
            return
        manager.cancel_job(int(sys.argv[2]))
        print("已取消任务")
    
    elif cmd == "start":
        manager.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
