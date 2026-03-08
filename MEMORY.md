# MEMORY.md - 长期记忆索引层

> 这是整理后的长期记忆索引。详细内容在各分层文件中。

---

## 用户信息

- **名称**: 待补充
- **称呼**: 待补充
- **时区**: Asia/Shanghai (GMT+8)
- **偏好**: 待补充

---

## 能力索引

### 已部署系统

| 系统 | 状态 | 文档位置 |
|------|------|----------|
| 多 Agent 协作 | 已部署 | `/workspace/agents/multi-agent-system.md` |
| 监控 v5 | 运行中 | `/workspace/scripts/monitor-v5.sh` |
| RSS 监控 | 运行中 | `/workspace/scripts/rss-monitor.sh` |
| 本地模型路由 | 已配置 | ollama + 4 个模型 |

### Agent 分工

| Agent | 职责 | 工作目录 |
|-------|------|----------|
| main | 调度中心 | `/agents/main/workspace/` |
| coder | 编程开发 | `/agents/coder/workspace/` |
| researcher | 搜索分析 | `/agents/researcher/workspace/` |
| monitor | 监控任务 | `/agents/monitor/workspace/` |
| creative | 创意文案 | `/agents/creative/workspace/` |

---

## 重要决策

### OpenClaw 多 Agent 协作系统
- **时间**: 2026-03-07
- **主机**: Mac mini (本地)
- **架构**: 单主机多 Agent 隔离会话

### 监控数据源策略
- **国内源**: V2EX、B站、掘金（无需代理）
- **国际源**: HN、GitHub（走代理）
- **RSS**: X(Twitter)、YouTube（RSSHub）
- **放弃**: Reddit（被限流）

---

## 项目状态

### 进行中
- [ ] 修复飞书 bindings 配置
- [ ] 研究 Cross-Claude MCP
- [ ] 部署 LLM Router

### 已完成
- [x] 配置 GitHub
- [x] 改进监控报告
- [x] 多 Agent 工作台
- [x] 本地模型路由

---

## 快速链接

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 行为宪法、工作规范 |
| `SOUL.md` | 性格定义、核心价值观 |
| `USER.md` | 用户信息、偏好 |
| `memory/projects.md` | 项目详情 |
| `memory/infra.md` | 基础设施配置 |
| `memory/lessons.md` | 经验教训 |

---

*这是索引层，保持精简。详细内容在各分层文件中。*

**最后更新**: 2026-03-08
