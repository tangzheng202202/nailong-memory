# Infra - 基础设施配置

## 系统信息

- **主机**: Mac mini
- **OS**: macOS (Darwin 24.6.0 arm64)
- **Shell**: zsh
- **Node**: v22.22.0

## OpenClaw 配置

### 核心路径
```
~/.openclaw/
├── openclaw.json          # 主配置
├── agents/                # Agent 目录
│   ├── main/
│   ├── coder/
│   ├── researcher/
│   ├── monitor/
│   └── creative/
├── workspace/             # 工作区
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── USER.md
│   ├── MEMORY.md
│   └── memory/
└── extensions/feishu/     # 飞书插件
```

### 网关配置
- **端口**: 18789
- **模式**: local (loopback)
- **状态**: running

### 模型配置

| 模型 | 来源 | 用途 |
|------|------|------|
| Kimi K2.5 | Moonshot API | 默认对话 |
| DeepSeek-R1 7B | Ollama 本地 | 代码/推理 |
| Gemma 3 4B | Ollama 本地 | 快速问答 |
| DeepSeek-R1 1.5B | Ollama 本地 | 轻量任务 |

### Ollama 配置
- **端口**: 11434
- **模型路径**: `~/.ollama/models/`
- **API**: `http://127.0.0.1:11434/v1`

## 飞书配置

### Bot 信息
- **App ID**: cli_a92c417c1b38dced
- **连接模式**: websocket

### 已配置群组

| 群名 | Agent | 群 ID |
|------|-------|-------|
| 奶龙指挥部 | main | oc_8f0cc... |
| 代码工坊 | coder | oc_4c3ba... |
| 情报中心 | researcher | oc_b44cf... |
| 监控室 | monitor | oc_0ea52... |
| 创意工作室 | creative | oc_74c02... |

## 代理配置

### 闪电云 Clash
- **端口**: 17890
- **URL**: `http://127.0.0.1:17890`
- **用途**: 国际源访问（HN、GitHub）

## 定时任务

### Cron 任务

| 任务 | 频率 | 下次执行 |
|------|------|----------|
| 监控 v5 | 每 4 小时 | 04:45 |
| RSS 监控 | 每小时 | 01:00 |
| 每日待办提醒 | 每天 21:00 | 20:00 |
| 记忆备份 | 每天 9:00, 21:00 | 08:00 |

## 环境变量

```bash
# 代理
export http_proxy=http://127.0.0.1:17890
export https_proxy=http://127.0.0.1:17890

# OpenClaw
export PATH="/Users/mac/.local/share/fnm/node-versions/v22.22.0/installation/bin:$PATH"
```

## 常用命令

```bash
# 重启 Gateway
openclaw gateway restart

# 查看状态
openclaw status
openclaw doctor --fix

# Cron 管理
openclaw cron list
openclaw cron add ...
openclaw cron delete <id>

# Agent 管理
openclaw agents list
openclaw agents add <name>
```

---

**最后更新**: 2026-03-08
