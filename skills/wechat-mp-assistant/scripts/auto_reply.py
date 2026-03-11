#!/usr/bin/env python3
"""
自动回复处理模块
处理关键词回复、关注回复、默认回复
"""

import json
import re
import sqlite3
from pathlib import Path
from xml.etree import ElementTree as ET

# 路径配置
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "wechat_mp.db"


class AutoReplyHandler:
    """自动回复处理器"""
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path or CONFIG_PATH)
        self.auto_reply_config = self.config.get("auto_reply", {})
        self._init_db()
    
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
        
        # 创建关键词规则表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                reply TEXT NOT NULL,
                match_type TEXT DEFAULT 'contains',
                is_active INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建消息记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openid TEXT NOT NULL,
                msg_type TEXT,
                content TEXT,
                msg_id TEXT,
                create_time INTEGER,
                reply_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建关注记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribe_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openid TEXT NOT NULL,
                event_type TEXT,
                event_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 加载配置文件中的关键词规则到数据库
        self._sync_keyword_rules()
    
    def _sync_keyword_rules(self):
        """同步配置文件中的关键词规则到数据库"""
        rules = self.auto_reply_config.get("keyword_rules", [])
        if not rules:
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for rule in rules:
            keyword = rule.get("keyword", "")
            reply = rule.get("reply", "")
            
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM keyword_rules WHERE keyword = ?",
                (keyword,)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO keyword_rules (keyword, reply) VALUES (?, ?)",
                    (keyword, reply)
                )
        
        conn.commit()
        conn.close()
    
    def parse_message(self, xml_data):
        """解析微信推送的 XML 消息"""
        try:
            root = ET.fromstring(xml_data)
            msg = {}
            for child in root:
                msg[child.tag] = child.text
            return msg
        except Exception as e:
            print(f"解析消息失败: {e}")
            return None
    
    def handle_message(self, msg_data):
        """处理消息并返回回复"""
        msg_type = msg_data.get("MsgType")
        openid = msg_data.get("FromUserName")
        
        # 记录消息
        self._log_message(msg_data)
        
        if msg_type == "event":
            event = msg_data.get("Event")
            if event == "subscribe":
                return self._handle_subscribe(openid)
            elif event == "unsubscribe":
                return self._handle_unsubscribe(openid, msg_data)
        
        elif msg_type == "text":
            content = msg_data.get("Content", "")
            return self._handle_text_message(openid, content)
        
        # 默认回复
        return self._get_default_reply()
    
    def _handle_subscribe(self, openid):
        """处理关注事件"""
        # 记录关注事件
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subscribe_events (openid, event_type, event_time) VALUES (?, ?, ?)",
            (openid, "subscribe", int(time.time()))
        )
        conn.commit()
        conn.close()
        
        # 返回欢迎消息
        welcome_msg = self.auto_reply_config.get("welcome_message", "感谢关注！")
        return self._build_text_reply(openid, welcome_msg)
    
    def _handle_unsubscribe(self, openid, msg_data):
        """处理取消关注事件"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subscribe_events (openid, event_type, event_time) VALUES (?, ?, ?)",
            (openid, "unsubscribe", int(time.time()))
        )
        conn.commit()
        conn.close()
        return None
    
    def _handle_text_message(self, openid, content):
        """处理文本消息"""
        # 检查关键词匹配
        reply = self._match_keyword(content)
        if reply:
            return self._build_text_reply(openid, reply)
        
        # 返回默认回复
        default_reply = self._get_default_reply()
        return self._build_text_reply(openid, default_reply)
    
    def _match_keyword(self, content):
        """匹配关键词"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT keyword, reply, match_type FROM keyword_rules WHERE is_active = 1 ORDER BY priority DESC"
        )
        rules = cursor.fetchall()
        conn.close()
        
        for keyword, reply, match_type in rules:
            if match_type == "exact":
                if content.strip() == keyword:
                    return reply
            elif match_type == "regex":
                try:
                    if re.search(keyword, content):
                        return reply
                except re.error:
                    continue
            else:  # contains
                if keyword in content:
                    return reply
        
        return None
    
    def _get_default_reply(self):
        """获取默认回复"""
        return self.auto_reply_config.get("default_reply", "收到您的消息，我们会尽快回复。")
    
    def _build_text_reply(self, to_user, content):
        """构建文本回复 XML"""
        import time
        
        xml_template = """<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
        
        # 注意：from_user 应该是公众号的原始ID，这里简化处理
        from_user = "official_account"
        
        return xml_template.format(
            to_user=to_user,
            from_user=from_user,
            create_time=int(time.time()),
            content=content
        )
    
    def _log_message(self, msg_data):
        """记录消息到数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (openid, msg_type, content, msg_id, create_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            msg_data.get("FromUserName"),
            msg_data.get("MsgType"),
            msg_data.get("Content"),
            msg_data.get("MsgId"),
            msg_data.get("CreateTime")
        ))
        conn.commit()
        conn.close()
    
    def add_keyword_rule(self, keyword, reply, match_type="contains", priority=0):
        """添加关键词规则"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO keyword_rules (keyword, reply, match_type, priority) VALUES (?, ?, ?, ?)",
            (keyword, reply, match_type, priority)
        )
        conn.commit()
        conn.close()
        return True
    
    def remove_keyword_rule(self, rule_id):
        """删除关键词规则"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM keyword_rules WHERE id = ?", (rule_id,))
        conn.commit()
        conn.close()
        return True
    
    def list_keyword_rules(self):
        """列出所有关键词规则"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, keyword, reply, match_type, is_active, priority FROM keyword_rules ORDER BY priority DESC"
        )
        rules = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "keyword": r[1],
                "reply": r[2],
                "match_type": r[3],
                "is_active": r[4],
                "priority": r[5]
            }
            for r in rules
        ]
    
    def get_message_stats(self, days=7):
        """获取消息统计"""
        import datetime
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 总消息数
        cursor.execute("SELECT COUNT(*) FROM messages")
        total = cursor.fetchone()[0]
        
        # 最近 N 天消息数
        since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE created_at > ?",
            (since,)
        )
        recent = cursor.fetchone()[0]
        
        # 消息类型分布
        cursor.execute(
            "SELECT msg_type, COUNT(*) FROM messages GROUP BY msg_type"
        )
        type_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_messages": total,
            "recent_messages": recent,
            "type_distribution": type_dist
        }


def main():
    """CLI 入口"""
    import sys
    
    handler = AutoReplyHandler()
    
    if len(sys.argv) < 2:
        print("用法: python auto_reply.py <command> [args]")
        print("\n命令:")
        print("  list                     - 列出关键词规则")
        print("  add <keyword> <reply>    - 添加关键词规则")
        print("  remove <rule_id>         - 删除关键词规则")
        print("  stats                    - 查看消息统计")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        rules = handler.list_keyword_rules()
        if rules:
            print(f"{'ID':<5} {'优先级':<6} {'匹配类型':<10} {'关键词':<20} {'回复'}")
            print("-" * 80)
            for rule in rules:
                status = "✓" if rule["is_active"] else "✗"
                print(f"{rule['id']:<5} {rule['priority']:<6} {rule['match_type']:<10} {rule['keyword']:<20} {status}")
        else:
            print("暂无关键词规则")
    
    elif cmd == "add":
        if len(sys.argv) < 4:
            print("请提供关键词和回复内容")
            return
        keyword = sys.argv[2]
        reply = sys.argv[3]
        match_type = sys.argv[4] if len(sys.argv) > 4 else "contains"
        handler.add_keyword_rule(keyword, reply, match_type)
        print(f"已添加关键词规则: {keyword} -> {reply}")
    
    elif cmd == "remove":
        if len(sys.argv) < 3:
            print("请提供规则 ID")
            return
        handler.remove_keyword_rule(int(sys.argv[2]))
        print("已删除关键词规则")
    
    elif cmd == "stats":
        stats = handler.get_message_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    import time
    main()
