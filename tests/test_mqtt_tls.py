import unittest
from unittest.mock import MagicMock, patch
from system_monitor.mqtt_client import MQTTClient

class TestMQTTTLS(unittest.TestCase):
    @patch('system_monitor.mqtt_client.mqtt.Client')
    def test_tls_configuration(self, mock_mqtt_client_cls):
        # Setup mock
        mock_client_instance = MagicMock()
        mock_mqtt_client_cls.return_value = mock_client_instance

        # Test Case 1: No TLS
        MQTTClient("localhost", 1883, "user", "pass", "device")
        mock_client_instance.tls_set.assert_not_called()

        # Test Case 2: TLS Enabled, defaults
        MQTTClient("localhost", 8883, "user", "pass", "device", use_tls=True)
        mock_client_instance.tls_set.assert_called_with(ca_certs=None, certfile=None, keyfile=None)
        mock_client_instance.tls_insecure_set.assert_not_called()

        # Test Case 3: TLS Enabled with params
        MQTTClient("localhost", 8883, "user", "pass", "device",
                   use_tls=True, ca_certs="/path/to/ca", certfile="/path/to/cert", keyfile="/path/to/key", tls_insecure=True)

        mock_client_instance.tls_set.assert_called_with(ca_certs="/path/to/ca", certfile="/path/to/cert", keyfile="/path/to/key")
        mock_client_instance.tls_insecure_set.assert_called_with(True)

if __name__ == '__main__':
    unittest.main()
