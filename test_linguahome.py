#!/usr/bin/env python3
"""
LinguaHome Test Script

Tests the system without requiring LLM API access.
"""

import sys
from pathlib import Path


def test_imports():
    """Test all imports."""
    print("=" * 60)
    print("🧪 Testing Imports")
    print("=" * 60)
    
    from __init__ import __version__
    print(f"✅ LinguaHome version: {__version__}")
    
    from config import DEVICE_MAP, ROOMS
    print(f"✅ Config: {len(DEVICE_MAP)} devices, {len(ROOMS)} rooms")
    
    from agent.memory import MemoryStore
    print("✅ MemoryStore")
    
    from agent.context import ContextBuilder, SYSTEM_PROMPT
    print(f"✅ ContextBuilder (System Prompt: {len(SYSTEM_PROMPT)} chars)")
    
    from agent.code_executor import CodeExecutor
    print("✅ CodeExecutor")
    
    from mock_sensors import Sensors, ZWaveHomeActuator
    print("✅ Mock Sensors")
    
    return True


def test_code_executor():
    """Test the code executor with mock sensors."""
    print("\n" + "=" * 60)
    print("🧪 Testing Code Executor")
    print("=" * 60)
    
    from agent.code_executor import CodeExecutor
    
    executor = CodeExecutor(safe_mode=True)
    
    tests = [
        {
            "name": "Simple print",
            "code": 'print("Hello, LinguaHome!")',
            "expected": "Hello, LinguaHome!"
        },
        {
            "name": "Temperature query",
            "code": '''
sensors = Sensors()
sensor = sensors.getSensor(1078)
print(f"Temperature: {sensor['value']}°C")
''',
            "expected": "°C"
        },
        {
            "name": "All sensors count",
            "code": '''
sensors = Sensors()
all_sensors = sensors.findSensors()
print(f"Found {len(all_sensors)} sensors")
''',
            "expected": "sensors"
        },
        {
            "name": "Actuator control",
            "code": '''
actuator = ZWaveHomeActuator()
result = actuator.setValue(35, "turnOn", 1)
print(f"Result: {result}")
''',
            "expected": "success"
        },
    ]
    
    passed = 0
    for test in tests:
        success, stdout, stderr = executor.execute(test["code"])
        if success and test["expected"] in stdout:
            print(f"✅ {test['name']}: {stdout.strip()[:50]}")
            passed += 1
        else:
            print(f"❌ {test['name']}: {stderr[:100] if stderr else 'No output'}")
    
    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)


def test_memory():
    """Test the memory system."""
    print("\n" + "=" * 60)
    print("🧪 Testing Memory System")
    print("=" * 60)
    
    import tempfile
    from agent.memory import MemoryStore
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        memory = MemoryStore(workspace)
        
        # Test daily memory
        memory.append_today("Test entry 1")
        memory.append_today("Test entry 2")
        today_content = memory.read_today()
        assert "Test entry 1" in today_content
        assert "Test entry 2" in today_content
        print("✅ Daily memory works")
        
        # Test long-term memory
        memory.remember_preference("User prefers 22°C")
        long_term = memory.read_long_term()
        assert "22°C" in long_term
        print("✅ Long-term memory works")
        
        # Test sensor event logging
        memory.remember_sensor_event("temp_sensor", "23.5", "Active")
        today = memory.read_today()
        assert "temp_sensor" in today
        print("✅ Sensor event logging works")
        
        # Test context building
        context = memory.get_memory_context()
        assert len(context) > 0
        print("✅ Memory context building works")
    
    return True


def test_context_builder():
    """Test the context builder."""
    print("\n" + "=" * 60)
    print("🧪 Testing Context Builder")
    print("=" * 60)
    
    from agent.context import ContextBuilder, SYSTEM_PROMPT
    
    builder = ContextBuilder()
    
    # Test system prompt
    prompt = builder.build_system_prompt()
    assert "LinguaHome" in prompt
    assert "Sensors" in prompt
    assert "ZWaveHomeActuator" in prompt
    print(f"✅ System prompt: {len(prompt)} characters")
    
    # Test user prompt
    user_prompt = builder.build_user_prompt("Turn off the lights")
    assert "Turn off the lights" in user_prompt
    print("✅ User prompt builder works")
    
    # Check device mapping in prompt
    assert "Robot Corner" in prompt
    assert "1078" in prompt
    print("✅ Device mapping included in prompt")
    
    return True


def test_security():
    """Test code execution security."""
    print("\n" + "=" * 60)
    print("🧪 Testing Security")
    print("=" * 60)
    
    from agent.code_executor import CodeExecutor
    
    executor = CodeExecutor(safe_mode=True)
    
    dangerous_codes = [
        ("import os", "import os\nos.system('ls')"),
        ("import subprocess", "import subprocess\nsubprocess.run(['ls'])"),
        ("open()", "open('/etc/passwd').read()"),
        ("eval()", "eval('1+1')"),
        ("exec()", "exec('print(1)')"),
    ]
    
    blocked = 0
    for name, code in dangerous_codes:
        is_safe, error = executor.validate_code(code)
        if not is_safe:
            print(f"✅ Blocked: {name}")
            blocked += 1
        else:
            print(f"❌ NOT blocked: {name}")
    
    print(f"\nBlocked: {blocked}/{len(dangerous_codes)}")
    return blocked == len(dangerous_codes)


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🏠 LinguaHome Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Code Executor", test_code_executor()))
    results.append(("Memory System", test_memory()))
    results.append(("Context Builder", test_context_builder()))
    results.append(("Security", test_security()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n{'✅' if passed == total else '❌'} Overall: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
