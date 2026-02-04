---
name: sensor-query
description: Query smart home sensors - temperature, motion, door status, power
---

# Sensor Query Skill

Templates for querying smart home sensors.

## Query Single Sensor

```python
from rh_sensors.db.access import Sensors
sensors = Sensors()

sensor = sensors.getSensor(SENSOR_ID)
if sensor:
    print(f"thermometer {sensor['name']}: {sensor['value']} ({sensor['status']})")
else:
    print("X Sensor not found")
```

## Query Sensors by Room

```python
from rh_sensors.db.access import Sensors
sensors = Sensors()

all_sensors = sensors.findSensors()
room_sensors = [s for s in all_sensors if s['locationName'] == 'ROOM_NAME']

for s in room_sensors:
    print(f"  {s['name']}: {s['value']}")
```

## Query Sensors by Type

```python
from rh_sensors.db.access import Sensors
sensors = Sensors()

all_sensors = sensors.findSensors()
temp_sensors = [s for s in all_sensors if 'temperature' in s['sensorTypeName'].lower()]

for s in temp_sensors:
    print(f"thermometer {s['locationName']}: {s['value']} degrees C")
```

## Available Sensor IDs

| Type | Sensor ID | Room |
|------|-----------|------|
| Temperature | 1028 | Working area |
| Temperature | 1060 | Entrance |
| Temperature | 1066 | Observation Room |
| Temperature | 1072 | Kaspar Room |
| Temperature | 1078 | Robot Corner |
| Motion | 1029 | Working area |
| Motion | 1061 | Entrance |
| Motion | 1067 | Observation Room |
| Motion | 1073 | Kaspar Room |
| Motion | 1079 | Robot Corner |
| Door | 1022 | Working area |
| Door | 1043 | Robot Corner |
| Door | 1047 | Kaspar Room |
| Door | 1051 | Entrance |
| Door | 1055 | Observation Room |
