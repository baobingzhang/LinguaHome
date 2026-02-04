---
name: device-control
description: 设备控制专用技能
metadata:
  nanobot:
    emoji: "🔌"
---

# 设备控制技能

专门用于控制智能家居设备（插座）。

## 可控设备列表

| 设备 | Device ID | 房间 |
|------|-----------|------|
| plug_0 | 25 | Working area |
| plug_1 | 35 | Robot Corner |
| plug_2 | 37 | Kaspar Room |
| plug_3 | 39 | Entrance |
| plug_4 | 41 | Working area |

## 控制命令

### 开启设备
```python
from rh_sensors.homecentre_actuators import ZWaveHomeActuator
actuator = ZWaveHomeActuator()
actuator.setValue(DEVICE_ID, "turnOn", 1)
print("✅ 设备已开启")
```

### 关闭设备
```python
from rh_sensors.homecentre_actuators import ZWaveHomeActuator
actuator = ZWaveHomeActuator()
actuator.setValue(DEVICE_ID, "turnOff", 0)
print("✅ 设备已关闭")
```

### 批量控制示例
```python
from rh_sensors.homecentre_actuators import ZWaveHomeActuator
actuator = ZWaveHomeActuator()

# 关闭所有插座
device_ids = [25, 35, 37, 39, 41]
for did in device_ids:
    actuator.setValue(did, "turnOff", 0)
print("✅ 所有插座已关闭")
```

## 安全规则
1. 控制前确认设备存在
2. 使用正确的 Device ID（不是 Sensor ID）
3. 记录操作日志
