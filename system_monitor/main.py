import os
import time
import socket
from monitor import SystemMonitor
from mqtt_client import MQTTClient

def main():
    # Load Environment Variables
    broker = os.environ.get('MQTT_BROKER', 'localhost')
    try:
        port = int(os.environ.get('MQTT_PORT', 1883))
    except ValueError:
        print("Invalid MQTT_PORT, defaulting to 1883")
        port = 1883
    
    username = os.environ.get('MQTT_USER')
    password = os.environ.get('MQTT_PASSWORD')

    # TLS Configuration
    use_tls = os.environ.get('MQTT_USE_TLS', 'false').lower() == 'true'
    tls_ca_certs = os.environ.get('MQTT_TLS_CA_CERTS')
    tls_certfile = os.environ.get('MQTT_TLS_CERTFILE')
    tls_keyfile = os.environ.get('MQTT_TLS_KEYFILE')
    tls_insecure = os.environ.get('MQTT_TLS_INSECURE', 'false').lower() == 'true'
    
    try:
        interval = int(os.environ.get('UPDATE_INTERVAL', 10))
    except ValueError:
        print("Invalid UPDATE_INTERVAL, defaulting to 10s")
        interval = 10

    device_name = os.environ.get('DEVICE_NAME', socket.gethostname())

    print(f"Starting System Monitor for device: {device_name}")
    print(f"Connecting to MQTT Broker: {broker}:{port}")

    # Initialize Monitor and MQTT Client
    monitor = SystemMonitor()
    client = MQTTClient(
        broker, port, username, password, device_name,
        use_tls=use_tls,
        ca_certs=tls_ca_certs,
        certfile=tls_certfile,
        keyfile=tls_keyfile,
        insecure=tls_insecure
    )

    # Allow some time for connection
    time.sleep(2)

    # Initial Fetch to register sensors
    print("Performing initial discovery...")
    # First call initializes state but might miss rates (CPU power)
    monitor.get_stats() 
    time.sleep(1) # Sleep briefly to allow rate calculation on next call
    initial_stats = monitor.get_stats()
    client.publish_discovery(initial_stats)
    
    # Main Loop
    print(f"Starting main loop with interval: {interval}s")
    while True:
        try:
            stats = monitor.get_stats()
            client.publish_update(stats)
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        time.sleep(interval)

if __name__ == "__main__":
    main()
