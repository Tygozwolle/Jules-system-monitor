import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add system_monitor to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../system_monitor'))

# Patch mqtt_client.mqtt before importing the module
with patch('paho.mqtt.client.Client') as mock_mqtt_class:
    from mqtt_client import MQTTClient

class TestMQTTTLS(unittest.TestCase):

    @patch('mqtt_client.mqtt.Client')
    def test_tls_enabled_no_insecure(self, mock_client_class):
        mock_client_instance = mock_client_class.return_value

        MQTTClient('localhost', 8883, 'user', 'pass', 'test_device',
                   use_tls=True, ca_certs='/path/to/ca.crt')

        mock_client_instance.tls_set.assert_called_with(ca_certs='/path/to/ca.crt', certfile=None, keyfile=None)
        mock_client_instance.tls_insecure_set.assert_not_called()

    @patch('mqtt_client.mqtt.Client')
    def test_tls_enabled_with_insecure(self, mock_client_class):
        mock_client_instance = mock_client_class.return_value

        MQTTClient('localhost', 8883, 'user', 'pass', 'test_device',
                   use_tls=True, ca_certs='/path/to/ca.crt', tls_insecure=True)

        mock_client_instance.tls_set.assert_called_with(ca_certs='/path/to/ca.crt', certfile=None, keyfile=None)
        mock_client_instance.tls_insecure_set.assert_called_with(True)

    @patch('mqtt_client.mqtt.Client')
    def test_tls_disabled(self, mock_client_class):
        mock_client_instance = mock_client_class.return_value

        MQTTClient('localhost', 1883, 'user', 'pass', 'test_device',
                   use_tls=False)

        mock_client_instance.tls_set.assert_not_called()
        mock_client_instance.tls_insecure_set.assert_not_called()

if __name__ == '__main__':
    unittest.main()
