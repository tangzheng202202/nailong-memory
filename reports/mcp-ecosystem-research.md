# MCP 生态连接器调研报告

> 调研日期: 2026-03-11
> 调研范围: MCP协议、生态现状、OpenClaw集成方案

---

## 一、MCP 协议核心概念

### 1.1 什么是 MCP

**Model Context Protocol (MCP)** 是 Anthropic 推出的开放协议，用于标准化 AI 应用与外部系统（数据源、工具、工作流）的连接。类比 USB-C 接口，MCP 为 AI 应用提供了一种标准化的"即插即用"方式来连接各种外部能力。

### 1.2 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Host (AI Application)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MCP Client 1 │  │ MCP Client 2 │  │ MCP Client 3 │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ MCP Server A │  │ MCP Server B │  │ MCP Server C │
   │  (Local)     │  │  (Local)     │  │  (Remote)    │
   └──────────────┘  └──────────────┘  └──────────────┘
```

**三个核心角色：**
- **MCP Host**: AI 应用（如 Claude Desktop、VS Code、Cursor）
- **MCP Client**: 与 MCP Server 保持连接的客户端组件
- **MCP Server**: 提供上下文和能力的程序

### 1.3 协议分层

| 层级 | 职责 | 关键技术 |
|------|------|----------|
| **数据层** | 定义 JSON-RPC 通信协议 | JSON-RPC 2.0 |
| **传输层** | 管理通信通道和认证 | stdio / Streamable HTTP |

### 1.4 核心原语 (Primitives)

**Server 提供的三大能力：**

| 原语 | 说明 | 类比 |
|------|------|------|
| **Tools** | 可执行函数，AI 可调用来执行操作 | POST 端点 |
| **Resources** | 数据源，为 AI 提供上下文 | GET 端点 |
| **Prompts** | 可复用的交互模板 | 预设提示词 |

**Client 可提供的可选能力：**
- **Sampling**: Server 发起的 LLM 采样请求
- **Roots**: Server 查询文件系统边界
- **Elicitation**: Server 向用户请求额外信息

### 1.5 传输机制

#### 1.5.1 stdio 传输
- **适用场景**: 本地进程间通信
- **工作原理**: Client 启动 Server 作为子进程，通过 stdin/stdout 交换 JSON-RPC 消息
- **特点**: 无网络开销，性能最优

#### 1.5.2 Streamable HTTP 传输
- **适用场景**: 远程服务、多客户端连接
- **工作原理**: 
  - HTTP POST 发送客户端消息
  - 可选 SSE (Server-Sent Events) 流式传输服务端消息
  - 支持标准 HTTP 认证（Bearer Token、API Key、OAuth）
- **安全要求**: 必须验证 Origin 头防止 DNS 重绑定攻击

### 1.6 协议版本

- **当前版本**: `2025-11-25`
- **版本格式**: `YYYY-MM-DD`（上次破坏性变更日期）
- **版本协商**: 在初始化阶段完成，支持多版本兼容

---

## 二、主流 MCP 服务器生态

### 2.1 官方参考实现

GitHub: `modelcontextprotocol/servers`

| 服务器 | 功能 | 语言 |
|--------|------|------|
| **filesystem** | 本地文件系统访问 | TypeScript |
| **sqlite** | SQLite 数据库操作 | Python |
| **postgres** | PostgreSQL 数据库 | TypeScript |
| **github** | GitHub API 集成 | TypeScript |
| **slack** | Slack 工作区操作 | TypeScript |
| **git** | Git 仓库操作 | Python |
| **fetch** | HTTP 请求获取 | Python |
| **sentry** | 错误监控集成 | Python |
| **puppeteer** | 浏览器自动化 | TypeScript |

### 2.2 社区热门服务器

来源: `punkpeye/awesome-mcp-servers`

#### 开发工具类
| 服务器 | 功能 | Stars |
|--------|------|-------|
| **@anthropic-ai/mcp-server-fetch** | 网页内容获取 | 官方 |
| **mcp-server-commands** | 执行 shell 命令 | 高 |
| **mcp-server-git** | Git 操作增强 | 高 |
| **mcp-server-github** | GitHub 深度集成 | 高 |
| **mcp-server-docker** | Docker 容器管理 | 中 |
| **mcp-server-kubernetes** | K8s 集群操作 | 中 |

#### 数据库/存储类
| 服务器 | 功能 |
|--------|------|
| **mcp-server-postgres** | PostgreSQL |
| **mcp-server-mysql** | MySQL |
| **mcp-server-mongodb** | MongoDB |
| **mcp-server-redis** | Redis |
| **mcp-server-chroma** | Chroma 向量数据库 |
| **mcp-server-supabase** | Supabase |

#### 云服务类
| 服务器 | 功能 |
|--------|------|
| **mcp-server-aws** | AWS 服务 |
| **mcp-server-gcp** | Google Cloud |
| **mcp-server-azure** | Azure |
| **mcp-server-vercel** | Vercel 部署 |
| **mcp-server-cloudflare** | Cloudflare |

#### 生产力工具类
| 服务器 | 功能 |
|--------|------|
| **mcp-server-notion** | Notion 工作区 |
| **mcp-server-slack** | Slack |
| **mcp-server-discord** | Discord |
| **mcp-server-telegram** | Telegram |
| **mcp-server-obsidian** | Obsidian 笔记 |
| **mcp-server-todoist** | Todoist 任务 |

#### 搜索/知识类
| 服务器 | 功能 |
|--------|------|
| **mcp-server-brave-search** | Brave 搜索 |
| **mcp-server-duckduckgo** | DuckDuckGo |
| **mcp-server-wikipedia** | Wikipedia |
| **mcp-server-arxiv** | 学术论文 |
| **mcp-server-pubmed** | 医学文献 |

### 2.3 MCP Registry

官方注册表: `https://registry.modelcontextprotocol.io/`

- 集中发布和发现 MCP 服务器
- 支持 npm、PyPI 等包管理器
- 提供 GitHub Actions 自动发布

### 2.4 官方 SDK

| SDK | 语言 | 状态 | 包名 |
|-----|------|------|------|
| **TypeScript SDK** | TypeScript/Node.js | v2 开发中 | `@modelcontextprotocol/server` |
| **Python SDK** | Python | v1 稳定 | `mcp` |
| **C# SDK** | C# | 可用 | 社区维护 |
| **Go SDK** | Go | 可用 | 社区维护 |
| **Java SDK** | Java | 可用 | 社区维护 |

---

## 三、OpenClaw MCP 化技术方案

### 3.1 双角色定位

OpenClaw 在 MCP 生态中可以扮演两种角色：

#### 角色 A: MCP Server (被调用)
将 OpenClaw 的能力封装为 MCP 服务器，供 Claude Desktop、Cursor 等客户端调用。

#### 角色 B: MCP Client (调用者)
OpenClaw 作为客户端，调用外部 MCP 服务器扩展能力。

### 3.2 OpenClaw as MCP Server 方案

#### 3.2.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Host (Claude Desktop)                │
│                         │                                   │
│                         ▼                                   │
│                    MCP Client                               │
└─────────────────────────┬───────────────────────────────────┘
                          │ stdio / HTTP
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  OpenClaw MCP Server                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              MCP Protocol Layer                      │  │
│  │         (JSON-RPC 2.0 / stdio / HTTP)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              OpenClaw Skill Bridge                   │  │
│  │    (Skill Discovery → Tool Registration)            │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│          ┌───────────────┼───────────────┐                  │
│          ▼               ▼               ▼                  │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│    │  Skill A │    │  Skill B │    │  Skill C │            │
│    │(feishu)  │    │(browser) │    │(github)  │            │
│    └──────────┘    └──────────┘    └──────────┘            │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.2 Skill 到 MCP Tool 的映射

```typescript
// Skill 定义示例
interface Skill {
  name: string;
  description: string;
  parameters: JSONSchema;
  handler: (args: any) => Promise<any>;
}

// 映射为 MCP Tool
interface MCPTool {
  name: string;
  description: string;
  inputSchema: JSONSchema;
  // handler 在 Server 端执行
}
```

**映射规则：**
| Skill 属性 | MCP Tool 属性 | 说明 |
|-----------|--------------|------|
| `name` | `name` | 保持唯一性，可添加前缀 |
| `description` | `description` | 直接映射 |
| `parameters` | `inputSchema` | JSON Schema 格式 |
| `handler` | 内部实现 | 调用 Skill 执行 |

#### 3.2.3 技术实现路径

**方案 1: TypeScript SDK (推荐)**
```typescript
import { Server } from '@modelcontextprotocol/server';
import { z } from 'zod';

// 创建 MCP Server
const server = new Server({
  name: 'openclaw-server',
  version: '1.0.0'
});

// 注册 Skill 为 Tool
server.registerTool({
  name: 'feishu_send_message',
  description: 'Send message to Feishu',
  inputSchema: z.object({
    channel: z.string(),
    message: z.string()
  }),
  handler: async (args) => {
    // 调用 OpenClaw Skill 系统
    return await skillManager.execute('feishu.send', args);
  }
});

// 启动 stdio 传输
server.start({ transport: 'stdio' });
```

**方案 2: Python SDK**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("openclaw")

@mcp.tool()
def feishu_send_message(channel: str, message: str) -> str:
    """Send message to Feishu"""
    return skill_manager.execute('feishu.send', locals())

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 3.3 OpenClaw as MCP Client 方案

#### 3.3.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Core                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Skill A    │  │   Skill B    │  │  MCP Client  │      │
│  │  (native)    │  │  (native)    │  │  (adapter)   │      │
│  └──────────────┘  └──────────────┘  └──────┬───────┘      │
│                                             │               │
└─────────────────────────────────────────────┼───────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
            ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
            │ MCP Server 1 │          │ MCP Server 2 │          │ MCP Server N │
            │ (filesystem) │          │ (postgres)   │          │ (custom)     │
            └──────────────┘          └──────────────┘          └──────────────┘
```

#### 3.3.2 MCP Client 集成代码

```typescript
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

class MCPClientAdapter {
  private clients: Map<string, Client> = new Map();

  async connect(serverId: string, command: string, args: string[]) {
    const transport = new StdioClientTransport({
      command,
      args
    });

    const client = new Client({
      name: 'openclaw-client',
      version: '1.0.0'
    });

    await client.connect(transport);
    this.clients.set(serverId, client);

    // 获取可用工具
    const tools = await client.listTools();
    return tools;
  }

  async callTool(serverId: string, toolName: string, args: any) {
    const client = this.clients.get(serverId);
    if (!client) throw new Error(`Server ${serverId} not connected`);

    return await client.callTool(toolName, args);
  }
}
```

### 3.4 MCP 与 Skill 系统的融合方案

#### 3.4.1 统一能力层

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Capability Layer                 │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              Skill Registry                         │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │  │
│   │  │ Native Skill│  │ MCP Skill   │  │ Hybrid Skill│ │  │
│   │  │  (内置)     │  │  (外部MCP)  │  │  (组合)     │ │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘ │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              Execution Engine                       │  │
│   │         (统一调度、权限、日志)                      │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 3.4.2 Skill 类型定义

```typescript
// 基础 Skill 接口
interface BaseSkill {
  id: string;
  name: string;
  description: string;
  parameters: JSONSchema;
  returns: JSONSchema;
}

// 原生 Skill
interface NativeSkill extends BaseSkill {
  type: 'native';
  handler: (args: any, context: Context) => Promise<any>;
}

// MCP Skill (封装外部 MCP Server)
interface MCPSkill extends BaseSkill {
  type: 'mcp';
  serverId: string;
  toolName: string;
  transport: 'stdio' | 'http';
  connection: MCPConnectionConfig;
}

// 组合 Skill
interface HybridSkill extends BaseSkill {
  type: 'hybrid';
  steps: Array<{
    skill: string;
    input: Record<string, any>;
  }>;
}
```

#### 3.4.3 配置示例

```yaml
# openclaw-mcp.yaml
mcp:
  # OpenClaw 作为 MCP Server
  server:
    enabled: true
    transport: stdio  # 或 http
    expose_skills:
      - feishu.*
      - github.*
      - browser.*
    
  # OpenClaw 作为 MCP Client
  clients:
    filesystem:
      enabled: true
      transport: stdio
      command: npx
      args: ['-y', '@modelcontextprotocol/server-filesystem', '/Users/mac/Documents']
      
    sqlite:
      enabled: true
      transport: stdio
      command: uvx
      args: ['mcp-server-sqlite', '--db-path', '/path/to/db.sqlite']
      
    brave-search:
      enabled: true
      transport: stdio
      command: npx
      args: ['-y', '@modelcontextprotocol/server-brave-search']
      env:
        BRAVE_API_KEY: ${BRAVE_API_KEY}
```

---

## 四、实施步骤和优先级

### 4.1 阶段规划

```
Phase 1 (2-3周)          Phase 2 (3-4周)          Phase 3 (4-6周)
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  MCP Client     │ ───► │  MCP Server     │ ───► │  Ecosystem      │
│  (调用外部)     │      │  (暴露能力)     │      │  (生态完善)     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
│ • 集成 MCP SDK  │      │ • Skill→Tool    │      │ • Registry 发布 │
│ • 连接常用Server│      │ • stdio/HTTP    │      │ • 多传输支持    │
│ • Tool 调用封装 │      │ • 动态发现      │      │ • 企业级特性    │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### 4.2 Phase 1: MCP Client 能力 (高优先级)

**目标**: 让 OpenClaw 能调用外部 MCP 服务器

**任务清单：**
- [ ] 集成 `@modelcontextprotocol/client` SDK
- [ ] 实现 MCP Server 连接管理
- [ ] 实现 MCP Tool 调用封装
- [ ] 添加配置管理（支持 `openclaw-mcp.yaml`）
- [ ] 预置常用 MCP Server 配置模板

**优先集成的 MCP Servers：**
1. **filesystem** - 文件系统操作
2. **sqlite/postgres** - 数据库查询
3. **fetch** - 网页内容获取
4. **brave-search** - 搜索能力
5. **github** - GitHub 操作

### 4.3 Phase 2: MCP Server 能力 (中优先级)

**目标**: 让外部客户端能调用 OpenClaw 的 Skill

**任务清单：**
- [ ] 实现 MCP Server 核心框架
- [ ] 实现 Skill → MCP Tool 自动映射
- [ ] 支持 stdio 传输
- [ ] 支持 Streamable HTTP 传输
- [ ] 实现动态 Tool 发现
- [ ] 添加权限控制（哪些 Skill 可暴露）

**技术要点：**
- Skill 元数据提取
- 参数 Schema 转换
- 执行结果格式化

### 4.4 Phase 3: 生态完善 (低优先级)

**任务清单：**
- [ ] 发布到 MCP Registry
- [ ] 支持 OAuth 认证
- [ ] 支持 Streaming 响应
- [ ] 性能优化（连接池、缓存）
- [ ] 监控和日志
- [ ] 文档和示例

### 4.5 技术选型建议

| 组件 | 推荐方案 | 理由 |
|------|----------|------|
| **SDK** | TypeScript SDK | OpenClaw 基于 Node.js，生态更好 |
| **传输** | 先 stdio 后 HTTP | stdio 简单稳定，HTTP 更灵活 |
| **配置** | YAML + 环境变量 | 与现有 Skill 配置保持一致 |
| **进程管理** | 子进程池 | 避免频繁启停 MCP Server |

### 4.6 风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| MCP 协议快速迭代 | 中 | 封装抽象层，隔离协议细节 |
| SDK 版本兼容 | 中 | 锁定版本，定期升级测试 |
| 进程管理复杂 | 中 | 使用进程池，健康检查 |
| 安全风险 | 高 | 权限隔离，用户确认敏感操作 |

---

## 五、总结

### 5.1 核心价值

1. **能力扩展**: 无缝集成 1000+ MCP 服务器，瞬间扩展 OpenClaw 能力边界
2. **生态互通**: 与 Claude Desktop、Cursor、VS Code 等主流工具生态互通
3. **标准化**: 采用行业标准协议，降低用户学习成本

### 5.2 关键决策

| 决策项 | 建议 |
|--------|------|
| 先做 Client 还是 Server? | **Client 优先**，快速获得能力扩展 |
| 支持哪些传输? | **stdio 优先**，HTTP 后续补充 |
| 哪些 Skill 暴露? | 白名单机制，用户可控 |
| 配置格式? | YAML，与现有 Skill 配置统一 |

### 5.3 下一步行动

1. **立即**: 创建 POC，验证 OpenClaw 调用 filesystem MCP Server
2. **本周**: 完成 Phase 1 技术方案设计
3. **本月**: 发布 MCP Client 功能
4. **下月**: 启动 MCP Server 开发

---

## 附录

### A. 参考资源

- **MCP 官网**: https://modelcontextprotocol.io/
- **协议规范**: https://spec.modelcontextprotocol.io/
- **官方 Servers**: https://github.com/modelcontextprotocol/servers
- **TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Awesome MCP**: https://github.com/punkpeye/awesome-mcp-servers
- **MCP Registry**: https://registry.modelcontextprotocol.io/

### B. 术语表

| 术语 | 说明 |
|------|------|
| MCP | Model Context Protocol |
| Host | AI 应用程序 |
| Client | 与 Server 通信的组件 |
| Server | 提供上下文和能力的程序 |
| Tool | 可执行函数 |
| Resource | 数据源 |
| Prompt | 可复用模板 |
| stdio | 标准输入输出传输 |
| SSE | Server-Sent Events |
