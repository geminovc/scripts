""" Interactive tool that lets you draw bounding boxes on the predicted 
    image on the right and shows you which part of the source image it
    maps to

    Needs a video strip from the FOM model reconstruction to read frames
    and flows from
"""
import os
import numpy as np 
import cv2
import argparse
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets  import RectangleSelector
import signal
import cv2

parser = argparse.ArgumentParser(description='Interactive tool to visualize flows based on bounding boxes')
parser.add_argument('--name', metavar='n', type=str,
                    help='name of video strip to infer data from.')

args = parser.parse_args()
video_name = args.name

""" call back function when a rectangle is drawn on the source image
"""
def line_select_callback(eclick, erelease):
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

    draw_overlays(x1, x2, y1, y2)


""" draw the outline rectangle and flow rectangle
"""
def draw_overlays(x1, x2, y1, y2):
    global prev_rect
    global current
    global flow
    global prev_patch
    
    current = [x1, y1, x2, y2]
    rect = plt.Rectangle((min(x1, x2), min(y1, y2)), \
            np.abs(x1 - x2), np.abs(y1 - y2), fill=False, edgecolor='red')
    
    a1, b1, a2, b2 = get_source_pixels_from_flow(flow, current)
    patch = plt.Rectangle((a1, b1), a2 - a1, b2 - b1, fill=False, edgecolor='green')
    
    if prev_rect != None:
        prev_rect.remove()
    if prev_patch != None:
        prev_patch.remove()
    
    prev_rect = rect
    prev_patch = patch
    
    ax.add_patch(rect)
    ax.add_patch(patch)


""" key press event to go to the next frame
"""
def press(event):
    global current

    if event.key == 'z':
        if current != None:
            plt.close()


""" get the corresponding pixel list of source from the 
    flow information and the selected rectangle
"""
def get_source_pixels_from_flow(flow, frame):
    src_list_x, src_list_y = [], []
    frame = [int(x) for x in frame]
    x1, y1, x2, y2 = frame
    x1 %= 256
    x2 %= 256

    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            xs = flow[x, y, 1]
            ys = flow[x, y, 0]
            src_pixel = (xs, ys)
            src_list_x.append(xs)
            src_list_y.append(ys)

    return min(src_list_x), min(src_list_y), max(src_list_x), max(src_list_y)


""" iterate through video frames fetching grids and finding its source patch
"""
cap = cv2.VideoCapture(video_name)
count = 0
prev_rect = None
prev_patch = None
current = []
plt.rcParams["figure.figsize"] = [16, 9]
while cap.isOpened():
    ret, img = cap.read()
    if ret == False:
        break
    count += 1

    # extract the source, predicted and flow
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    source_img = img[:, :256, :]
    driving_img = img[:, 256:512, :]
    deformed_img = img[:, 512:3*256, :]
    flow = img[:, 3*256:4*256, :]
    predicted_img = img[:, 4*256:5*256, :]
    
    # display source and predicted, register call back
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('key_press_event', press)
    new_img = np.concatenate((source_img, driving_img, deformed_img, predicted_img), axis=1)
    line = ax.imshow(new_img)        
    
    # retain rectangle from previous frame    
    if current != None and len(current) != 0:
        x1, y1, x2, y2 = current
        draw_overlays(x1, x2, y1, y2)

    rs = RectangleSelector(ax, line_select_callback,
                        drawtype='box', useblit=False, button=[1], 
                        minspanx=5, minspany=5, spancoords='pixels',
                        interactive=True)

    plt.show()

cap.release()
cv2.destroyAllWindows()
