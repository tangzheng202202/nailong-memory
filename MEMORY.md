# MEMORY.md - 长期记忆

_这是整理后的长期记忆，记录重要信息、偏好和决策。_

## 用户信息

- **名称**: 待补充
- **称呼**: 待补充
- **时区**: Asia/Shanghai (GMT+8)
- **偏好**: 待补充

## 重要决策

_记录重要的选择和决定_

## 项目

### OpenClaw 多 Agent 协作系统
- **状态**: 已部署
- **时间**: 2026-03-07
- **主机**: Mac mini (本地)
- **架构**: 单主机多 Agent 隔离会话

**Agent 分工:**
1. **main** - 对话入口、任务调度、结果整合
2. **coder** - 编程、技术实现、Git 操作（危险命令需确认）
3. **researcher** - 网络搜索、数据分析（走代理）
4. **monitor** - 定时监控、通知推送（每2小时运行）

**安全策略:**
- 文件隔离: 各 Agent 独立工作目录
- 通信: 通过 `/workspace/memory/` 共享状态
- 审计: 所有敏感操作记录到 `audit.log`
- 代理: 网络请求统一走 17890 端口

**配置文件:**
- 系统文档: `/workspace/agents/multi-agent-system.md`
- 启动脚本: `/workspace/agents/init.sh`
- 共享状态: `/workspace/memory/shared-state.json`
- 任务队列: `/workspace/memory/task-queue.json`

## 偏好

_工作习惯、沟通风格等_

## 教训/经验

_从错误中学到的东西_

## 待办

_需要记住的长期事项_

---

*最后更新: 2026-03-07*
