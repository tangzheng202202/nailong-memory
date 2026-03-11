#!/usr/bin/env python3
"""
微信公众号 API 封装
提供 access_token 管理、用户信息获取、文章数据获取等功能
"""

import json
import time
import hashlib
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# 配置文件路径
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "wechat_mp.db"

class WeChatAPI:
    """微信公众号 API 封装类"""
    
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path or CONFIG_PATH)
        self.appid = self.config.get("appid", "")
        self.appsecret = self.config.get("appsecret", "")
        self.token = self.config.get("token", "")
        self._access_token = None
        self._token_expires = 0
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
        """初始化数据库"""
        DATA_DIR.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建 access_token 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                openid TEXT PRIMARY KEY,
                nickname TEXT,
                sex INTEGER,
                city TEXT,
                province TEXT,
                country TEXT,
                headimgurl TEXT,
                subscribe_time INTEGER,
                subscribe_scene TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_id TEXT,
                title TEXT,
                author TEXT,
                digest TEXT,
                content TEXT,
                url TEXT,
                thumb_url TEXT,
                publish_time TIMESTAMP,
                read_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建粉丝统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follower_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total INTEGER DEFAULT 0,
                new_followers INTEGER DEFAULT 0,
                unfollowers INTEGER DEFAULT 0,
                stat_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_access_token(self, force_refresh=False):
        """获取 access_token"""
        # 检查内存缓存
        if not force_refresh and self._access_token and time.time() < self._token_expires:
            return self._access_token
        
        # 检查数据库缓存
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token, expires_at FROM access_tokens ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()
        
        if row and not force_refresh:
            token, expires_at = row
            if time.time() < expires_at - 300:  # 提前5分钟刷新
                self._access_token = token
                self._token_expires = expires_at
                return token
        
        # 请求新 token
        if not self.appid or not self.appsecret:
            raise ValueError("请先在 config.json 中配置 appid 和 appsecret")
        
        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        if "access_token" in data:
            self._access_token = data["access_token"]
            self._token_expires = time.time() + data.get("expires_in", 7200)
            
            # 保存到数据库
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO access_tokens (token, expires_at) VALUES (?, ?)",
                (self._access_token, int(self._token_expires))
            )
            conn.commit()
            conn.close()
            
            return self._access_token
        else:
            raise Exception(f"获取 access_token 失败: {data}")
    
    def get_user_info(self, openid):
        """获取用户信息"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/user/info"
        params = {
            "access_token": token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        if "openid" in data:
            # 保存到数据库
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (openid, nickname, sex, city, province, country, headimgurl, 
                 subscribe_time, subscribe_scene, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("openid"),
                data.get("nickname"),
                data.get("sex"),
                data.get("city"),
                data.get("province"),
                data.get("country"),
                data.get("headimgurl"),
                data.get("subscribe_time"),
                data.get("subscribe_scene"),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        
        return data
    
    def get_followers(self, next_openid=None):
        """获取粉丝列表"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/user/get"
        params = {
            "access_token": token
        }
        if next_openid:
            params["next_openid"] = next_openid
        
        resp = requests.get(url, params=params, timeout=30)
        return resp.json()
    
    def get_material_list(self, material_type="news", offset=0, count=20):
        """获取素材列表"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/material/batchget_material?access_token={token}"
        data = {
            "type": material_type,
            "offset": offset,
            "count": count
        }
        
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    
    def get_user_summary(self, begin_date, end_date):
        """获取用户增减数据"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/datacube/getusersummary?access_token={token}"
        data = {
            "begin_date": begin_date,
            "end_date": end_date
        }
        
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    
    def get_user_cumulate(self, begin_date, end_date):
        """获取累计用户数据"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/datacube/getusercumulate?access_token={token}"
        data = {
            "begin_date": begin_date,
            "end_date": end_date
        }
        
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    
    def get_article_summary(self, begin_date, end_date):
        """获取图文群发每日数据"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/datacube/getarticlesummary?access_token={token}"
        data = {
            "begin_date": begin_date,
            "end_date": end_date
        }
        
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    
    def get_article_total(self, begin_date, end_date):
        """获取图文群发总数据"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/datacube/getarticletotal?access_token={token}"
        data = {
            "begin_date": begin_date,
            "end_date": end_date
        }
        
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    
    def send_text_message(self, openid, content):
        """发送客服文本消息"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/message/custom/send?access_token={token}"
        data = {
            "touser": openid,
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    
    def verify_signature(self, signature, timestamp, nonce):
        """验证微信服务器签名"""
        tmp_list = [self.token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "".join(tmp_list)
        hashcode = hashlib.sha1(tmp_str.encode()).hexdigest()
        return hashcode == signature


def main():
    """CLI 入口"""
    import sys
    
    api = WeChatAPI()
    
    if len(sys.argv) < 2:
        print("用法: python api.py <command> [args]")
        print("\n命令:")
        print("  token                    - 获取 access_token")
        print("  user_info <openid>       - 获取用户信息")
        print("  followers                - 获取粉丝列表")
        print("  articles                 - 获取图文素材列表")
        print("  user_summary <begin> <end>  - 获取用户增减数据 (YYYY-MM-DD)")
        print("  article_summary <begin> <end> - 获取文章数据 (YYYY-MM-DD)")
        return
    
    cmd = sys.argv[1]
    
    try:
        if cmd == "token":
            token = api.get_access_token(force_refresh=True)
            print(f"access_token: {token}")
        
        elif cmd == "user_info":
            if len(sys.argv) < 3:
                print("请提供 openid")
                return
            result = api.get_user_info(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "followers":
            next_id = sys.argv[2] if len(sys.argv) > 2 else None
            result = api.get_followers(next_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "articles":
            result = api.get_material_list("news")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "user_summary":
            if len(sys.argv) < 4:
                print("请提供开始和结束日期 (YYYY-MM-DD)")
                return
            result = api.get_user_summary(sys.argv[2], sys.argv[3])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "article_summary":
            if len(sys.argv) < 4:
                print("请提供开始和结束日期 (YYYY-MM-DD)")
                return
            result = api.get_article_summary(sys.argv[2], sys.argv[3])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        else:
            print(f"未知命令: {cmd}")
    
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
