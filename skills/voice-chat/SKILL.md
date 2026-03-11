# Voice Chat - 语音对话助手

实现语音输入 → AI处理 → 语音回复 + 文本显示

## 功能

- 接收语音消息（飞书已支持）
- 语音回复（TTS）
- 文本同时显示
- 智能判断：语音输入 → 语音回复，文字输入 → 文字回复

## 使用方式

### 自动模式（推荐）

当用户发送语音消息时，AI 会自动：
1. 识别语音内容
2. 生成回复
3. **同时发送语音 + 文字**

### 手动触发

```bash
# 生成语音回复
python3 ~/.openclaw/workspace/skills/voice-chat/scripts/voice_chat.py \
  --text "要转换的文本内容"
```

## 配置

### 环境变量

```bash
# 语音文件保存目录（可选）
export VOICE_CHAT_DIR="$HOME/.openclaw/voice-chat"
```

## 工作原理

```
用户语音 → 飞书语音识别 → AI处理 → TTS生成语音 → 同时发送语音+文字
```

## 注意事项

1. 飞书已内置语音识别，无需额外处理
2. 语音回复通过 OpenClaw TTS 工具生成
3. 语音文件临时存储，定期清理

## 依赖

- OpenClaw Gateway（提供 TTS 工具）
- Python 3.8+
