#!/bin/bash
# 部署自建 RSSHub 服务

echo "🚀 部署 RSSHub 自建服务"
echo "========================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 需要先安装 Docker"
    echo "安装命令: brew install docker"
    exit 1
fi

echo "📦 启动 RSSHub 容器..."
docker run -d --name rsshub \
  -p 1200:1200 \
  -e HTTP_PROXY=http://host.docker.internal:17890 \
  -e HTTPS_PROXY=http://host.docker.internal:17890 \
  diygod/rsshub:latest

echo ""
echo "✅ RSSHub 已启动"
echo ""
echo "访问地址: http://localhost:1200"
echo ""
echo "测试 YouTube RSS:"
echo "  http://localhost:1200/youtube/trending"
echo ""
echo "测试 Twitter RSS:"
echo "  http://localhost:1200/twitter/user/elonmusk"
echo ""
echo "📋 常用路由:"
echo "  - YouTube 热门: /youtube/trending"
echo "  - YouTube 频道: /youtube/channel/频道ID"
echo "  - Twitter 用户: /twitter/user/用户名"
echo "  - Twitter 列表: /twitter/list/列表ID"
echo "  - B站 热门: /bilibili/popular"
echo "  - B站 UP主: /bilibili/user/UID"
echo "  - 微博 热门: /weibo/search/hot"
echo "  - 知乎 热榜: /zhihu/hotlist"
echo ""
echo "⚠️ 注意:"
echo "  - 首次启动需要下载镜像，约 1-2 分钟"
echo "  - 容器会自动使用宿主机代理（端口 17890）"
echo "  - 如果 RSSHub 也无法访问 Twitter，说明 Twitter 封锁严格"
echo ""
echo "🛑 停止服务: docker stop rsshub"
echo "🗑️  删除服务: docker rm rsshub"
