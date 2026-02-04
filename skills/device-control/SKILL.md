---
name: device-control
description: Control smart home devices - turn on/off plugs and switches
---

# Device Control Skill

Templates for controlling smart home devices.

## Controllable Devices

| Device | Device ID | Room |
|--------|-----------|------|
| plug_0 | 25 | Working area |
| plug_1 | 35 | Robot Corner |
| plug_2 | 37 | Kaspar Room |
| plug_3 | 39 | Entrance |
| plug_4 | 41 | Working area |

## Turn On Device

```python
from rh_sensors.homecentre_actuators import ZWaveHomeActuator
actuator = ZWaveHomeActuator()

result = actuator.setValue(DEVICE_ID, "turnOn", 1)
print("checkmark Device turned on")
```

## Turn Off Device

```python
from rh_sensors.homecentre_actuators import ZWaveHomeActuator
actuator = ZWaveHomeActuator()

result = actuator.setValue(DEVICE_ID, "turnOff", 0)
print("checkmark Device turned off")
```

## Room-based Control

To control a device by room name:
1. Look up the device ID from the table above
2. Use the appropriate device ID in setValue()

Example - Turn off Entrance plug:
```python
from rh_sensors.homecentre_actuators import ZWaveHomeActuator
actuator = ZWaveHomeActuator()
actuator.setValue(39, "turnOff", 0)  # plug_3, Entrance
print("checkmark Entrance plug turned off")
```
