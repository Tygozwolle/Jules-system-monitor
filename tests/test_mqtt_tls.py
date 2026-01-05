import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure system_monitor is in path
sys.path.append(os.path.join(os.getcwd(), 'system_monitor'))

from mqtt_client import MQTTClient

class TestMQTTClientTLS(unittest.TestCase):
    @patch('mqtt_client.mqtt.Client')
    def test_tls_configuration(self, mock_client_cls):
        # Setup mock
        mock_instance = mock_client_cls.return_value

        # Test case: TLS enabled
        client = MQTTClient(
            broker="localhost",
            port=8883,
            username="user",
            password="password",
            device_name="test_device",
            use_tls=True,
            ca_certs="/path/to/ca.crt",
            certfile="/path/to/client.crt",
            keyfile="/path/to/client.key",
            tls_insecure=False
        )

        # Verify tls_set was called with correct arguments
        mock_instance.tls_set.assert_called_once_with(
            ca_certs="/path/to/ca.crt",
            certfile="/path/to/client.crt",
            keyfile="/path/to/client.key"
        )

        # Verify tls_insecure_set was called
        mock_instance.tls_insecure_set.assert_called_once_with(False)

    @patch('mqtt_client.mqtt.Client')
    def test_tls_disabled(self, mock_client_cls):
        # Setup mock
        mock_instance = mock_client_cls.return_value

        # Test case: TLS disabled (default behavior or explicit False)
        client = MQTTClient(
            broker="localhost",
            port=1883,
            username="user",
            password="password",
            device_name="test_device",
            use_tls=False
        )

        # Verify tls_set was NOT called
        mock_instance.tls_set.assert_not_called()

if __name__ == '__main__':
    unittest.main()
