import cv2
import numpy as np
import json
import sys
from common import *
import picamera
import time

#### THREE AXES
    # 1. Edge based comparison
    # 2. Colour based
    # 3. Matching based

# When given an RGB input, produce a grayscale version, an edge map, and histograms for both as well as the original

def get_relevant_processings(im):
    # Convert RGB image to grayscale
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    normed = cv2.equalizeHist(gray)

    # Apply edge detection
    edges = cv2.Canny(normed, 100, 200)

    # Calculate histograms
    hist_gray = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_edges = cv2.calcHist([edges], [0], None, [256], [0, 256])

    return gray, edges, hist_gray, hist_edges

def chi_square(hist1, hist2):
    # Compare histograms using chi-square
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)

def get_good_matches(img1, img2):
    # Perform feature detection and description
    orb = cv2.ORB_create(10000)

    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

    if descriptors1 is None or descriptors2 is None:
        return -1

    # Perform feature matching using RANSAC
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors1, descriptors2)

    # Apply RANSAC to filter out outliers
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    if len(src_pts) < 4 or len(dst_pts) < 4:
        return -1

    _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # Count the number of good matches
    good_matches = np.sum(mask)

    # Calculate the percentage of good matches
    total_matches = len(matches)
    percentage = (good_matches / total_matches)

    return percentage

def yolo_detect(frame):
    weights_path = "yolo_deps/yolov3.weights"
    config_path = "yolo_deps/yolov3.cfg"
    
    #setup labels
    labels_path = "yolo_deps/yolov3.txt"
    LABELS = open(labels_path).read().strip().split("\n")
    
    net = cv2.dnn.readNet(weights_path, config_path)
    blob = cv2.dnn.blobFromImage(frame, 0.000352, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    def get_output_layers(net):
        layer_names = net.getLayerNames()

        try:
            output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        except:
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        return output_layers
    
    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    confidence_threshold = 0.5

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > confidence_threshold:
                class_ids.append(LABELS[class_id])
                confidences.append(float(confidence))

    out = {}
    for i in range(len(class_ids)):
        if class_ids[i] not in out.keys():
            out[class_ids[i]] = confidences[i]
        else:
            out[class_ids[i]] = max(out[class_ids[i]], confidences[i])

    return out


def main():
    try:
        with open('device_info.json', 'r') as f:
            device_data = json.load(f)
    except:
        print("No device and room device_info.json found")
        return

    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(3)
        camera.capture('frame.png', 'png')
        camera.stop_preview()
    
    frame = cv2.imread('frame.png')

    #flip frame
    if ("rotate" in device_data.keys()):
        frame = cv2.flip(frame, -1)
        cv2.imwrite('frame.png', frame)
    


    im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    reference_path = f"room_{device_data['room_id']}-camera_{device_data['camera_id']}+setup_frame.png"
    ref = cv2.imread(reference_path)

    if ref is None:
        print("Failed to read reference frame")
        return

    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

    # cv2.imwrite("/temp/im.png", im)
    # cv2.imwrite("temp/ref.png", ref)

    ref_segments = []
    im_segments = []

    for i in range(len(device_data['zones'])):
        b = Bounds(device_data['zones'][i]['x'], device_data['zones'][i]['y'], device_data['zones'][i]['w'], device_data['zones'][i]['h'])
        ref_segments.append(get_bounded_image(ref, b))
        im_segments.append(get_bounded_image(im, b))

        # cv2.imwrite(f"temp/ref{i}.png", ref_segments[i])
        # cv2.imwrite(f"temp/im{i}.png", im_segments[i])

    zone_results = {}
    # 100 percent score for the zone:
    ##### 10 points for the log difference of the chi square distance --> 7 for edges, 3 for color
    ##### 40 points for the match percentage --> 30 for edges, 10 for color
    ##### 50 points for the yolo score --> confidence * 50
    
    for i in range(len(ref_segments)):
        ref_segment = ref_segments[i]
        im_segment = im_segments[i]

        ref_im, ref_edges, ref_hist_original, ref_hist_edges = get_relevant_processings(ref_segment)
        im_im, im_edges, im_hist_original, im_hist_edges = get_relevant_processings(im_segment)

        result = {}

        result['edge'] = {}
        result['edge']['match_percentage'] = get_good_matches(ref_edges, im_edges)
        result['edge']['hist_chi_square'] = chi_square(ref_hist_edges, im_hist_edges)
        
        edge_score = (1 - result['edge']['match_percentage']) * 0.3 + max(np.log10(result['edge']['hist_chi_square']) / 1000 - 0.07, 0)

        result['im'] = {}
        result['im']['match_percentage'] = get_good_matches(ref_im, im_im)
        result['im']['hist_chi_square'] = chi_square(ref_hist_original, im_hist_original)
        
        im_score = (1 - result['im']['match_percentage']) * 0.4 * 0.1 + max(min(0.003, np.log10(result['edge']['hist_chi_square']) / 1000) - 0.03, 0)
        
        yolo_score = 0

        if edge_score + im_score > 0.2:
            yolo = yolo_detect(im_segment)
            if 'person' in yolo.keys():
                yolo_score = max(yolo['person'] * 0.9, 0.5)
        else:
            yolo = -1

        result['cnn'] = yolo if yolo != -1 else {}
        
        zone_results[i] = {'score': yolo_score + im_score + edge_score, 'breakdown': {'edge_score': edge_score, 'im_score': im_score, 'yolo_score': yolo_score}, 'cnn': result['cnn']}

    with open("stats.json", "w") as f:
        json.dump(zone_results, f)



if __name__ == "__main__":
    sys.exit(main())