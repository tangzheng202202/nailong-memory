#!/bin/bash
# Agent 快速启动脚本
# 用法: ./spawn-agent.sh <agent-type> <task-description>

AGENT_TYPE=$1
TASK_DESC="${@:2}"
LABEL="${AGENT_TYPE}-$(date +%s)"

if [ -z "$AGENT_TYPE" ] || [ -z "$TASK_DESC" ]; then
    echo "用法: ./spawn-agent.sh <coder|researcher|monitor> <任务描述>"
    exit 1
fi

# 根据 Agent 类型设置系统提示
 case $AGENT_TYPE in
    coder)
        SYSTEM_PROMPT="你是代码专家 Agent (Coder)。
职责: 编写高质量代码、技术实现、代码审查。
安全规则:
1. rm/chmod/dd 等危险命令必须确认
2. 所有代码改动可回滚（走 git）
3. 代码必须有注释和使用示例

工作目录: /Users/mac/.openclaw/workspace/agents/coder/workspace/"
        ;;
    researcher)
        SYSTEM_PROMPT="你是研究专家 Agent (Researcher)。
职责: 网络搜索、数据分析、资料收集。
安全规则:
1. 网络请求必须走代理（端口 17890）
2. 不存储敏感数据到外部
3. 搜索结果标注来源

工作目录: /Users/mac/.openclaw/workspace/agents/researcher/workspace/"
        ;;
    *)
        echo "未知 Agent 类型: $AGENT_TYPE"
        echo "可用类型: coder, researcher"
        exit 1
        ;;
esac

# 记录任务到队列
TASK_ID=$(date +%s)
QUEUE_FILE="/Users/mac/.openclaw/workspace/memory/task-queue.json"
jq --arg id "$TASK_ID" \
   --arg type "$AGENT_TYPE" \
   --arg task "$TASK_DESC" \
   --arg time "$(date -Iseconds)" \
   '.queue += [{id: $id, type: $type, task: $task, status: "running", created: $time}]' \
   "$QUEUE_FILE" > /tmp/task-queue.json && mv /tmp/task-queue.json "$QUEUE_FILE"

echo "🚀 启动 $AGENT_TYPE Agent..."
echo "任务 ID: $TASK_ID"
echo "任务描述: $TASK_DESC"
echo ""
echo "正在创建隔离会话..."
echo "提示: 子 Agent 启动后会直接与你对话"
echo ""

# 输出启动命令（供主 Agent 调用）
echo "EXECUTE:"
echo "sessions_spawn --label $LABEL --mode session --thinking minimal <<'EOF'"
echo "$SYSTEM_PROMPT"
echo ""
echo "任务: $TASK_DESC"
echo ""
echo "请直接开始执行，完成后说明结果。"
echo "EOF"
