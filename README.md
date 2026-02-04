# 🏠 LinguaHome

**Language-Driven Smart Home Automation**

LinguaHome is a code-generative LLM framework for smart home control. Users send requests in natural language, and the system generates and executes Python code through LLM to query and control smart home devices.

## ✨ Features

- **🤖 Code-as-Intent**: LLM dynamically generates code, no predefined intent classification needed
- **🔌 Zero-Shot Control**: Zero-shot device control capability
- **🧠 Memory System**: Daily memory + long-term memory support
- **🛡️ Safe Execution**: Secure code execution sandbox
- **📱 Multi-Channel**: Supports Telegram, WhatsApp, and CLI interaction
- **🤖 Multi-LLM**: Supports OpenAI, Anthropic, Gemini

## 📁 Project Structure

```
├── __init__.py              # Package initialization
├── main.py                  # CLI entry point
├── config.py                # Configuration and device mapping
├── mock_sensors.py          # Mock sensors for testing
├── requirements.txt         # Dependencies
├── test_linguahome.py       # Test script
│
├── agent/                   # Agent core
│   ├── loop.py              # Main loop
│   ├── memory.py            # Memory system
│   ├── context.py           # Context builder
│   ├── code_executor.py     # Code executor
│   └── llm_provider.py      # LLM interface (OpenAI/Anthropic/Gemini)
│
├── channels/                # Message channels
│   ├── telegram_bot.py      # Telegram integration
│   └── whatsapp_bot.py      # WhatsApp integration (via Twilio)
│
└── skills/                  # Skill files
    ├── linguahome/SKILL.md  # Core skill
    ├── sensor-query/SKILL.md # Sensor query
    └── device-control/SKILL.md # Device control
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install litellm python-telegram-bot twilio flask
```

### 2. Configure Environment Variables

```bash
# LLM API (choose one)
export OPENAI_API_KEY="sk-..."        # GPT models
export ANTHROPIC_API_KEY="sk-ant-..." # Claude models
export GEMINI_API_KEY="..."           # Gemini models

# Telegram (optional)
export TELEGRAM_BOT_TOKEN="your-token"

# WhatsApp (optional, requires Twilio)
export TWILIO_ACCOUNT_SID="your-sid"
export TWILIO_AUTH_TOKEN="your-token"
export TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886"

# Model selection (default: gpt-4o)
export LINGUAHOME_MODEL="gpt-4o"
# Options: claude, gemini, gpt-4o-mini, claude-haiku, gemini-flash
```

### 3. Run Tests

```bash
python3 test_linguahome.py
```

### 4. Interactive Mode

```bash
python3 main.py
```

### 5. Single Query

```bash
python3 main.py "What's the temperature in Robot Corner?"
```

### 6. Telegram Bot

```bash
python3 -m channels.telegram_bot
```

### 7. WhatsApp Bot

```bash
python3 -m channels.whatsapp_bot
```

## 🤖 Supported LLM Models

| Provider | Model | Alias |
|----------|-------|-------|
| OpenAI | gpt-4o | gpt4o |
| OpenAI | gpt-4o-mini | - |
| Anthropic | claude-3-5-sonnet | claude |
| Anthropic | claude-3-5-haiku | claude-haiku |
| Google | gemini-2.0-flash | gemini |
| Google | gemini-1.5-pro | gemini-pro |

## 🎯 Usage Examples

### Query Temperature
```
👤 You: What's the temperature in Robot Corner?
🤖 LinguaHome: 🌡️ Robot Corner temperature: 23.9°C
```

### Control Device
```
👤 You: Turn off the plug at the entrance
🤖 LinguaHome: ✅ Entrance plug (plug_3) has been turned off
```

### Complex Query
```
👤 You: Which room is the warmest?
🤖 LinguaHome: 🔥 The warmest room is Kaspar Room at 24.1°C

All temperatures:
  • Kaspar Room: 24.1°C
  • Robot Corner: 23.9°C
  • Observation Room: 23.2°C
  • Working area: 22.5°C
  • Entrance: 21.8°C
```

## 🏠 Supported Devices

| Device Name | Sensor ID | Device ID | Room | Type |
|-------------|-----------|-----------|------|------|
| plug_0 | 1025 | 25 | Working area | Controllable plug |
| plug_1 | 1035 | 35 | Robot Corner | Controllable plug |
| plug_2 | 1037 | 37 | Kaspar Room | Controllable plug |
| plug_3 | 1039 | 39 | Entrance | Controllable plug |
| plug_4 | 1041 | 41 | Working area | Controllable plug |
| motion_0_temp | 1028 | 28 | Working area | Temperature |
| motion_1_temp | 1060 | 60 | Entrance | Temperature |
| motion_2_temp | 1066 | 66 | Observation Room | Temperature |
| motion_3_temp | 1072 | 72 | Kaspar Room | Temperature |
| motion_4_temp | 1078 | 78 | Robot Corner | Temperature |

## 🔧 Architecture

```
User Message → LLM (Generate Code) → Code Executor → Result → User Response
                    ↓
              System Prompt
              (Device Mapping + Code Templates)
```

## 📊 Mock Mode

When unable to connect to the real Fibaro Home Center, the system automatically uses mock sensors for testing.

## 🔐 Security Features

- Whitelisted import modules
- Forbidden dangerous operations (os, subprocess, open, eval, exec)
- Code execution timeout protection
- Syntax checking

## 📝 Paper

This project is used for the IEEE IoT-J paper:

> **LinguaHome: A Code-Generative LLM Framework for Conversational Smart Home Automation**

## 📄 License

MIT License

---

**Version**: 0.1.0  
**Author**: Baobin Zhang
