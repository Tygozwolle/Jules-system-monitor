## 2024-05-23 - MQTT TLS Security Gap
**Vulnerability:** The MQTT client in `system_monitor` does not support TLS, transmitting data and credentials in plaintext.
**Learning:** Containerized applications often default to insecure communication protocols (like plain MQTT) assuming a secure local network, but this breaks the "defense in depth" principle.
**Prevention:** Always implement TLS configuration options in network clients, even for internal tools, to allow secure deployment in zero-trust environments.
