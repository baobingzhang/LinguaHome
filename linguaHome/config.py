"""
LinguaHome Configuration
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FibaroConfig:
    """Fibaro Home Center 3 configuration."""
    address: str = field(default_factory=lambda: os.environ.get('HC_ADDRESS', '10.0.1.70'))
    user: str = field(default_factory=lambda: os.environ.get('HC_USER', 'admin'))
    password: str = field(default_factory=lambda: os.environ.get('HC_PASSWORD', 'admin'))


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    model: str = field(default_factory=lambda: os.environ.get('LINGUAHOME_MODEL', 'gpt-4o'))
    api_key: Optional[str] = field(default_factory=lambda: os.environ.get('OPENAI_API_KEY'))
    temperature: float = 0.1
    max_tokens: int = 4096


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    token: str = field(default_factory=lambda: os.environ.get('TELEGRAM_BOT_TOKEN', ''))
    allowed_users: list = field(default_factory=list)


@dataclass
class LinguaHomeConfig:
    """Main configuration."""
    fibaro: FibaroConfig = field(default_factory=FibaroConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    
    # Paths
    workspace: Path = field(default_factory=lambda: Path.cwd())
    skills_dir: Path = field(default_factory=lambda: Path(__file__).parent / "skills")
    memory_dir: Path = field(default_factory=lambda: Path.cwd() / "memory")
    
    # Code execution
    code_timeout: int = 30  # seconds
    safe_mode: bool = True  # Only allow whitelisted imports


# Device mapping for the testbed
DEVICE_MAP = {
    # Plugs (controllable)
    "plug_0": {"sensor_id": 1025, "device_id": 25, "room": "Working area", "type": "plug"},
    "plug_1": {"sensor_id": 1035, "device_id": 35, "room": "Robot Corner", "type": "plug"},
    "plug_2": {"sensor_id": 1037, "device_id": 37, "room": "Kaspar Room", "type": "plug"},
    "plug_3": {"sensor_id": 1039, "device_id": 39, "room": "Entrance", "type": "plug"},
    "plug_4": {"sensor_id": 1041, "device_id": 41, "room": "Working area", "type": "plug"},
    
    # Temperature sensors
    "motion_0_temperature": {"sensor_id": 1028, "device_id": 28, "room": "Working area", "type": "temperature"},
    "motion_1_temperature": {"sensor_id": 1060, "device_id": 60, "room": "Entrance", "type": "temperature"},
    "motion_2_temperature": {"sensor_id": 1066, "device_id": 66, "room": "Observation Room", "type": "temperature"},
    "motion_3_temperature": {"sensor_id": 1072, "device_id": 72, "room": "Kaspar Room", "type": "temperature"},
    "motion_4_temperature": {"sensor_id": 1078, "device_id": 78, "room": "Robot Corner", "type": "temperature"},
    
    # Motion sensors
    "motion_0_movement": {"sensor_id": 1029, "device_id": 28, "room": "Working area", "type": "motion"},
    "motion_1_movement": {"sensor_id": 1061, "device_id": 60, "room": "Entrance", "type": "motion"},
    "motion_2_movement": {"sensor_id": 1067, "device_id": 66, "room": "Observation Room", "type": "motion"},
    "motion_3_movement": {"sensor_id": 1073, "device_id": 72, "room": "Kaspar Room", "type": "motion"},
    "motion_4_movement": {"sensor_id": 1079, "device_id": 78, "room": "Robot Corner", "type": "motion"},
    
    # Door sensors
    "door_0": {"sensor_id": 1022, "device_id": 22, "room": "Working area", "type": "door"},
    "door_1": {"sensor_id": 1043, "device_id": 43, "room": "Robot Corner", "type": "door"},
    "door_2": {"sensor_id": 1047, "device_id": 47, "room": "Kaspar Room", "type": "door"},
    "door_3": {"sensor_id": 1051, "device_id": 51, "room": "Entrance", "type": "door"},
    "door_4": {"sensor_id": 1055, "device_id": 55, "room": "Observation Room", "type": "door"},
}

# Room list
ROOMS = ["Working area", "Robot Corner", "Kaspar Room", "Entrance", "Observation Room"]

# Controllable devices
CONTROLLABLE_DEVICES = {k: v for k, v in DEVICE_MAP.items() if v["type"] == "plug"}
