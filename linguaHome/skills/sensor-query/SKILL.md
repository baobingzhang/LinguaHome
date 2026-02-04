---
name: sensor-query
description: 传感器状态查询专用技能
metadata:
  nanobot:
    emoji: "📊"
---

# 传感器查询技能

专门用于查询智能家居传感器状态。

## 查询模式

### 单个传感器
```python
from rh_sensors.db.access import Sensors
sensors = Sensors()
sensor = sensors.getSensor(SENSOR_ID)
print(f"{sensor['name']}: {sensor['value']} ({sensor['status']})")
```

### 按房间查询
```python
from rh_sensors.db.access import Sensors
sensors = Sensors()
all_sensors = sensors.findSensors()
room_sensors = [s for s in all_sensors if s['locationName'] == 'ROOM_NAME']
for s in room_sensors:
    print(f"  • {s['name']}: {s['value']}")
```

### 按类型查询
```python
from rh_sensors.db.access import Sensors
sensors = Sensors()
all_sensors = sensors.findSensors()
type_sensors = [s for s in all_sensors if 'temperature' in s['name'].lower()]
```

## 温度传感器 Sensor IDs
- Working area: 1028
- Entrance: 1060
- Observation Room: 1066
- Kaspar Room: 1072
- Robot Corner: 1078

## 输出格式
- 使用 🌡️ 表示温度
- 使用 🚶 表示运动
- 使用 🚪 表示门状态
- 使用 ⚡ 表示功率
