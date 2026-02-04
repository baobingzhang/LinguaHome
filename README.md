# 🏠 LinguaHome

**Language-Driven Smart Home Automation**

LinguaHome 是一个基于 LLM 代码生成的智能家居控制框架。用户使用自然语言发送请求，系统通过 LLM 生成 Python 代码并执行，实现智能家居的查询和控制。

## ✨ 特点

- **🤖 Code-as-Intent**: LLM 动态生成代码，无需预定义意图分类
- **🔌 Zero-Shot Control**: 零样本设备控制能力
- **🧠 Memory System**: 日记忆 + 长期记忆支持
- **🛡️ Safe Execution**: 安全的代码执行沙盒
- **📱 Multi-Channel**: 支持 Telegram、WhatsApp 和 CLI 交互
- **🤖 Multi-LLM**: 支持 OpenAI、Anthropic、Gemini

## 📁 项目结构

```
linguaHome/
├── __init__.py              # 包初始化
├── main.py                  # CLI 入口
├── config.py                # 配置和设备映射
├── mock_sensors.py          # 模拟传感器
├── requirements.txt         # 依赖
├── test_linguahome.py       # 测试脚本
│
├── agent/                   # Agent 核心
│   ├── loop.py              # 主循环
│   ├── memory.py            # 记忆系统
│   ├── context.py           # 上下文构建
│   ├── code_executor.py     # 代码执行器
│   └── llm_provider.py      # LLM 接口 (OpenAI/Anthropic/Gemini)
│
├── channels/                # 消息渠道
│   ├── telegram_bot.py      # Telegram 集成
│   └── whatsapp_bot.py      # WhatsApp 集成 (via Twilio)
│
└── skills/                  # 技能文件
    ├── linguahome/SKILL.md  # 核心技能
    ├── sensor-query/SKILL.md # 传感器查询
    └── device-control/SKILL.md # 设备控制
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install litellm python-telegram-bot twilio flask
```

### 2. 配置环境变量

```bash
# LLM API (选择其一)
export OPENAI_API_KEY="sk-..."        # GPT 模型
export ANTHROPIC_API_KEY="sk-ant-..." # Claude 模型
export GEMINI_API_KEY="..."           # Gemini 模型

# Telegram (可选)
export TELEGRAM_BOT_TOKEN="your-token"

# WhatsApp (可选，需要 Twilio)
export TWILIO_ACCOUNT_SID="your-sid"
export TWILIO_AUTH_TOKEN="your-token"
export TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886"

# 模型选择 (默认 gpt-4o)
export LINGUAHOME_MODEL="gpt-4o"
# 可选: claude, gemini, gpt-4o-mini, claude-haiku, gemini-flash
```

### 3. 运行测试

```bash
python3 test_linguahome.py
```

### 4. 交互模式

```bash
python3 -m linguaHome.main
```

### 5. 单次查询

```bash
python3 -m linguaHome.main "Robot Corner 温度多少？"
```

### 6. Telegram Bot

```bash
python3 -m linguaHome.channels.telegram_bot
```

### 7. WhatsApp Bot

```bash
python3 -m linguaHome.channels.whatsapp_bot
```

## 🤖 支持的 LLM 模型

| Provider | 模型 | 别名 |
|----------|------|------|
| OpenAI | gpt-4o | gpt4o |
| OpenAI | gpt-4o-mini | - |
| Anthropic | claude-3-5-sonnet | claude |
| Anthropic | claude-3-5-haiku | claude-haiku |
| Google | gemini-2.0-flash | gemini |
| Google | gemini-1.5-pro | gemini-pro |

## 🎯 使用示例

### 查询温度
```
👤 You: Robot Corner 温度多少？
🤖 LinguaHome: 🌡️ Robot Corner 温度: 23.9°C
```

### 控制设备
```
👤 You: 关掉入口的插座
🤖 LinguaHome: ✅ 入口插座 (plug_3) 已关闭
```

### 复杂查询
```
👤 You: 哪个房间最热？
🤖 LinguaHome: 🔥 最热的房间是 Kaspar Room，温度 24.1°C

所有温度:
  • Kaspar Room: 24.1°C
  • Robot Corner: 23.9°C
  • Observation Room: 23.2°C
  • Working area: 22.5°C
  • Entrance: 21.8°C
```

## 🏠 支持的设备

| 设备名 | Sensor ID | Device ID | 房间 | 类型 |
|--------|-----------|-----------|------|------|
| plug_0 | 1025 | 25 | Working area | 可控插座 |
| plug_1 | 1035 | 35 | Robot Corner | 可控插座 |
| plug_2 | 1037 | 37 | Kaspar Room | 可控插座 |
| plug_3 | 1039 | 39 | Entrance | 可控插座 |
| plug_4 | 1041 | 41 | Working area | 可控插座 |
| motion_0_temp | 1028 | 28 | Working area | 温度 |
| motion_1_temp | 1060 | 60 | Entrance | 温度 |
| motion_2_temp | 1066 | 66 | Observation Room | 温度 |
| motion_3_temp | 1072 | 72 | Kaspar Room | 温度 |
| motion_4_temp | 1078 | 78 | Robot Corner | 温度 |

## 🔧 架构

```
用户消息 → LLM (生成代码) → 代码执行器 → 结果 → 用户响应
               ↓
         System Prompt
         (设备映射 + 代码模板)
```

## 📊 Mock 模式

当无法连接到真实的 Fibaro Home Center 时，系统会自动使用 Mock 传感器进行测试。

## 🔐 安全特性

- 白名单导入模块
- 禁止危险操作 (os, subprocess, open, eval, exec)
- 代码执行超时保护
- 语法检查

## 📝 论文

本项目用于 IEEE IoT-J 论文:

> **LinguaHome: A Code-Generative LLM Framework for Conversational Smart Home Automation**

## 📄 License

MIT License

---

**Version**: 0.1.0  
**Author**: Baobin Zhang
