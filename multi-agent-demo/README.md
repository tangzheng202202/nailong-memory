# 多 Agent 工作台演示项目
# 任务：开发一个简单的 Web 应用

## 任务分配

### Agent 1: Claude (workspace-claude)
- **职责**: 前端界面设计 + 用户交互
- **工具**: Claude Code
- **目录**: /Users/mac/.openclaw/workspace-claude

### Agent 2: Codex (workspace-codex)  
- **职责**: 后端 API + 数据库
- **工具**: OpenAI Codex CLI
- **目录**: /Users/mac/.openclaw/workspace-codex

### Agent 3: Gemini (workspace-gemini)
- **职责**: 测试 + 文档
- **工具**: Gemini CLI
- **目录**: /Users/mac/.openclaw/workspace-gemini

## 协作流程

1. **主 Agent** 分配任务到各目录
2. **各 Agent** 在独立 worktree 中并行开发
3. **完成后** 合并到 main 分支

## 使用方法

```bash
# 进入 Claude 工作区
 cd ../workspace-claude
 claude "写前端登录页面"

# 进入 Codex 工作区  
 cd ../workspace-codex
 codex "写后端登录API"

# 进入 Gemini 工作区
 cd ../workspace-gemini
 gemini "写测试用例"
```
