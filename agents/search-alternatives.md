# 免费搜索工具配置方案
# 用于替代 Brave API 的实时搜索

## 方案 1: SearXNG 公开实例（推荐）

SearXNG 是去中心化搜索聚合器，无需注册。

### 可用公开实例
- https://search.sapti.me
- https://search.bus-hit.me
- https://searx.be

### 配置脚本
```bash
#!/bin/bash
# searx-search.sh
QUERY="$1"
SEARX_URL="https://search.sapti.me"
curl -s "$SEARX_URL/search?q=$(echo $QUERY | sed 's/ /+/g')" \
  -H "User-Agent: Mozilla/5.0" | \
  grep -oE 'href="http[^"]*"' | grep -v '$SEARX_URL' | head -10
```

## 方案 2: RSS 订阅（最稳定）

订阅以下源获取音乐节信息：

### 微信公众号 RSS
- 草莓音乐节官方公众号
- 佛山本地宝
- 广东演出资讯

### 微博 RSS
- @摩登天空
- @草莓音乐节

### 配置方法
```bash
# 使用 rss-bridge 转换微博为 RSS
curl -s 'https://rsshub.app/weibo/user/用户ID'
```

## 方案 3: 聚合搜索配置

### 安装 SearXNG 本地实例（Docker）
```bash
docker run -d --name searxng \
  -p 8080:8080 \
  -v "$HOME/searxng:/etc/searxng" \
  searxng/searxng
```

### 配置 OpenClaw 调用
修改监控脚本，增加：
```bash
# 在 monitor-v4.sh 中添加搜索函数
search_web() {
    local query="$1"
    curl -s "http://127.0.0.1:8080/search?q=$query" ...
}
```

## 方案 4: 社交媒体监控

### 小红书搜索
- 关键词：#佛山草莓音乐节 #草莓音乐节攻略
- API: 需逆向或模拟登录

### 豆瓣同城
- 佛山 → 音乐 → 近期活动
- RSS: https://www.douban.com/location/.../events

## 推荐配置

当前环境建议：
1. **短期**: 手动搜索后提供给我
2. **中期**: 配置 SearXNG 公开实例
3. **长期**: 自建 SearXNG + RSS 聚合

## 当前限制

- DuckDuckGo: 有反爬保护，不稳定
- SearXNG 公开实例: 可能随时失效
- 社交媒体: 需要登录态或逆向

## 替代策略

对于实时性要求高的查询（如音乐节阵容）：
1. 你截图发我
2. 我基于图片做分析规划
3. 比搜索更快更准
