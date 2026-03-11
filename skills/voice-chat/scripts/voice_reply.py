#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Reply Script - OpenClaw Integration
语音回复脚本 - 直接集成 OpenClaw 工具调用

这个脚本设计为被 OpenClaw Agent 直接调用，通过工具调用实现 TTS
"""

import sys
import os
import tempfile
import json

# 配置路径
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "wake_word": "奶龙",
        "voice_enabled": True,
        "text_enabled": True
    }

def check_wake_word(text, config):
    """检查是否包含唤醒词"""
    wake_word = config.get("wake_word", "奶龙")
    return wake_word in text

def main():
    """
    主函数 - 输出需要执行的工具调用指令
    
    输出格式为 JSON，供 OpenClaw Agent 解析并执行
    """
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "缺少参数",
            "usage": "python3 voice_reply.py \"要回复的文本内容\""
        }, ensure_ascii=False))
        sys.exit(1)
    
    # 获取回复文本
    reply_text = sys.argv[1]
    
    # 加载配置
    config = load_config()
    
    # 检查唤醒词（可选功能）
    is_wake_word_called = check_wake_word(reply_text, config)
    
    # 构建输出指令
    result = {
        "text_reply": reply_text,
        "voice_enabled": config.get("voice_enabled", True),
        "text_enabled": config.get("text_enabled", True),
        "wake_word_detected": is_wake_word_called,
        "actions": []
    }
    
    # 添加文本回复动作
    if config.get("text_enabled", True):
        result["actions"].append({
            "type": "message",
            "tool": "message",
            "params": {
                "action": "send",
                "message": reply_text
            }
        })
    
    # 添加语音回复动作
    if config.get("voice_enabled", True):
        result["actions"].append({
            "type": "voice",
            "tool": "tts",
            "params": {
                "text": reply_text
            }
        })
    
    # 输出 JSON 供 OpenClaw 解析
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
