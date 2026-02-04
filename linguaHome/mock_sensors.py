"""
LinguaHome Mock Sensors

Mock implementations for testing without database/hardware.
"""

import random
from datetime import datetime
from typing import Dict, List, Optional

# Mock sensor data
MOCK_SENSORS = {
    1025: {"sensorId": 1025, "name": "plug_0", "value": "95.3", "status": "On", "locationName": "Working area", "sensorTypeName": "Power"},
    1035: {"sensorId": 1035, "name": "plug_1", "value": "0.0", "status": "Off", "locationName": "Robot Corner", "sensorTypeName": "Power"},
    1037: {"sensorId": 1037, "name": "plug_2", "value": "45.2", "status": "On", "locationName": "Kaspar Room", "sensorTypeName": "Power"},
    1039: {"sensorId": 1039, "name": "plug_3", "value": "0.0", "status": "Off", "locationName": "Entrance", "sensorTypeName": "Power"},
    1041: {"sensorId": 1041, "name": "plug_4", "value": "120.5", "status": "On", "locationName": "Working area", "sensorTypeName": "Power"},
    
    1028: {"sensorId": 1028, "name": "motion_0_temperature", "value": "22.5", "status": "Active", "locationName": "Working area", "sensorTypeName": "Temperature"},
    1060: {"sensorId": 1060, "name": "motion_1_temperature", "value": "21.8", "status": "Active", "locationName": "Entrance", "sensorTypeName": "Temperature"},
    1066: {"sensorId": 1066, "name": "motion_2_temperature", "value": "23.2", "status": "Active", "locationName": "Observation Room", "sensorTypeName": "Temperature"},
    1072: {"sensorId": 1072, "name": "motion_3_temperature", "value": "24.1", "status": "Active", "locationName": "Kaspar Room", "sensorTypeName": "Temperature"},
    1078: {"sensorId": 1078, "name": "motion_4_temperature", "value": "23.9", "status": "Active", "locationName": "Robot Corner", "sensorTypeName": "Temperature"},
    
    1029: {"sensorId": 1029, "name": "motion_0_movement", "value": "1", "status": "Active", "locationName": "Working area", "sensorTypeName": "Motion"},
    1061: {"sensorId": 1061, "name": "motion_1_movement", "value": "0", "status": "Inactive", "locationName": "Entrance", "sensorTypeName": "Motion"},
    1067: {"sensorId": 1067, "name": "motion_2_movement", "value": "0", "status": "Inactive", "locationName": "Observation Room", "sensorTypeName": "Motion"},
    1073: {"sensorId": 1073, "name": "motion_3_movement", "value": "1", "status": "Active", "locationName": "Kaspar Room", "sensorTypeName": "Motion"},
    1079: {"sensorId": 1079, "name": "motion_4_movement", "value": "0", "status": "Inactive", "locationName": "Robot Corner", "sensorTypeName": "Motion"},
    
    1022: {"sensorId": 1022, "name": "door_0", "value": "0", "status": "Closed", "locationName": "Working area", "sensorTypeName": "Door"},
    1043: {"sensorId": 1043, "name": "door_1", "value": "1", "status": "Open", "locationName": "Robot Corner", "sensorTypeName": "Door"},
    1047: {"sensorId": 1047, "name": "door_2", "value": "0", "status": "Closed", "locationName": "Kaspar Room", "sensorTypeName": "Door"},
    1051: {"sensorId": 1051, "name": "door_3", "value": "0", "status": "Closed", "locationName": "Entrance", "sensorTypeName": "Door"},
    1055: {"sensorId": 1055, "name": "door_4", "value": "1", "status": "Open", "locationName": "Observation Room", "sensorTypeName": "Door"},
}

# Plug states
PLUG_STATES = {
    25: True,   # plug_0 - On
    35: False,  # plug_1 - Off
    37: True,   # plug_2 - On
    39: False,  # plug_3 - Off
    41: True,   # plug_4 - On
}


class MockSensors:
    """Mock sensor data access class."""
    
    def __init__(self):
        self._sensors = dict(MOCK_SENSORS)
        # Add small random variations
        for sid, sensor in self._sensors.items():
            if 'temperature' in sensor['name']:
                base_temp = float(sensor['value'])
                variation = random.uniform(-0.5, 0.5)
                self._sensors[sid]['value'] = f"{base_temp + variation:.1f}"
    
    def findSensors(self) -> List[Dict]:
        """Get all sensors."""
        return list(self._sensors.values())
    
    def getSensor(self, sensor_id: int) -> Optional[Dict]:
        """Get a single sensor by ID."""
        return self._sensors.get(sensor_id)
    
    def getSensorByName(self, name: str) -> Optional[Dict]:
        """Get sensor by name."""
        for sensor in self._sensors.values():
            if sensor['name'] == name:
                return sensor
        return None


class MockZWaveHomeActuator:
    """Mock actuator for controlling devices."""
    
    def __init__(self):
        self._states = dict(PLUG_STATES)
    
    def setValue(self, device_id: int, action: str, value: int) -> Dict:
        """Set device value."""
        if device_id not in self._states:
            return {"success": False, "error": f"Device {device_id} not found"}
        
        if action == "turnOn":
            self._states[device_id] = True
            return {"success": True, "state": "On"}
        elif action == "turnOff":
            self._states[device_id] = False
            return {"success": True, "state": "Off"}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def getState(self, device_id: int) -> Optional[bool]:
        """Get device state."""
        return self._states.get(device_id)


class MockZWaveHomeSensor:
    """Mock sensor API for history queries."""
    
    def getDevices(self) -> List[Dict]:
        """Get all devices."""
        return list(MOCK_SENSORS.values())
    
    def getHistory(self, duration_ms: int) -> List[Dict]:
        """Get history events (mock data)."""
        now = datetime.now()
        return [
            {"timestamp": now.isoformat(), "device": "motion_0", "event": "motion_detected"},
            {"timestamp": now.isoformat(), "device": "door_1", "event": "opened"},
        ]


# Alias for compatibility
Sensors = MockSensors
ZWaveHomeActuator = MockZWaveHomeActuator
ZWaveHomeSensor = MockZWaveHomeSensor


if __name__ == "__main__":
    # Test mock sensors
    sensors = Sensors()
    
    print("All sensors:")
    for s in sensors.findSensors():
        print(f"  {s['name']}: {s['value']} ({s['status']}) - {s['locationName']}")
    
    print("\nSingle sensor test:")
    sensor = sensors.getSensor(1078)
    print(f"  Robot Corner temp: {sensor['value']}°C")
    
    print("\nActuator test:")
    actuator = ZWaveHomeActuator()
    result = actuator.setValue(35, "turnOn", 1)
    print(f"  Turn on plug_1: {result}")
