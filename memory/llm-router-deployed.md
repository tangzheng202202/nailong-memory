# LLM Router 部署总结

## 现状
OpenClaw 原生不支持自动路由，但已配置好模型别名：
- `Gemma-Local` - 轻量快速
- `DeepSeek-7B-Local` - 代码/推理
- `DeepSeek-1.5B-Local` - 极简任务
- `GLM-4-Flash` - 免费云端
- `Kimi-K2.5` - 默认主力

## 使用方式

### 1. 手动切换模型
在对话中使用模型别名：
```
/model DeepSeek-7B-Local
写个 Python 脚本...
```

### 2. 通过不同 Agent 路由
已配置多个 Agent，每个用不同模型：
- `main` → Kimi K2.5 (默认)
- `coder` → DeepSeek-7B-Local (代码专用)

### 3. 脚本路由 (已部署)
```bash
~/workspace/scripts/llm-router.sh "你的问题"
```

## 成本优化建议

| 场景 | 推荐模型 | 成本 |
|-----|---------|------|
| 日常对话 | Gemma-Local | 免费 |
| 代码编写 | DeepSeek-7B-Local | 免费 |
| 复杂分析 | GLM-4-Flash | 免费 |
| 长文本/多模态 | Kimi K2.5 | 按需 |

## 下一步优化
- [ ] 开发 MCP Router Server
- [ ] 实现自动任务分类
- [ ] 添加成本统计
