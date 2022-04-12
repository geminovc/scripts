import os
import numpy as np 
import cv2
import argparse
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets  import RectangleSelector
import signal

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--folder', metavar='f', type=str,
                    help='path to the folder /averages folder that has all the images.')
parser.add_argument('--name', metavar='n', type=str,
                    help='name of the celebrity, used to create the pkl with the dictionary.')
parser.add_argument('--resolution', metavar='n', type=int, default=1024,
                    help='The resolution to crop the video at.')
parser.add_argument('--phase', metavar='n', type=str,
                    help='Train or test phase.')
args = parser.parse_args()

data_dir = args.folder + "/averages/" + str(args.phase) + "/"
video_name = args.name
image_names = sorted(os.listdir(data_dir))
resolution = int(args.resolution)

if not os.path.exists(args.folder + "/" + video_name + "_" + str(args.phase) + ".pkl"):
    annotations = {}
    for x in image_names:
        annotations[x] = []

    with open(args.folder + "/" + video_name + "_" + str(args.phase) + ".pkl", "wb") as handle:
        pickle.dump(annotations, handle)
else:
    with open(args.folder + "/" + video_name + "_" + str(args.phase) + ".pkl", "rb") as handle:
        annotations = pickle.load(handle)
    assert(sorted(annotations.keys()) == image_names)

def line_select_callback(eclick, erelease):
    global prev_rect
    global current
    global adjusted
    global img
    global resolution
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    x2, y2 = min(x1 + resolution, img.shape[1]), min(y1 + resolution, img.shape[0])

    rect = plt.Rectangle( (min(x1,x2),min(y1,y2)), np.abs(x1-x2), np.abs(y1-y2), fill=False, edgecolor='red')
    if prev_rect != None:
        prev_rect.remove()
    
    adjusted = 0
    prev_rect = rect
    current = [x1, y1, x2, y2]
    ax.add_patch(rect)
    ax.set_title (f"{np.abs(x1-x2)}, {np.abs(y1-y2)}")

def press(event):
    global i
    global img
    global current
    global prev_rect
    global ax
    global adjusted
    global resolution

    if event.key == 'z':
        if current != None:
            plt.close()

    if event.key == 'a':
        if adjusted == 1:
            return
        if current == None:
            print("Please create an annotation before adjusting it.")
            return
        prev_rect.remove()
        x1, y1, x2, y2 = current
        center_x = np.abs(x1+x2)/2
        center_y = np.abs(y1+y2)/2
        length = resolution #min(img.shape[0], img.shape[1]) #resolution
        start_x = center_x - int(length/2)
        start_y = center_y - int(length/2)
        rect = plt.Rectangle((start_x, start_y), int(length), int(length), fill=False, edgecolor='blue')
        prev_rect = rect
        #current = [max(0, start_x), max(0, start_y), min(img.shape[1], start_x + length), min(img.shape[0], length,start_y + length)]
        print("current",i, current)
        adjusted = 1
        ax.add_patch(rect)
        plt.draw()
        plt.show()

prev_rect = None
current = []
prev_dim = None
adjusted = 0
for i in range(len(image_names)):
    if len(annotations[image_names[i]]) != 0:
        print(image_names[i], "Done!")
        current = annotations[image_names[i]]
        continue
    print(data_dir, image_names[i])
    img = np.flip(cv2.imread(os.path.join(data_dir, image_names[i])), 2)
    adjusted = 0
    xdata = np.linspace(0,9*np.pi, num=301)
    ydata = np.sin(xdata)

    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('key_press_event', press)
    line = ax.imshow(img)        
    
    if i != 0 and img.shape != prev_dim:
        if prev_rect != None:
            prev_rect.remove()
        
        prev_rect = None
        current = []
    
    print(current)
    if current != None and len(current) != 0:
        x1, y1, x2, y2 = current
        print("Current from prev:", current)
        cur_rect = plt.Rectangle((x1, y1), np.abs(x1-x2), np.abs(y1-y2), fill=False, edgecolor='red')
        ax.add_patch(cur_rect)
        prev_rect = cur_rect

    rs = RectangleSelector(ax, line_select_callback,
                        drawtype='box', useblit=False, button=[1], 
                        minspanx=5, minspany=5, spancoords='pixels',
                        interactive=True)
    plt.show()
    prev_dim = img.shape
    print("final coordinate", image_names[i], current)
    annotations[image_names[i]] = current
    with open(args.folder + "/" + video_name + "_" + str(args.phase) + ".pkl", "wb") as handle:
        pickle.dump(annotations, handle)
