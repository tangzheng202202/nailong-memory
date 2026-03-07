#!/bin/bash
# 多模型路由配置验证脚本

echo "🧠 OpenClaw 多模型路由配置"
echo "=============================="
echo ""

# 检查 Ollama 服务
echo "📦 检查 Ollama 服务..."
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama 服务运行中"
    echo ""
    echo "本地模型列表:"
    ollama list | tail -n +2 | awk '{print "  • " $1 " (" $3 ")"}'
else
    echo "❌ Ollama 服务未运行"
    echo "   请运行: ollama serve"
    exit 1
fi

echo ""
echo "=============================="
echo ""

# 模型路由规则
echo "🎯 模型路由规则:"
echo ""
echo "  1. 代码任务 (写代码/编程/脚本/debug)"
echo "     → DeepSeek-R1 7B (本地)"
echo ""
echo "  2. 快速问答 (是什么/怎么/如何)"
echo "     → Gemma 3 4B (本地)"
echo ""
echo "  3. 复杂推理 (分析/研究/对比)"
echo "     → DeepSeek-R1 7B (本地)"
echo ""
echo "  4. 日常对话 (默认)"
echo "     → Kimi K2.5 (云端)"
echo ""
echo "=============================="
echo ""

# 测试本地模型
echo "🧪 测试本地模型..."
echo ""

echo "测试 Gemma 3 4B:"
curl -s http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "gemma3:4b", "prompt": "Hello", "stream": false}' \
  -o /dev/null && echo "  ✅ Gemma 3 4B 可用" || echo "  ❌ Gemma 3 4B 不可用"

echo ""
echo "测试 DeepSeek-R1 1.5B:"
curl -s http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:1.5b", "prompt": "Hello", "stream": false}' \
  -o /dev/null && echo "  ✅ DeepSeek-R1 1.5B 可用" || echo "  ❌ DeepSeek-R1 1.5B 不可用"

echo ""
echo "测试 DeepSeek-R1 7B:"
curl -s http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:7b", "prompt": "Hello", "stream": false}' \
  -o /dev/null && echo "  ✅ DeepSeek-R1 7B 可用" || echo "  ❌ DeepSeek-R1 7B 不可用"

echo ""
echo "=============================="
echo "✅ 配置完成!"
echo ""
echo "使用方式:"
echo "  • 直接对话 → 自动路由到合适模型"
echo "  • 指定模型 → /model gemma3:4b"
echo "  • 查看当前 → /status"
