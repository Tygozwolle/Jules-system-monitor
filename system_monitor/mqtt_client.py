import json
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, username, password, device_name, tls_config=None):
        self.client = mqtt.Client()

        if tls_config:
            self.client.tls_set(
                ca_certs=tls_config.get('ca_certs'),
                certfile=tls_config.get('certfile'),
                keyfile=tls_config.get('keyfile')
            )
            if tls_config.get('insecure', False):
                self.client.tls_insecure_set(True)

        if username and password:
            self.client.username_pw_set(username, password)
        self.client.connect(broker, port)
        self.client.loop_start()
        self.device_name = device_name
        self.discovery_prefix = "homeassistant"
        
        # Sanitize device name for IDs
        self.device_id = device_name.lower().replace(" ", "_")

    def publish_discovery(self, sensor_data):
        """
        Publishes MQTT Auto Discovery config for each sensor key found in sensor_data.
        """
        device_info = {
            "identifiers": [self.device_id],
            "name": self.device_name,
            "manufacturer": "Custom System Monitor",
            "model": "Docker Monitor",
            "sw_version": "1.0"
        }

        for key, value in sensor_data.items():
            # Infer sensor type/unit based on key name
            unit_of_measurement = None
            device_class = None
            state_class = "measurement" # Default to measurement
            
            if "_percent" in key:
                unit_of_measurement = "%"
                # If usage, maybe not a specific device class, but fine
            elif "_mb" in key:
                unit_of_measurement = "MB"
                device_class = "data_size"
            elif "_gb" in key:
                unit_of_measurement = "GB"
                device_class = "data_size"
            elif "_c" in key or "_temp" in key:
                unit_of_measurement = "°C"
                device_class = "temperature"
            elif "_watts" in key:
                unit_of_measurement = "W"
                device_class = "power"
            elif "_freq" in key:
                unit_of_measurement = "MHz"
                device_class = "frequency"
            elif "uptime" in key:
                unit_of_measurement = "s"
                device_class = "duration"
                state_class = "total_increasing"

            unique_id = f"{self.device_id}_{key}"
            config_topic = f"{self.discovery_prefix}/sensor/{self.device_id}/{key}/config"
            
            payload = {
                "name": f"{self.device_name} {key.replace('_', ' ').title()}",
                "state_topic": f"{self.discovery_prefix}/sensor/{self.device_id}/state",
                "value_template": f"{{{{ value_json.{key} }}}}",
                "unique_id": unique_id,
                "device": device_info
            }
            
            if unit_of_measurement:
                payload["unit_of_measurement"] = unit_of_measurement
            if device_class:
                payload["device_class"] = device_class
            if state_class:
                payload["state_class"] = state_class

            self.client.publish(config_topic, json.dumps(payload), retain=True)

    def publish_update(self, sensor_data):
        """
        Publishes the current state of all sensors to a single JSON topic.
        """
        state_topic = f"{self.discovery_prefix}/sensor/{self.device_id}/state"
        self.client.publish(state_topic, json.dumps(sensor_data))
