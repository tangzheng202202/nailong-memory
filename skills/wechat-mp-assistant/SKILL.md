# 微信公众号助手

类似壹伴的公众号管理工具，提供数据采集、粉丝分析、自动回复、定时群发等功能。

## 功能特性

- 📊 **数据采集** - 文章阅读、点赞、分享、评论数据
- 👥 **粉丝分析** - 增长趋势、取关分析
- 💬 **自动回复** - 关键词回复、关注回复、默认回复
- ⏰ **定时群发** - 定时发布文章
- 📈 **数据分析** - 爆款文章分析、最佳发布时间推荐

## 安装

```bash
# 进入 skill 目录
cd ~/.openclaw/workspace/skills/wechat-mp-assistant

# 安装依赖
pip install -r requirements.txt

# 配置公众号信息
# 编辑 config.json，填入 appid 和 appsecret
```

## 配置说明

### 1. 申请微信公众号测试号

访问 https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login 申请测试号

获取：
- `appid` - 应用ID
- `appsecret` - 应用密钥

### 2. 配置服务器

在测试号管理页面配置：
- URL: `http://你的服务器/wechat/callback`
- Token: 自定义令牌（与 config.json 中一致）

### 3. 编辑配置文件

```json
{
  "appid": "你的appid",
  "appsecret": "你的appsecret",
  "token": "自定义token",
  "encoding_aes_key": ""
}
```

## 使用方法

### 启动 Web 服务

```bash
python scripts/web.py
```

访问 http://localhost:5000 查看管理界面

### CLI 命令

```bash
# 获取 access_token
python scripts/api.py token

# 获取用户信息
python scripts/api.py user_info openid

# 获取文章数据
python scripts/api.py articles

# 获取粉丝列表
python scripts/api.py followers
```

## 目录结构

```
wechat-mp-assistant/
├── SKILL.md              # 本文件
├── config.json           # 配置文件
├── requirements.txt      # Python 依赖
├── scripts/
│   ├── api.py           # 公众号 API 封装
│   ├── crawler.py       # 数据采集
│   ├── auto_reply.py    # 自动回复
│   ├── scheduler.py     # 定时任务
│   ├── analytics.py     # 数据分析
│   └── web.py           # Web 界面
├── data/
│   └── wechat_mp.db     # SQLite 数据库
└── templates/           # HTML 模板
```

## 技术说明

- 使用微信公众号官方 API
- SQLite 存储数据
- Flask 提供 Web 界面
- APScheduler 处理定时任务

## 注意事项

1. 测试号有接口调用频率限制
2. 正式号需要认证才能使用全部接口
3. 服务器需要 80/443 端口可被微信服务器访问
