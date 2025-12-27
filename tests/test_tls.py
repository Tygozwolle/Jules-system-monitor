import sys
import unittest
from unittest.mock import MagicMock
import os

# Mock dependencies
sys.modules['psutil'] = MagicMock()
sys.modules['paho'] = MagicMock()
sys.modules['paho.mqtt'] = MagicMock()
sys.modules['paho.mqtt.client'] = MagicMock()
sys.modules['pynvml'] = MagicMock()

sys.path.append(os.path.join(os.getcwd(), 'system_monitor'))

from mqtt_client import MQTTClient

class TestMQTTTLS(unittest.TestCase):
    def test_tls_configuration_enabled(self):
        """Verify that TLS is configured when requested."""
        client = MQTTClient(
            "localhost", 8883, None, None, "TestDevice",
            use_tls=True,
            ca_certs="/path/to/ca.crt",
            certfile="/path/to/client.crt",
            keyfile="/path/to/client.key",
            insecure=True
        )

        # Verify tls_set was called with correct args
        client.client.tls_set.assert_called_with(
            ca_certs="/path/to/ca.crt",
            certfile="/path/to/client.crt",
            keyfile="/path/to/client.key"
        )

        # Verify insecure set
        client.client.tls_insecure_set.assert_called_with(True)

    def test_tls_configuration_defaults(self):
        """Verify defaults (no TLS) work as expected."""
        client = MQTTClient("localhost", 1883, None, None, "TestDevice")

        client.client.tls_set.assert_not_called()
        client.client.tls_insecure_set.assert_not_called()

if __name__ == '__main__':
    unittest.main()
