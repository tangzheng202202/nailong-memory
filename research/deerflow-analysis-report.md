# DeerFlow 代码结构分析报告

## 1. 整体架构

### 1.1 架构图（文字描述）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Frontend (Next.js 16 + React 19 + Tailwind CSS 4)                 │   │
│  │  - Landing page, Chat interface, Settings                          │   │
│  │  - LangGraph SDK for streaming                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Reverse Proxy (Nginx:2026)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  /api/langgraph/*  →  LangGraph Server (2024)                      │   │
│  │  /api/*            →  Gateway API (8001)                           │   │
│  │  /*                →  Frontend (3000)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────────────┐
│   LangGraph Server  │ │    Gateway API      │ │     IM Channels             │
│     (Port 2024)     │ │    (Port 8001)      │ │  - Feishu/Lark              │
│                     │ │                     │ │  - Slack                    │
│  - Agent Runtime    │ │  - Models API       │ │  - Telegram                 │
│  - Thread Mgmt      │ │  - MCP Config       │ │                             │
│  - SSE Streaming    │ │  - Skills Mgmt      │ │                             │
│  - Checkpointing    │ │  - File Uploads     │ │                             │
└─────────────────────┘ └─────────────────────┘ └─────────────────────────────┘
          │                       │
          │     ┌─────────────────┘
          │     │
          ▼     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Shared Services Layer                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Config    │ │   Sandbox   │ │    MCP      │ │   Skills    │           │
│  │   System    │ │   System    │ │   Manager   │ │   Loader    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Model     │ │  Subagent   │ │   Memory    │ │   Tools     │           │
│  │   Factory   │ │   Executor  │ │   System    │ │   Registry  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Next.js 16, React 19, Tailwind CSS 4 | 现代 React 全栈框架 |
| 后端 | Python 3.11+, FastAPI, LangGraph | Agent 运行时和 API |
| 数据库 | SQLite/PostgreSQL (可选) | 状态持久化 |
| 消息队列 | 内置异步任务 | 子 Agent 执行 |
| 沙箱 | Local/Docker/AIO Sandbox | 代码执行隔离 |

---

## 2. 核心模块清单和职责

### 2.1 Backend 核心模块

| 模块路径 | 核心文件 | 职责 |
|----------|----------|------|
| `src/agents/lead_agent/` | `agent.py`, `prompt.py` | Lead Agent 创建和配置 |
| `src/agents/middlewares/` | 8 个 middleware | 请求处理链（文件上传、沙箱、摘要等） |
| `src/agents/thread_state.py` | `ThreadState` | 扩展 LangGraph AgentState |
| `src/subagents/` | `executor.py`, `builtins/` | 子 Agent 执行引擎 |
| `src/tools/` | `builtins/`, `tools.py` | 工具注册和内置工具 |
| `src/sandbox/` | `local/`, `middleware.py` | 沙箱环境管理 |
| `src/skills/` | `loader.py`, `parser.py` | Skill 系统加载和解析 |
| `src/mcp/` | `manager.py`, `client.py` | MCP 服务器集成 |
| `src/models/` | `factory.py` | 模型工厂（支持多提供商） |
| `src/channels/` | `feishu.py`, `slack.py`, `telegram.py` | IM 渠道集成 |
| `src/gateway/` | `app.py`, `routers/` | REST API 网关 |
| `src/config/` | 多个 config 文件 | 配置管理系统 |

### 2.2 Frontend 核心模块

| 模块路径 | 职责 |
|----------|------|
| `src/app/` | Next.js App Router 页面 |
| `src/core/api/` | API 客户端和数据获取 |
| `src/core/threads/` | 线程管理 |
| `src/core/skills/` | Skill 系统前端 |
| `src/core/mcp/` | MCP 配置界面 |
| `src/core/todos/` | 待办事项系统 |
| `src/components/` | React UI 组件 |

### 2.3 配置系统

| 配置文件 | 用途 |
|----------|------|
| `config.yaml` | 主配置（模型、工具、沙箱等） |
| `extensions_config.json` | MCP 服务器和 Skill 状态 |

---

## 3. 任务编排核心逻辑

### 3.1 Lead Agent 执行流程

```
用户请求
    │
    ▼
┌─────────────────────────────────────┐
│ 1. ThreadDataMiddleware             │
│    - 初始化 workspace/uploads/outputs 路径 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 2. UploadsMiddleware                │
│    - 处理上传文件列表                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 3. SandboxMiddleware                │
│    - 获取沙箱环境                     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 4. DanglingToolCallMiddleware       │
│    - 修复缺失的 ToolMessage          │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 5. SummarizationMiddleware (可选)    │
│    - 上下文摘要（token 限制时触发）    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 6. TodoMiddleware (plan_mode 时)     │
│    - 任务跟踪和管理                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 7. TitleMiddleware                  │
│    - 自动生成对话标题                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 8. MemoryMiddleware                 │
│    - 记忆队列和更新                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 9. ViewImageMiddleware (vision 模型) │
│    - 处理图片输入                     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 10. SubagentLimitMiddleware (可选)   │
│    - 限制并行子 Agent 数量            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 11. ClarificationMiddleware         │
│    - 处理澄清请求（最后拦截）          │
└─────────────────────────────────────┘
    │
    ▼
Agent Core (Model + Tools + System Prompt)
    │
    ▼
SSE 流式响应
```

### 3.2 Sub Agent 系统设计

#### 分工模式

| Agent 类型 | 职责 | 触发方式 |
|------------|------|----------|
| **Lead Agent** | 任务分解、调度、结果汇总 | 主入口 |
| **general-purpose** | 复杂多步骤任务（研究、分析、编码） | `task` 工具 |
| **bash** | 命令执行专家（git、构建、部署） | `task` 工具 |

#### 执行机制

```
Lead Agent
    │
    ├── task(description, prompt, subagent_type)
    │       │
    │       ▼
    │   SubagentExecutor
    │       │
    │       ├── 创建独立 Agent 实例
    │       ├── 继承父级 sandbox/thread_data
    │       ├── 在后台线程池执行
    │       └── 轮询等待结果（5秒间隔）
    │       │
    │       ▼
    │   返回结果给 Lead Agent
    │
    ├── task(...)  // 并行执行（最多 3 个）
    │
    └── 汇总所有结果
```

#### 关键设计

- **并发限制**：每轮响应最多 3 个并行子 Agent
- **超时控制**：默认 15 分钟（可配置）
- **上下文隔离**：子 Agent 有自己的消息历史
- **资源继承**：共享父级的沙箱和线程数据

---

## 4. Skill 系统实现

### 4.1 目录结构

```
skills/
├── public/                    # 公共 Skills（代码仓库维护）
│   ├── pdf-processing/
│   │   └── SKILL.md
│   ├── frontend-design/
│   │   └── SKILL.md
│   └── ...
└── custom/                    # 自定义 Skills（用户安装，gitignored）
    └── user-installed/
        └── SKILL.md
```

### 4.2 SKILL.md 格式

```yaml
---
name: PDF Processing
description: Handle PDF documents efficiently
license: MIT
allowed-tools:
  - read_file
  - write_file
  - bash
---

# Skill Instructions
内容注入到系统提示词中...
```

### 4.3 加载流程

```
1. 扫描 skills/public/ 和 skills/custom/ 目录
2. 解析每个 SKILL.md 的 YAML frontmatter
3. 从 extensions_config.json 读取启用状态
4. 将启用的 Skill 内容注入系统提示词
```

---

## 5. 与 OpenClaw 的异同对比

### 5.1 架构对比

| 维度 | DeerFlow | OpenClaw |
|------|----------|----------|
| **定位** | 完整的 Agent 应用平台 | AI Agent 运行时和工具框架 |
| **前端** | 内置 Next.js 全功能 UI | 无内置前端，依赖外部集成 |
| **后端** | LangGraph + FastAPI | 自有 Agent 运行时 |
| **部署** | 独立部署（Docker/本地） | 作为服务嵌入 |
| **扩展** | MCP + Skill 系统 | Skills + Tools |

### 5.2 Agent 系统对比

| 特性 | DeerFlow | OpenClaw |
|------|----------|----------|
| **多 Agent** | Lead + Sub Agent 模式 | Multi-Agent 协作 |
| **任务分解** | 显式 `task` 工具调用 | 隐式/显式调度 |
| **并行执行** | 最多 3 个并行子 Agent | 支持更多并行 |
| **上下文管理** | SummarizationMiddleware | 自动上下文管理 |
| **记忆系统** | 内置 MemoryMiddleware | 支持多种记忆后端 |

### 5.3 工具系统对比

| 特性 | DeerFlow | OpenClaw |
|------|----------|----------|
| **内置工具** | bash, read_file, write_file, web_search 等 | 类似 |
| **MCP 支持** | ✅ 完整支持 | ✅ 完整支持 |
| **Skill 系统** | ✅ SKILL.md 格式 | ✅ SKILL.md 格式 |
| **工具注册** | YAML 配置 + 代码注册 | 代码注册 |
| **沙箱** | Local/Docker/AIO | Docker/本地 |

### 5.4 集成点分析

DeerFlow 与 OpenClaw 可以集成的点：

1. **MCP 工具共享**：DeerFlow 的 MCP 配置可直接用于 OpenClaw
2. **Skill 共享**：SKILL.md 格式相同，Skills 可复用
3. **模型配置**：模型配置格式类似，可互相参考
4. **沙箱系统**：AIO Sandbox 可被两者共用

---

## 6. 可优化/改造点清单

### 6.1 架构层面

| 优先级 | 优化点 | 说明 |
|--------|--------|------|
| 🔴 高 | **子 Agent 并发限制提升** | 当前硬编码 3 个，应可配置 |
| 🔴 高 | **Agent 生命周期管理** | 缺少 Agent 注册表和动态加载 |
| 🟡 中 | **工作流引擎** | 支持可视化编排复杂工作流 |
| 🟡 中 | **分布式执行** | 支持多节点部署和负载均衡 |
| 🟢 低 | **插件系统** | 支持运行时加载插件 |

### 6.2 功能层面

| 优先级 | 优化点 | 说明 |
|--------|--------|------|
| 🔴 高 | **RAG 集成** | 缺少内置向量检索和知识库 |
| 🔴 高 | **持久化存储** | Thread 状态应支持数据库存储 |
| 🟡 中 | **用户认证** | 当前无认证系统 |
| 🟡 中 | **审计日志** | 缺少完整的操作日志 |
| 🟢 低 | **多语言支持** | i18n 框架已有，需完善翻译 |

### 6.3 性能层面

| 优先级 | 优化点 | 说明 |
|--------|--------|------|
| 🔴 高 | **连接池管理** | MCP 和数据库连接池 |
| 🟡 中 | **缓存层** | 工具结果和配置缓存 |
| 🟡 中 | **流式优化** | SSE 连接稳定性 |
| 🟢 低 | **资源限制** | 沙箱资源配额管理 |

### 6.4 代码质量

| 优先级 | 优化点 | 说明 |
|--------|--------|------|
| 🟡 中 | **类型注解** | 部分代码缺少完整类型 |
| 🟡 中 | **测试覆盖** | 缺少单元和集成测试 |
| 🟢 低 | **文档完善** | API 文档和开发指南 |

---

## 7. 二次开发建议方案

### 7.1 短期方案（1-2 周）

**目标**：快速定制和扩展

1. **自定义 Skill 开发**
   - 在 `skills/custom/` 创建 SKILL.md
   - 通过 Gateway API 启用
   - 无需修改核心代码

2. **MCP 工具集成**
   - 编辑 `extensions_config.json`
   - 添加所需的 MCP 服务器
   - 即时生效

3. **前端主题定制**
   - 修改 Tailwind 配置
   - 替换 Logo 和品牌元素
   - 调整页面布局

### 7.2 中期方案（1-2 月）

**目标**：深度定制和功能扩展

1. **新增工具类型**
   ```python
   # 在 src/tools/builtins/ 添加新工具
   @tool("my_custom_tool")
   def my_tool(...) -> str:
       ...
   ```

2. **自定义 Sub Agent 类型**
   ```python
   # 在 src/subagents/builtins/ 添加
   class MySubagentConfig(SubagentConfig):
       ...
   ```

3. **数据库持久化**
   - 修改 `checkpointer` 配置为 PostgreSQL
   - 添加用户和会话表
   - 实现认证中间件

4. **RAG 系统集成**
   - 集成向量数据库（如 Chroma、Pinecone）
   - 添加文档上传和索引接口
   - 实现检索增强生成

### 7.3 长期方案（3-6 月）

**目标**：产品化和平台化

1. **工作流引擎**
   - 设计可视化工作流 DSL
   - 实现工作流解析和执行引擎
   - 前端可视化编辑器

2. **多租户架构**
   - 租户隔离的数据模型
   - 资源配额管理
   - 计费系统集成

3. **企业级功能**
   - SSO 集成（OAuth2/SAML）
   - 审计日志和合规报告
   - 数据加密和隐私保护

4. **生态建设**
   - Skill 市场
   - MCP 服务器仓库
   - 开发者文档和 SDK

### 7.4 与 OpenClaw 集成方案

如果需要在 OpenClaw 中使用 DeerFlow 的能力：

```
方案 A：MCP 桥接
- 将 DeerFlow 的 Agent 封装为 MCP 服务器
- OpenClaw 通过 MCP 调用 DeerFlow

方案 B：共享后端
- 复用 DeerFlow 的 backend 代码
- OpenClaw 作为上层编排层

方案 C：混合部署
- DeerFlow 作为独立服务运行
- OpenClaw 通过 HTTP API 调用
```

---

## 8. 总结

DeerFlow 是一个设计精良的 Agent 应用平台，具有以下特点：

**优势**：
- 完整的端到端解决方案（前端+后端）
- 清晰的 Agent 分层架构（Lead + Sub）
- 灵活的扩展机制（MCP + Skill）
- 完善的 IM 渠道集成

**适合场景**：
- 快速搭建 AI 助手应用
- 需要多 Agent 协作的复杂任务
- 与 IM 平台深度集成

**改造建议**：
- 优先完善 RAG 和用户认证
- 提升子 Agent 并发能力
- 考虑与 OpenClaw 的能力互补

---

*报告生成时间：2026-03-11*
*分析版本：DeerFlow main branch*
