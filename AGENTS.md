# Agent Instructions for System Monitor

This repository contains a Python-based system monitor designed to run in a Docker container and publish metrics to Home Assistant via MQTT.

## Project Structure
- `system_monitor/`: Source code.
  - `monitor.py`: Core logic for gathering system and hardware stats.
  - `mqtt_client.py`: Handles MQTT connection and Home Assistant Auto Discovery.
  - `main.py`: Entry point and main loop.
- `tests/`: Unit tests.
- `Dockerfile`: Container configuration.

## Development Guidelines

### 1. Hardware Abstraction
This project runs in environments where hardware access might be limited (CI/CD) or specific (Docker).
- **Do not assume hardware exists.** Always wrap sensor reads in `try...except` blocks.
- **Sysfs Paths:** We heavily rely on `/sys` filesystem (e.g., `/sys/class/drm`, `/sys/class/powercap`). When testing, these must be mocked.
- **GPU Libraries:** `pynvml` is used for NVIDIA. It is imported conditionally to avoid crashes on non-NVIDIA systems.

### 2. Testing
- Run tests using `python3 -m pytest tests/test_dry_run.py`.
- **Mocks are mandatory.** Since we cannot access real hardware sensors in the test environment, you must use `unittest.mock` to simulate `psutil` returns and file system reads (`builtins.open`, `os.path.exists`, `glob.glob`).

### 3. Home Assistant Integration
- **Auto Discovery:** We use the HA MQTT Discovery protocol.
- **Topic Structure:** `homeassistant/sensor/<device_name>/<sensor_id>/config`
- **State Updates:** We publish a single JSON payload to the state topic to minimize MQTT traffic.

### 4. Docker Environment
- The container is designed to run with `--privileged` or specific volume mounts (`/sys:/sys:ro`).
- Dependencies like `gcc` and `python3-dev` are needed in the Dockerfile for building `psutil`.

## Code Style
- Use standard Python conventions (PEP 8).
- Keep dependencies minimal to ensure the container remains lightweight.
