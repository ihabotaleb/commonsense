import numpy as np
import cv2
from common import Bounds
import sys


# Load current frame
IMAGE_PATH = sys.argv[1]

setup_frame = cv2.imread(IMAGE_PATH)

include_device_info = False
DEVICE_INFO = IMAGE_PATH.split('+')[0]

if len(DEVICE_INFO) > 1:
    include_device_info = True
    room_str, camera_str = DEVICE_INFO.split('-')
    DEVICE_INFO = {'room_id': int(room_str.split('_')[1]), 'camera_id': int(camera_str.split('_')[1])}    

while True:
    # determine how many zones
    im = setup_frame.copy()
    zone_count = input("How many zones? ")

    # Setup zones list
    zones = []

    # Show image and select zones
    cv2.imshow('im', im)
    for i in range(int(zone_count)):
        x,y,w,h = cv2.selectROI('im', im, fromCenter=False, showCrosshair=True)
        zones.append(Bounds(x, y, w, h))
        im = cv2.rectangle(im, (x,y), (x+w, y+h), (0, 255, 0, 0.5), -1)
        center = x + int(w/2), y + int(h/2)
        center = (center[0]-10, center[1]+10)
        im = cv2.putText(im, str(i), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow('im', im)

    cv2.imshow('im', im)

    # Confirm zones
    confirmation = input("Confirm? (y/n) ")
    if confirmation == 'y':
        print(zones[0].to_dict())
        print("Saved!")
        break

# Wait for keypress to end
print("Press any key to end selection...")
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save zones to JSON file
import json

out = {'zones': [zone.to_dict() for zone in zones]}

if include_device_info:
    out.update(DEVICE_INFO)

# save json of out
out_path = "device_info.json"
with open(out_path, 'w') as f:
    json.dump(out, f)

cv2.imwrite('zones.png', im)
