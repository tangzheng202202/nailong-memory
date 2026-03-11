# price-monitor

购物比价监控工具 - 监控京东商品价格变化，降价时自动通知

## 功能特性

- 🔍 监控京东商品价格变化
- ➕ 支持添加/删除/列出监控商品
- ⏰ 定时检查价格（每4小时）
- 📢 降价时通过飞书通知
- 📊 记录价格历史

## 安装依赖

```bash
cd ~/.openclaw/workspace/skills/price-monitor
pip install playwright beautifulsoup4 lxml requests
playwright install chromium
```

## 使用方法

### 添加监控商品

```bash
python scripts/add_product.py --url "https://item.jd.com/12345678.html" --name "iPhone 15"
```

### 列出所有监控商品

```bash
python scripts/add_product.py --list
```

### 删除监控商品

```bash
python scripts/add_product.py --delete <product_id>
```

### 手动运行价格检查

```bash
python scripts/monitor.py
```

### 设置定时任务（每4小时检查一次）

```bash
# 添加到 crontab
crontab -e
# 添加以下行：
0 */4 * * * cd ~/.openclaw/workspace/skills/price-monitor && python scripts/monitor.py
```

## 数据库结构

- **products**: 商品信息表
  - id: 商品ID
  - name: 商品名称
  - url: 商品链接
  - current_price: 当前价格
  - lowest_price: 历史最低价
  - created_at: 创建时间
  - updated_at: 更新时间

- **price_history**: 价格历史表
  - id: 记录ID
  - product_id: 关联商品ID
  - price: 价格
  - recorded_at: 记录时间

## 飞书通知配置

在 `scripts/monitor.py` 中配置飞书 webhook URL：

```python
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

## 注意事项

1. 京东页面结构可能会变化，需要定期更新解析逻辑
2. 频繁请求可能会被限制，建议合理设置检查间隔
3. 部分商品可能需要登录才能获取价格
