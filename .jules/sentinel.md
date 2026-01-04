## 2024-05-23 - MQTT TLS Security Gap
**Vulnerability:** The `MQTTClient` implementation relied on default insecure settings (plain TCP) and lacked any mechanism to configure TLS/SSL, exposing credentials and data to interception.
**Learning:** Default libraries often prioritize ease of use (no TLS) over security. Even in internal tools, unencrypted protocols are a significant risk.
**Prevention:** Always check if a network client supports TLS and ensure configuration hooks (like environment variables) are present to enable it. Fail secure by defaulting to secure options or explicitly requiring configuration.
