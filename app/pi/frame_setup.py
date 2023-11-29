import picamera
import json
import sys
import cv2

try:
    with open('device_info.json', 'r') as f:
        data = json.load(f)
        DEVICE_INFO = f"room_{data['room_id']}-camera_{data['camera_id']}"
    with picamera.PiCamera() as camera:
        camera.start_preview()  # Start the camera preview
        while True:
            user_input = input("Press ENTER to take frame")
            break
        print('Saving frame')
        camera.capture(f'{DEVICE_INFO}+setup_frame.png', 'png')
        camera.stop_preview()  # Stop the camera preview
        if ("rotate" in data.keys()):
            frame = cv2.imread(f'{DEVICE_INFO}+setup_frame.png')
            frame = cv2.flip(frame, -1)
            cv2.imwrite(f'{DEVICE_INFO}+setup_frame.png', frame)
    print('Done!')

except FileNotFoundError:
    print("Failed. No device and room device_info.json found")