#!/usr/bin/env python3
"""
数据分析模块
提供粉丝分析、文章数据分析、最佳发布时间推荐
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 路径配置
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "wechat_mp.db"


class Analytics:
    """数据分析类"""
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        DATA_DIR.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建分析结果缓存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT NOT NULL,
                analysis_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_follower_growth(self, days=30):
        """获取粉丝增长趋势"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 查询关注事件
        cursor.execute('''
            SELECT DATE(created_at) as date, event_type, COUNT(*) as count
            FROM subscribe_events
            WHERE created_at > ?
            GROUP BY DATE(created_at), event_type
            ORDER BY date
        ''', (since,))
        
        data = defaultdict(lambda: {"subscribe": 0, "unsubscribe": 0})
        for row in cursor.fetchall():
            date, event_type, count = row
            data[date][event_type] = count
        
        conn.close()
        
        # 转换为列表
        result = []
        for date in sorted(data.keys()):
            result.append({
                "date": date,
                "new_followers": data[date]["subscribe"],
                "unfollowers": data[date]["unsubscribe"],
                "net_growth": data[date]["subscribe"] - data[date]["unsubscribe"]
            })
        
        return result
    
    def get_follower_stats(self):
        """获取粉丝统计概览"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 总用户数
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # 今日新增
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT COUNT(*) FROM subscribe_events 
            WHERE event_type = 'subscribe' AND DATE(created_at) = ?
        ''', (today,))
        today_new = cursor.fetchone()[0]
        
        # 今日取关
        cursor.execute('''
            SELECT COUNT(*) FROM subscribe_events 
            WHERE event_type = 'unsubscribe' AND DATE(created_at) = ?
        ''', (today,))
        today_lost = cursor.fetchone()[0]
        
        # 最近7天趋势
        week_data = self.get_follower_growth(days=7)
        
        conn.close()
        
        return {
            "total_followers": total_users,
            "today_new": today_new,
            "today_lost": today_lost,
            "today_net": today_new - today_lost,
            "weekly_trend": week_data
        }
    
    def get_article_analytics(self, days=30):
        """获取文章数据分析"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 查询文章数据
        cursor.execute('''
            SELECT title, read_count, like_count, share_count, comment_count, publish_time
            FROM articles
            WHERE publish_time > ?
            ORDER BY read_count DESC
        ''', (since,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                "title": row[0],
                "read_count": row[1],
                "like_count": row[2],
                "share_count": row[3],
                "comment_count": row[4],
                "publish_time": row[5]
            })
        
        conn.close()
        
        if not articles:
            return {
                "total_articles": 0,
                "avg_reads": 0,
                "avg_likes": 0,
                "top_articles": [],
                "engagement_rate": 0
            }
        
        # 计算平均值
        total_reads = sum(a["read_count"] for a in articles)
        total_likes = sum(a["like_count"] for a in articles)
        total_shares = sum(a["share_count"] for a in articles)
        
        # 爆款文章 (阅读量 > 平均值的 2 倍)
        avg_reads = total_reads / len(articles)
        top_articles = [a for a in articles if a["read_count"] > avg_reads * 2]
        
        # 互动率 (点赞 + 分享) / 阅读
        engagement_rate = (total_likes + total_shares) / total_reads if total_reads > 0 else 0
        
        return {
            "total_articles": len(articles),
            "avg_reads": round(avg_reads, 2),
            "avg_likes": round(total_likes / len(articles), 2),
            "top_articles": top_articles[:5],
            "engagement_rate": round(engagement_rate * 100, 2)
        }
    
    def get_best_post_time(self):
        """分析最佳发布时间"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询历史文章的发布时间和阅读量
        cursor.execute('''
            SELECT publish_time, read_count
            FROM articles
            WHERE publish_time IS NOT NULL AND read_count > 0
        ''')
        
        hourly_data = defaultdict(lambda: {"total_reads": 0, "count": 0})
        
        for row in cursor.fetchall():
            publish_time = row[0]
            read_count = row[1]
            
            if publish_time:
                try:
                    dt = datetime.fromisoformat(publish_time)
                    hour = dt.hour
                    hourly_data[hour]["total_reads"] += read_count
                    hourly_data[hour]["count"] += 1
                except:
                    pass
        
        conn.close()
        
        # 计算每个时段的平均阅读量
        hourly_avg = []
        for hour in range(24):
            data = hourly_data[hour]
            avg = data["total_reads"] / data["count"] if data["count"] > 0 else 0
            hourly_avg.append({
                "hour": hour,
                "avg_reads": round(avg, 2),
                "article_count": data["count"]
            })
        
        # 排序找出最佳时段
        hourly_avg.sort(key=lambda x: x["avg_reads"], reverse=True)
        
        return {
            "best_hours": hourly_avg[:3],
            "all_hours": sorted(hourly_avg, key=lambda x: x["hour"]),
            "recommendation": self._generate_time_recommendation(hourly_avg[:3])
        }
    
    def _generate_time_recommendation(self, top_hours):
        """生成时间推荐文字"""
        if not top_hours or top_hours[0]["avg_reads"] == 0:
            return "暂无足够数据，建议尝试早上 8:00 或晚上 20:00 发布"
        
        hours = [h["hour"] for h in top_hours]
        time_strs = [f"{h}:00" for h in sorted(hours)]
        
        if len(time_strs) == 1:
            return f"建议在 {time_strs[0]} 发布文章"
        else:
            return f"建议在 {'、'.join(time_strs)} 这几个时段发布文章效果较好"
    
    def get_unfollow_analysis(self, days=30):
        """取关分析"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 取关时间分布
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM subscribe_events
            WHERE event_type = 'unsubscribe' AND created_at > ?
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (since,))
        
        unfollow_trend = [
            {"date": row[0], "count": row[1]}
            for row in cursor.fetchall()
        ]
        
        # 计算取关率
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN event_type = 'subscribe' THEN 1 ELSE 0 END) as subscribes,
                SUM(CASE WHEN event_type = 'unsubscribe' THEN 1 ELSE 0 END) as unsubscribes
            FROM subscribe_events
            WHERE created_at > ?
        ''', (since,))
        
        row = cursor.fetchone()
        subscribes = row[0] or 0
        unsubscribes = row[1] or 0
        
        conn.close()
        
        unfollow_rate = (unsubscribes / subscribes * 100) if subscribes > 0 else 0
        
        return {
            "total_unfollows": unsubscribes,
            "unfollow_rate": round(unfollow_rate, 2),
            "trend": unfollow_trend,
            "assessment": self._assess_unfollow_rate(unfollow_rate)
        }
    
    def _assess_unfollow_rate(self, rate):
        """评估取关率"""
        if rate < 2:
            return "优秀"
        elif rate < 5:
            return "良好"
        elif rate < 10:
            return "一般，需关注"
        else:
            return "较高，建议优化内容"
    
    def generate_report(self):
        """生成完整的数据报告"""
        return {
            "generated_at": datetime.now().isoformat(),
            "follower_stats": self.get_follower_stats(),
            "article_analytics": self.get_article_analytics(),
            "best_post_time": self.get_best_post_time(),
            "unfollow_analysis": self.get_unfollow_analysis()
        }


def main():
    """CLI 入口"""
    import sys
    
    analytics = Analytics()
    
    if len(sys.argv) < 2:
        print("用法: python analytics.py <command>")
        print("\n命令:")
        print("  followers               - 粉丝统计")
        print("  articles                - 文章分析")
        print("  best_time               - 最佳发布时间")
        print("  unfollow                - 取关分析")
        print("  report                  - 生成完整报告")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "followers":
        result = analytics.get_follower_stats()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "articles":
        result = analytics.get_article_analytics()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "best_time":
        result = analytics.get_best_post_time()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "unfollow":
        result = analytics.get_unfollow_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "report":
        result = analytics.generate_report()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
