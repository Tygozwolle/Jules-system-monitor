import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
import time

# Mock dependencies before importing local modules
sys.modules['psutil'] = MagicMock()
sys.modules['paho'] = MagicMock()
sys.modules['paho.mqtt'] = MagicMock()
sys.modules['paho.mqtt.client'] = MagicMock()
sys.modules['pynvml'] = MagicMock()

# Now we can import our code
sys.path.append(os.path.join(os.getcwd(), 'system_monitor'))

from monitor import SystemMonitor
from mqtt_client import MQTTClient

class TestSystemMonitor(unittest.TestCase):
    @patch('monitor.platform')
    @patch('monitor.psutil')
    def test_get_stats_structure(self, mock_psutil, mock_platform):
        # Setup Mocks
        mock_platform.system.return_value = 'Linux'
        mock_platform.machine.return_value = 'x86_64'
        
        mock_psutil.cpu_percent.side_effect = [10.5, [10.5, 10.5]]
        mock_psutil.virtual_memory.return_value.total = 8 * 1024**3
        mock_psutil.virtual_memory.return_value.used = 4 * 1024**3
        mock_psutil.virtual_memory.return_value.free = 4 * 1024**3
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.swap_memory.return_value.percent = 0.0
        mock_psutil.disk_usage.return_value.percent = 40.0
        mock_psutil.disk_usage.return_value.free = 100 * 1024**3
        mock_psutil.net_io_counters.return_value.bytes_sent = 1024
        mock_psutil.net_io_counters.return_value.bytes_recv = 2048
        mock_psutil.boot_time.return_value = 1600000000

        monitor = SystemMonitor()
        stats = monitor.get_stats()

        self.assertIn('cpu_usage_percent', stats)
        self.assertIn('memory_used_mb', stats)
        self.assertIn('disk_root_usage_percent', stats)
        self.assertIn('net_bytes_sent_mb', stats)
        
        # Verify default values
        self.assertEqual(stats['cpu_usage_percent'], 10.5)

    @patch('monitor.glob.glob')
    @patch('monitor.os.path.exists')
    @patch('monitor.os.path.join')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('monitor.platform')
    def test_amd_gpu_detection(self, mock_platform, mock_open_file, mock_join, mock_exists, mock_glob):
        mock_platform.system.return_value = 'Linux'
        mock_platform.machine.return_value = 'x86_64'
        
        # Mock glob to find one card
        mock_glob.side_effect = lambda x: ['/sys/class/drm/card0'] if 'card' in x else []

        mock_exists.return_value = True
        mock_join.side_effect = lambda *args: "/".join(args)

        # Mock file reads. 
        # Logic: 
        # 1. Check vendor: read vendor -> "0x1002" (Is AMD)
        # 2. AMD Usage: read "50"
        # 3. AMD Temp: read "35000" (35C)
        # 4. AMD Power: read "50000000" (50W) from power1_average
        
        mock_open_file.side_effect = [
            unittest.mock.mock_open(read_data="0x1002").return_value, # Vendor Check (AMD)
            unittest.mock.mock_open(read_data="50").return_value,     # Usage
            unittest.mock.mock_open(read_data="35000").return_value,  # Temp
            unittest.mock.mock_open(read_data="50000000").return_value, # Power
            unittest.mock.mock_open(read_data="0x1002").return_value, # Extra for safety
        ]

        monitor = SystemMonitor()
        stats = monitor.get_stats()
        
        self.assertIn('gpu_amd_card0_usage_percent', stats)
        self.assertEqual(stats['gpu_amd_card0_usage_percent'], 50)
        self.assertIn('gpu_amd_card0_power_watts', stats)
        self.assertEqual(stats['gpu_amd_card0_power_watts'], 50.0)

    @patch('monitor.glob.glob')
    @patch('monitor.os.path.exists')
    @patch('monitor.os.path.join')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('monitor.platform')
    def test_cpu_power_calculation(self, mock_platform, mock_open_file, mock_join, mock_exists, mock_glob):
        mock_platform.system.return_value = 'Linux'
        mock_platform.machine.return_value = 'x86_64'
        
        # Mock rapl paths
        mock_exists.return_value = True
        mock_glob.side_effect = [
            ['/sys/class/drm/card0'], # drm card glob (first call)
            ['/sys/class/powercap/intel-rapl/intel-rapl:0'], # rapl packages (first call)
            ['/sys/class/drm/card0'], # drm card glob (second call)
            ['/sys/class/powercap/intel-rapl/intel-rapl:0'], # rapl packages (second call)
            [], [] # extra calls
        ]
        mock_join.side_effect = lambda *args: "/".join(args)

        # Monitor Logic calls CPU stats then GPU stats.
        # We want to test CPU stats.
        # CPU Stats Logic:
        # Glob rapl packages. For each: read name, read energy_uj.
        
        # First call:
        # Read name: "package-0"
        # Read energy: "1000000" (1J)
        
        # Second call:
        # Read name: "package-0"
        # Read energy: "2000000" (2J) -> Delta 1J in X seconds
        
        # We need to interleave these returns with the GPU logic calls or ensure GPU logic doesn't crash/consume too many side effects.
        # To simplify, let's assume GPU returns nothing or fails gracefully.
        # But we need to handle the vendor/file reads if GPU logic runs.
        # Easier: Mock platform such that GPU logic is skipped or make glob return empty for drm.
        
        # Re-setup mocks strictly for this test to avoid complexity
        mock_glob.side_effect = lambda x: ['/sys/class/powercap/intel-rapl/intel-rapl:0'] if 'intel-rapl' in x else []
        
        monitor = SystemMonitor()
        
        # First Call
        mock_open_file.side_effect = [
            unittest.mock.mock_open(read_data="package-0").return_value,
            unittest.mock.mock_open(read_data="1000000").return_value,
        ]
        monitor.get_stats()
        
        # Wait a bit to ensure non-zero delta
        time.sleep(0.1)
        
        # Second Call
        mock_open_file.side_effect = [
            unittest.mock.mock_open(read_data="package-0").return_value,
            unittest.mock.mock_open(read_data="2000000").return_value,
        ]
        stats = monitor.get_stats()
        
        self.assertIn('cpu_power_package-0_watts', stats)
        # 1,000,000 uJ diff = 1 Joule.
        # Time delta approx 0.1s. Power = 1J / 0.1s = 10W.
        # Allow some float margin
        self.assertAlmostEqual(stats['cpu_power_package-0_watts'], 10.0, delta=2.0)



class TestMQTTClient(unittest.TestCase):
    def test_discovery_payload(self):
        client = MQTTClient("localhost", 1883, None, None, "Test Device")
        client.client.publish = MagicMock()
        
        sensor_data = {
            "cpu_usage_percent": 10.5,
            "memory_used_mb": 4000
        }
        
        client.publish_discovery(sensor_data)
        
        # Verify publish called twice (once for each sensor)
        self.assertEqual(client.client.publish.call_count, 2)
        
        # Inspect first call args
        call_args = client.client.publish.call_args_list
        topics = [args[0][0] for args in call_args]
        
        self.assertTrue(any("homeassistant/sensor/test_device/cpu_usage_percent/config" in t for t in topics))

if __name__ == '__main__':
    unittest.main()
