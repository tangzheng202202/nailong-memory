# 公众号文章 HTML 处理工具

## 功能

1. **一键替换图片 URL** - 交互式或自动模式
2. **优化 HTML 格式** - 适应公众号编辑器
3. **生成内联样式** - 提高兼容性
4. **输出粘贴版本** - 直接复制到公众号

## 安装

脚本已保存到：
```
~/.openclaw/workspace/scripts/wechat_html_processor.py
```

## 使用方法

### 方法 1：交互式（推荐）
```bash
cd ~/.openclaw/workspace/memory
python3 ~/.openclaw/workspace/scripts/wechat_html_processor.py wechat-article-html.html
```

然后按提示输入图片 URL：
- 输入新的图片 URL 替换
- 直接回车跳过

### 方法 2：自动模式（跳过图片替换）
```bash
python3 ~/.openclaw/workspace/scripts/wechat_html_processor.py wechat-article-html.html --auto
```

## 输出文件

处理后生成两个文件：

| 文件 | 用途 |
|------|------|
| `wechat-article-html_optimized.html` | 完整 HTML，用浏览器打开后复制 |
| `wechat-article-html_paste.html` | 纯内容，直接复制粘贴到公众号 |

## 使用流程

### 第一步：准备图片
1. 登录公众号后台
2. 进入「素材库」→「图片」
3. 上传文章需要的所有图片
4. 获取每张图片的 URL（右键→复制链接）

### 第二步：运行脚本
```bash
python3 ~/.openclaw/workspace/scripts/wechat_html_processor.py wechat-article-html.html
```

按提示输入图片 URL：
```
[1/5] 当前图片: https://your-cdn.com/image1.png...
  请输入新URL (直接回车跳过): https://mmbiz.qpic.cn/xxx/xxx.jpg
  ✅ 已设置替换
```

### 第三步：复制到公众号

**方式 A：使用优化版 HTML**
1. 用浏览器打开 `wechat-article-html_optimized.html`
2. 全选（Cmd+A）→ 复制（Cmd+C）
3. 粘贴到公众号编辑器

**方式 B：使用粘贴版 HTML**
1. 打开 `wechat-article-html_paste.html`
2. 复制全部内容
3. 粘贴到公众号编辑器

### 第四步：调整优化
1. 检查图片是否正常显示
2. 调整代码块（建议截图替换）
3. 手机预览检查效果
4. 设置封面和摘要
5. 发表

## 优化内容

脚本会自动进行以下优化：

✅ **样式内联** - 提高公众号兼容性  
✅ **图片居中** - 自动添加居中样式  
✅ **引用美化** - 红色左边框样式  
✅ **提示框颜色** - 黄色/绿色提示框  
✅ **代码块标记** - 添加截图提示  
✅ **移除脚本** - 删除不支持的 JS  
✅ **简化结构** - 移除复杂 CSS

## 注意事项

1. **代码块处理** - 公众号代码块支持有限，建议：
   - 简单代码：保留，但可能格式丢失
   - 复杂代码：截图后插入图片

2. **图片大小** - 建议单张图片不超过 2MB

3. **预览检查** - 发表前务必手机预览

4. **样式微调** - 粘贴后可能需要在公众号编辑器微调

## 快捷命令

添加到 alias（可选）：
```bash
echo 'alias wxhtml="python3 ~/.openclaw/workspace/scripts/wechat_html_processor.py"' >> ~/.zshrc
source ~/.zshrc

# 之后使用
wxhtml wechat-article-html.html
```
