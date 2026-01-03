import time
import os
import glob
from unittest.mock import MagicMock, patch, mock_open

# Mock data
NUM_CARDS = 50  # Simulating a system with many potential card entries (maybe virtual functions)
CARDS = []
for i in range(NUM_CARDS):
    if i % 3 == 0:
        CARDS.append(('/sys/class/drm/card{}'.format(i), '0x8086')) # Intel
    elif i % 3 == 1:
        CARDS.append(('/sys/class/drm/card{}'.format(i), '0x1002')) # AMD
    else:
        CARDS.append(('/sys/class/drm/card{}'.format(i), '0x10DE')) # NVIDIA/Other

# Original Implementation
def original_get_gpu_stats(cards):
    data = {}

    # Intel Loop
    for path, vendor_id_val in cards:
        try:
            # Simulate vendor check
            # In real code: vendor_path = os.path.join(path, 'device/vendor')
            # if os.path.exists...
            if True: # path exists
                vendor_id = vendor_id_val
                if vendor_id == '0x8086': # Intel
                    card_name = os.path.basename(path)
                    # Simulate freq check
                    data[f'gpu_intel_{card_name}_freq_mhz'] = 1000
        except Exception:
            pass

    # AMD Loop
    for path, vendor_id_val in cards:
        try:
            # Simulate vendor check AGAIN
            if True:
                vendor_id = vendor_id_val
                if vendor_id == '0x1002': # AMD
                    card_name = os.path.basename(path)
                    # Simulate stats
                    data[f'gpu_amd_{card_name}_usage_percent'] = 50
        except Exception:
            pass
    return data

# Optimized Implementation
def optimized_get_gpu_stats(cards):
    data = {}

    # Combined Loop
    for path, vendor_id_val in cards:
        try:
            # Simulate vendor check ONCE
            if True:
                vendor_id = vendor_id_val

                if vendor_id == '0x8086': # Intel
                    card_name = os.path.basename(path)
                    data[f'gpu_intel_{card_name}_freq_mhz'] = 1000
                elif vendor_id == '0x1002': # AMD
                    card_name = os.path.basename(path)
                    data[f'gpu_amd_{card_name}_usage_percent'] = 50
        except Exception:
            pass

    return data

def run_benchmark():
    iterations = 10000

    start = time.time()
    for _ in range(iterations):
        original_get_gpu_stats(CARDS)
    original_time = time.time() - start

    start = time.time()
    for _ in range(iterations):
        optimized_get_gpu_stats(CARDS)
    optimized_time = time.time() - start

    print(f"Original Time: {original_time:.4f}s")
    print(f"Optimized Time: {optimized_time:.4f}s")
    print(f"Improvement: {(original_time - optimized_time) / original_time * 100:.2f}%")

if __name__ == "__main__":
    run_benchmark()
