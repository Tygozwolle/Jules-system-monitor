# System Monitor for Home Assistant

A lightweight, Dockerized system monitor that publishes system performance metrics to Home Assistant via MQTT. It supports Auto Discovery, so no manual YAML configuration is needed in Home Assistant.

**Repository:** [Tygozwolle/Jules-system-monitor](https://github.com/Tygozwolle/Jules-system-monitor)


## Features

*   **Real-time Monitoring:**
    *   **CPU:** Usage (Total & Per Core), Frequency, Load Average, Temperature.
    *   **Memory:** RAM Usage (Total, Used, Free, %), Swap Usage.
    *   **Disk:** Root Partition Usage.
    *   **Network:** Bytes Sent/Received.
    *   **System:** Uptime, Boot Time.
*   **Power Monitoring:**
    *   **CPU Power (x86):** Real-time power consumption in Watts (via RAPL).
    *   **GPU Power:** Supported for NVIDIA (NVML) and AMD (hwmon).
*   **GPU Support:**
    *   **NVIDIA:** Usage, Memory, Temp, Power (requires `--gpus all` or `nvidia-container-runtime`).
    *   **AMD:** Usage, Temp, Power (requires mapped `/sys/class/drm` and `/sys/class/hwmon`).
    *   **Intel:** GPU Frequency (requires mapped `/sys/class/drm`).
*   **Home Assistant Integration:** Fully automated MQTT Discovery.


## Prerequisites

*   Docker
*   MQTT Broker (e.g., Mosquitto, EMQX)


## Quick Start (Docker)

```bash
docker run -d \
  --name system-monitor \
  --privileged \
  --net=host \
  -v /sys:/sys:ro \
  -e MQTT_BROKER="192.168.1.100" \
  -e MQTT_PORT=1883 \
  -e MQTT_USER="homeassistant" \
  -e MQTT_PASSWORD="password" \
  -e DEVICE_NAME="My Server" \
  -e UPDATE_INTERVAL=10 \
  system-monitor
```

*Note: `--net=host` is recommended for easiest network discovery, but not strictly required if the MQTT broker is reachable. `--privileged` and `-v /sys:/sys:ro` are **required** for reading hardware sensors (Power, GPU).*


## Configuration (Environment Variables)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `MQTT_BROKER` | `localhost` | IP address or hostname of your MQTT Broker. |
| `MQTT_PORT` | `1883` | Port of the MQTT Broker. |
| `MQTT_USER` | `None` | MQTT Username (optional). |
| `MQTT_PASSWORD` | `None` | MQTT Password (optional). |
| `UPDATE_INTERVAL`| `10` | Time in seconds between updates. |
| `DEVICE_NAME` | Hostname | Name of the device as it will appear in Home Assistant. |


## GPU Support Details


### NVIDIA

Requires the **NVIDIA Container Toolkit** installed on the host. Run the container with `--gpus all`.


### AMD / Intel

Requires mapping the system directory: `-v /sys:/sys:ro`. The container monitors `/sys/class/drm` and `/sys/class/hwmon` to find stats.


## Development


### Running Locally

1. Install dependencies: `pip install -r system_monitor/requirements.txt`
2. Run: `python system_monitor/main.py`


### Testing

Run the test suite:
```bash
python3 -m pytest tests/test_dry_run.py
```
