import platform
import psutil
import os
import glob
import time

class SystemMonitor:
    def __init__(self):
        self.os_type = platform.system()
        self.arch = platform.machine()
        
        # State for rate calculations (CPU Power)
        self.last_check_time = time.time()
        self.last_cpu_energy = {} # {package_path: energy_uj_value}

        # Initialize NVIDIA stats if possible
        self.nvml_initialized = False
        try:
            import pynvml
            pynvml.nvmlInit()
            self.nvml_initialized = True
            self.pynvml = pynvml
        except ImportError:
            pass
        except Exception:
            pass

    def get_stats(self):
        stats = {}
        # Calculate time delta for rates
        current_time = time.time()
        time_delta = current_time - self.last_check_time
        
        # We need at least a small delta to calculate rates correctly
        # If called too fast, we might skip update or use tiny delta
        if time_delta <= 0:
            time_delta = 0.001

        stats.update(self._get_cpu_stats(time_delta))
        stats.update(self._get_memory_stats())
        stats.update(self._get_disk_stats())
        stats.update(self._get_network_stats())
        stats.update(self._get_system_stats())
        stats.update(self._get_gpu_stats())
        
        self.last_check_time = current_time
        return stats

    def _get_cpu_stats(self, time_delta):
        data = {}
        # Usage
        data['cpu_usage_percent'] = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        for i, p in enumerate(per_core):
            data[f'cpu_core_{i}_usage_percent'] = p
        
        # Frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                data['cpu_freq_current'] = freq.current
        except Exception:
            pass

        # Load
        if hasattr(os, 'getloadavg'):
            load = os.getloadavg()
            data['load_1m'] = load[0]
            data['load_5m'] = load[1]
            data['load_15m'] = load[2]

        # Temp (Linux only usually)
        if self.os_type == 'Linux':
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                for entry in temps['coretemp']:
                    if entry.label:
                        data[f'cpu_temp_{entry.label}'] = entry.current
                    else:
                        data['cpu_temp'] = entry.current
            elif 'cpu_thermal' in temps: # Raspberry Pi often
                 data['cpu_temp'] = temps['cpu_thermal'][0].current

        # Power (x86 Linux RAPL)
        if self.os_type == 'Linux' and self.arch in ['x86_64', 'i686']:
            rapl_path = '/sys/class/powercap/intel-rapl'
            if os.path.exists(rapl_path):
                # Iterate over packages
                packages = glob.glob(os.path.join(rapl_path, 'intel-rapl:*'))
                for pkg in packages:
                    name_file = os.path.join(pkg, 'name')
                    energy_file = os.path.join(pkg, 'energy_uj')
                    if os.path.exists(name_file) and os.path.exists(energy_file):
                        try:
                            with open(name_file, 'r') as f:
                                name = f.read().strip()
                            with open(energy_file, 'r') as f:
                                energy_uj = int(f.read().strip())
                            
                            # Calculate Watts if we have previous data
                            if pkg in self.last_cpu_energy:
                                diff_uj = energy_uj - self.last_cpu_energy[pkg]
                                # Handle wrap-around if necessary (though unlikely for 64bit counters in short intervals)
                                if diff_uj >= 0:
                                    power_watts = (diff_uj / 1_000_000.0) / time_delta
                                    data[f'cpu_power_{name}_watts'] = round(power_watts, 2)
                            
                            # Update state
                            self.last_cpu_energy[pkg] = energy_uj

                        except Exception:
                            pass
        
        return data

    def _get_memory_stats(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'memory_total_mb': mem.total // 1024 // 1024,
            'memory_used_mb': mem.used // 1024 // 1024,
            'memory_free_mb': mem.free // 1024 // 1024,
            'memory_percent': mem.percent,
            'swap_percent': swap.percent
        }

    def _get_disk_stats(self):
        data = {}
        try:
            usage = psutil.disk_usage('/')
            data['disk_root_usage_percent'] = usage.percent
            data['disk_root_free_gb'] = usage.free // 1024 // 1024 // 1024
        except Exception:
            pass
        return data

    def _get_network_stats(self):
        data = {}
        net = psutil.net_io_counters()
        data['net_bytes_sent_mb'] = net.bytes_sent // 1024 // 1024
        data['net_bytes_recv_mb'] = net.bytes_recv // 1024 // 1024
        return data

    def _get_system_stats(self):
        return {
            'boot_time': int(psutil.boot_time()),
            'uptime_seconds': int(time.time() - psutil.boot_time())
        }

    def _get_gpu_stats(self):
        data = {}
        # ARM: Skip
        if self.arch not in ['x86_64', 'i686']:
            return data

        # NVIDIA
        if self.nvml_initialized:
            try:
                device_count = self.pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = self.pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = self.pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode('utf-8')
                    util = self.pynvml.nvmlDeviceGetUtilizationRates(handle)
                    mem = self.pynvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = self.pynvml.nvmlDeviceGetTemperature(handle, 0)
                    try:
                        power = self.pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0 # mW to W
                        data[f'gpu_nvidia_{i}_power_watts'] = power
                    except Exception:
                        pass
                    
                    data[f'gpu_nvidia_{i}_usage_percent'] = util.gpu
                    data[f'gpu_nvidia_{i}_memory_percent'] = (mem.used / mem.total) * 100
                    data[f'gpu_nvidia_{i}_temp_c'] = temp
            except Exception:
                pass

        # Intel & AMD (sysfs)
        # Look for /sys/class/drm/card*
        for path in glob.glob('/sys/class/drm/card*'):
            try:
                vendor_path = os.path.join(path, 'device/vendor')
                if os.path.exists(vendor_path):
                    with open(vendor_path, 'r') as f:
                        vendor_id = f.read().strip()

                    if vendor_id == '0x8086': # Intel
                        card_name = os.path.basename(path)
                        # Frequency
                        freq_path = os.path.join(path, 'gt_act_freq_mhz')
                        if os.path.exists(freq_path):
                            with open(freq_path, 'r') as f:
                                data[f'gpu_intel_{card_name}_freq_mhz'] = int(f.read().strip())
                        # Attempt to find power/energy if available (often in rapl but specific)

                    elif vendor_id == '0x1002': # AMD
                        card_name = os.path.basename(path)
                        # Usage
                        busy_path = os.path.join(path, 'device/gpu_busy_percent')
                        if os.path.exists(busy_path):
                            with open(busy_path, 'r') as f:
                                data[f'gpu_amd_{card_name}_usage_percent'] = int(f.read().strip())
                        # Temp and Power (via hwmon)
                        hwmon_dir = os.path.join(path, 'device/hwmon')
                        if os.path.exists(hwmon_dir):
                            for hwmon in glob.glob(os.path.join(hwmon_dir, 'hwmon*')):
                                # Temp
                                temp_input = os.path.join(hwmon, 'temp1_input')
                                if os.path.exists(temp_input):
                                    with open(temp_input, 'r') as f:
                                        # Millidegree Celsius
                                        data[f'gpu_amd_{card_name}_temp_c'] = int(f.read().strip()) / 1000.0
                                
                                # Power
                                # Try power1_average first, then power1_input
                                power_found = False
                                for p_file in ['power1_average', 'power1_input']:
                                    p_path = os.path.join(hwmon, p_file)
                                    if os.path.exists(p_path):
                                        with open(p_path, 'r') as f:
                                            # Microwatts
                                            val = int(f.read().strip())
                                            data[f'gpu_amd_{card_name}_power_watts'] = val / 1_000_000.0
                                            power_found = True
                                            break
            except Exception:
                pass

        return data
