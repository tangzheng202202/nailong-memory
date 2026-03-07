# OpenClaw 多 Agent 协作系统配置
# 创建时间: 2026-03-07
# 主机: Mac mini (本地)

## 架构概览

```
┌─────────────────────────────────────────┐
│           Mac mini (本地)                │
│  ┌─────────────────────────────────┐    │
│  │      OpenClaw Gateway           │    │
│  │  ┌─────────┐ ┌─────────┐       │    │
│  │  │ 主 Agent │ │代码Agent│       │    │
│  │  │ (调度)   │ │(coder)  │       │    │
│  │  └────┬────┘ └────┬────┘       │    │
│  │  ┌────┴───────────┴────┐       │    │
│  │  │   共享状态中心      │       │    │
│  │  │ /workspace/memory/  │       │    │
│  │  └────────────────────┘       │    │
│  │  ┌─────────┐ ┌─────────┐       │    │
│  │  │研究Agent│ │监控Agent│       │    │
│  │  │(research)│ │(monitor)│      │    │
│  │  └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Agent 分工

### 1. 主 Agent (main)
- **角色**: 对话入口、任务调度、结果整合
- **职责**: 
  - 接收用户指令
  - 分析任务类型，分派给子 Agent
  - 汇总子 Agent 结果，生成最终报告
  - 管理待办事项和提醒
- **安全级别**: 标准
- **文件权限**: 全 workspace 访问

### 2. 代码 Agent (coder)
- **角色**: 编程、技术实现、代码审查
- **职责**:
  - 写代码、脚本、配置文件
  - 代码重构和优化
  - 技术方案实现
  - Git 操作
- **安全级别**: 高
- **限制**: 
  - 执行命令前确认（rm/chmod 等危险操作）
  - 不涉及系统级修改
  - 所有代码改动记录到 git
- **启动命令**: `sessions_spawn --agentId coder --task "..."`

### 3. 研究 Agent (researcher)
- **角色**: 信息搜索、数据分析、资料收集
- **职责**:
  - 网络搜索（web_search/web_fetch）
  - 数据分析、报告生成
  - 竞品分析、市场调研
  - 文档阅读和摘要
- **安全级别**: 中
- **限制**:
  - 不访问本地敏感文件
  - 网络请求走代理
  - 不存储用户隐私数据到外部
- **启动命令**: `sessions_spawn --agentId researcher --task "..."`

### 4. 监控 Agent (monitor)
- **角色**: 定时任务、数据监控、通知推送
- **职责**:
  - 定时执行监控脚本
  - 检查系统状态
  - 推送重要通知
  - 维护日志和状态文件
- **安全级别**: 低
- **限制**:
  - 只读访问外部数据源
  - 推送目标固定（用户授权的渠道）
- **状态**: 已配置（cron 任务）

## 数据安全策略

### 1. 文件隔离
```
/workspace/
├── agents/
│   ├── main/          # 主 Agent 工作区
│   ├── coder/         # 代码 Agent 工作区
│   ├── researcher/    # 研究 Agent 工作区
│   └── monitor/       # 监控 Agent 工作区
├── memory/            # 共享状态（所有 Agent 可读）
│   ├── todo-daily.md  # 每日待办
│   ├── shared-state.json  # 共享状态
│   └── daily/         # 日志
└── secrets/           # 敏感配置（仅主 Agent 可写）
```

### 2. 通信协议
- Agent 间通过 `memory/shared-state.json` 通信
- 消息格式: `{from, to, task, status, result, timestamp}`
- 任务队列: `memory/task-queue.json`

### 3. 审计日志
- 所有敏感操作记录到 `memory/audit.log`
- 记录: 操作者、时间、操作类型、结果

### 4. 敏感操作确认
- 删除文件: 必须用户确认
- 网络请求: 走代理，记录域名
- 代码执行: 危险命令（rm/dd等）需确认

## 工作流示例

### 场景: "帮我研究 MCP 并写个示例"

```
用户 → 主 Agent
       │
       ├─► 研究 Agent: "搜索 MCP 相关资料"
       │   └─► 返回: 文档链接、关键概念
       │
       ├─► 代码 Agent: "基于研究结果写示例"
       │   └─► 返回: 代码文件
       │
       └─► 主 Agent 整合 → 推送报告给用户
```

## 配置文件

- 主配置: `/workspace/agents/config.json`
- 安全策略: `/workspace/agents/security.md`
- Agent 角色定义: `/workspace/agents/roles/`

## 启动命令

```bash
# 代码 Agent
openclaw sessions_spawn --agentId coder --mode session --label "coder-$(date +%s)"

# 研究 Agent
openclaw sessions_spawn --agentId researcher --mode session --label "research-$(date +%s)"
```

## 状态检查

```bash
# 查看所有 Agent 状态
openclaw subagents list

# 查看任务队列
cat /workspace/memory/task-queue.json
```

---
*配置完成时间: 待填写*
*版本: 1.0*
