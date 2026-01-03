import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure we can import system_monitor modules
# This path append is needed because the code expects to be run from system_monitor/ usually,
# or we just need to add system_monitor to path.
if 'system_monitor' not in sys.path:
    sys.path.append(os.path.join(os.getcwd(), 'system_monitor'))

from mqtt_client import MQTTClient

class TestMQTTClientTLS(unittest.TestCase):
    def test_tls_configuration(self):
        # Patch the mqtt object inside mqtt_client module
        with patch('mqtt_client.mqtt') as mock_mqtt_module:
            mock_client_instance = MagicMock()
            mock_mqtt_module.Client.return_value = mock_client_instance

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
                tls_insecure=True
            )

            # Verify tls_set was called with correct args
            mock_client_instance.tls_set.assert_called_with(
                ca_certs="/path/to/ca.crt",
                certfile="/path/to/client.crt",
                keyfile="/path/to/client.key"
            )

            # Verify tls_insecure_set was called
            mock_client_instance.tls_insecure_set.assert_called_with(True)

    def test_no_tls_configuration(self):
        # Patch the mqtt object inside mqtt_client module
        with patch('mqtt_client.mqtt') as mock_mqtt_module:
            mock_client_instance = MagicMock()
            mock_mqtt_module.Client.return_value = mock_client_instance

            # Test case: TLS disabled (default)
            client = MQTTClient(
                broker="localhost",
                port=1883,
                username="user",
                password="password",
                device_name="test_device",
                use_tls=False
            )

            # Verify tls_set was NOT called
            mock_client_instance.tls_set.assert_not_called()
            mock_client_instance.tls_insecure_set.assert_not_called()

if __name__ == '__main__':
    unittest.main()
