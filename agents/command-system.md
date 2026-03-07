# Agent 指令系统配置
# 版本: 1.0
# 创建: 2026-03-07

## 可用指令

### /coder <任务描述>
启动代码 Agent，处理编程任务

**示例:**
- `/coder 写个 Python 爬虫，抓取 V2EX 热榜`
- `/coder 修复 monitor-v3.sh 的代理问题`
- `/coder 把这个脚本重构得更优雅`

**安全规则:**
- 危险命令（rm/chmod/dd）会先询问确认
- 所有改动走 git，可回滚

### /researcher <任务描述>
启动研究 Agent，处理搜索分析任务

**示例:**
- `/researcher 搜索最新的 MCP server 项目`
- `/researcher 分析 OpenClaw 的竞品`
- `/researcher 调研 AI Agent 商业模式`

**安全规则:**
- 网络请求走代理（17890）
- 不存储敏感数据到外部

### /monitor
查看监控 Agent 状态和最近报告

**示例:**
- `/monitor` - 查看最近监控结果
- `/monitor status` - 查看运行状态

### /status
查看所有 Agent 状态和系统健康

**示例:**
- `/status` - 所有 Agent 状态
- `/status coder` - 指定 Agent 状态

### /todo
查看和管理待办事项

**示例:**
- `/todo` - 列出今日待办
- `/todo add 配置 GitHub` - 添加待办
- `/todo done 1` - 标记完成

## 使用流程

1. **发送指令**
   你: `/coder 写个自动化脚本`

2. **主 Agent 识别**
   - 解析指令类型: coder
   - 提取任务: "写个自动化脚本"

3. **启动子 Agent**
   - 创建隔离会话
   - 传递任务上下文

4. **子 Agent 执行**
   - 直接与你对话
   - 实时反馈进度

5. **任务完成**
   - 子 Agent 提交结果
   - 主 Agent 汇总（如需要）

## 快捷指令（无需 / 前缀）

以下关键词自动触发对应 Agent：

| 关键词 | 触发 Agent | 示例 |
|--------|-----------|------|
"写代码" | coder | "帮我写个代码" |
"搜索" | researcher | "搜索一下 OpenClaw" |
"查资料" | researcher | "查一下 MCP 协议" |
"分析" | researcher | "分析这个数据" |
"修复" | coder | "修复这个 bug" |
"重构" | coder | "重构这段代码" |

## 多 Agent 协作

复杂任务自动拆分：

```
你: "研究 MCP 并写个示例"

主 Agent:
  ├─ 启动 researcher: "搜索 MCP 资料"
  ├─ researcher 完成后 → 结果写入共享区
  ├─ 启动 coder: "基于资料写示例"
  └─ coder 完成后 → 推送完整报告
```

## 中断和切换

- 随时发新指令切换 Agent
- 发 `/stop` 终止当前任务
- 发 `/main` 回到主 Agent

## 配置文件

- 指令定义: `/workspace/agents/commands.json`
- 快捷映射: `/workspace/agents/shortcuts.json`
