from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import sys

awsiot_endpoint = 'a2rag7jax1a2lq-ats.iot.us-east-1.amazonaws.com'
root_ca_path = '/home/pi/certs/Amazon-root-CA-1.pem'  
private_key_path = '/home/pi/certs/private.pem.key'  
cert_path = '/home/pi/certs/device.pem.crt'  
mqtt_client = AWSIoTMQTTClient('common-sense-h1')  
mqtt_client.configureEndpoint(awsiot_endpoint, 8883)
mqtt_client.configureCredentials(root_ca_path, private_key_path, cert_path)
mqtt_client.connect()

def main():
    #read device_info.json
    DEVICE_INFO = {}
    try:
        with open('device_info.json', 'r') as f:
            DEVICE_INFO = json.load(f)
    except:
        print("device_info.json not found")
        return 0
    
    #load stats.json
    STATS = {}
    try:
        with open('stats.json', 'r') as f:
            STATS = json.load(f)
    except:
        print("stats.json not found, run compare_frames.py first")
        return 0
    
    # occupancy = [STATS[str(i)]['score'] for i in range(len(DEVICE_INFO['zones']))]

    data = {
        "room_id": DEVICE_INFO['room_id'],
        "camera_id": DEVICE_INFO['camera_id'],
        "occupancy": STATS,
        "timestamp": time.time(),
        "ttl": time.time() + 300
    }
    json_data = json.dumps(data)

    mqtt_client.publish('occupancy', json_data, 1)

if __name__ == '__main__':
    sys.exit(main())