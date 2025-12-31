import unittest
from unittest.mock import patch, MagicMock
from system_monitor.mqtt_client import MQTTClient

class TestMQTTTLS(unittest.TestCase):
    @patch('system_monitor.mqtt_client.mqtt.Client')
    def test_tls_configuration(self, mock_client_cls):
        # Setup mock
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Test TLS Config
        tls_config = {
            'ca_certs': '/path/to/ca.crt',
            'certfile': '/path/to/client.crt',
            'keyfile': '/path/to/client.key',
            'insecure': True
        }

        MQTTClient('localhost', 8883, 'user', 'pass', 'test_device', tls_config)

        # Verify tls_set was called with correct args
        mock_client.tls_set.assert_called_with(
            ca_certs='/path/to/ca.crt',
            certfile='/path/to/client.crt',
            keyfile='/path/to/client.key'
        )

        # Verify tls_insecure_set was called
        mock_client.tls_insecure_set.assert_called_with(True)

    @patch('system_monitor.mqtt_client.mqtt.Client')
    def test_no_tls_configuration(self, mock_client_cls):
        # Setup mock
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        MQTTClient('localhost', 1883, 'user', 'pass', 'test_device', None)

        # Verify tls_set was NOT called
        mock_client.tls_set.assert_not_called()
