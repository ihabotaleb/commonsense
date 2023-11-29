import json

def main():
    try:
        with open('device_info.json', 'r') as f:
            device_data = json.load(f)

        with open('stats.json', 'r') as f:
            stats = json.load(f)
    except:
        print("No device and room device_info.json found")
        return
    
    out = {}

    out['room_id'] = device_data['room_id']
    out['camera_id'] = device_data['camera_id']

    for i in stats.keys():
        if i not in device_data.keys():
            device_data[i] = stats[i]
        else:
            device_data[i] = max(device_data[i], stats[i])