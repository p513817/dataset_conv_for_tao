import os
import json
import numpy as np
import cv2
from numpy.lib.function_base import average

def parse_json(json_file):
    # parse ./map_table.json 
    with open(json_file) as f:
        map_table = json.load(f)
        dataset = map_table['dataset']
        mode = map_table['mode']
        in_type = map_table['in_type']
        out_type = map_table['out_type']
        sample_grid = map_table['sample_grid']
        sample_grid_path = map_table['sample_grid_path']
        map_class = map_table['map_class']
    return dataset, mode, in_type, out_type, sample_grid, sample_grid_path, map_class

def dset_format(format):
    # 使用 Lambda 定義 數據集 格式
    kitti = lambda classes, x1, y1, x2, y2: f"{classes} 0.00 0 0.00 {x1} {y1} {x2} {y2} 0.00 0.00 0.00 0.00 0.00 0.00 0.00"
    yolo = lambda classes, cx, cy, w, h: f"{classes} {cx} {cy} {w} {h}"

    table = {   
        "kitti": kitti,
        "yolo": yolo 
    }
    return table[format]

def name_mapping(name, dict):
    return dict[name] if name in dict.keys() else name

def check_path(input_path):
    # check is the path exists
    if input_path == None:
        print("Please Enter Input Folder's Path")
        exit(1)
    if not os.path.exists(input_path):
        print("Couldn't Find Input Path")
        exit(1)    

def dset_check_parse(raw_data, in_type):
    if in_type=='yolo':
        if len(raw_data)==5:
            return raw_data
        else:
            print("\n\nlabel's format doesn't fit yolo format, please check again.")
            exit(1)
    else:
        print('unknown in_type')
        exit(1)

def bbox_yolo2norm(x, y, w, h, width, height):
    """
    convert bounding box's format from yolo to kitti ( for TAO ):
    
        YOLO: center_x, center_y, width, height
        Normal: left_x, left_y, right_x, right_y
    """
    x,y,w,h=map(lambda x: float(x), (x,y,w,h))
    x1, y1 = (x-w/2)*width, (y-h/2)*height
    x2, y2 = (x+w/2)*width, (y+h/2)*height
    return x1, y1, x2, y2

def bbox_yolo2norm_temp(xo, yo, wo, ho, image):
    # other tips: convert bounding box's format from yolo to kitti ( for TAO )
    # Auther: Innodisk, IPA, Will
    xo, yo, wo, ho=map(lambda x: float(x), (xo, yo, wo, ho))
    left = int(round(((2*xo*image.shape[1])-(wo*image.shape[1]))/2,0))
    top = int(round(((2*yo*image.shape[0])-(ho*image.shape[0]))/2,0))
    right = int(round(wo*image.shape[1]+left))
    bottom = int(round(ho*image.shape[0]+top))
    return left,top,right,bottom

def get_norm_bbox_from_label(frame, raw, label_type):
    if label_type=="kitti":
        x1,y1,x2,y2=map(lambda x:int(float(x)), raw[4:8])
    elif label_type=="yolo":
        x1,y1,x2,y2=map(lambda x:int(x), bbox_yolo2norm(raw[1], raw[2], raw[3], raw[4], frame.shape[1], frame.shape[0]))
    return (raw[0], x1,y1,x2,y2)

# img_path, label_path,, out_type
# auto random sample if sample_path not None
color_table=[(0,0,255),(255,0,0),(0,255,0),(255,255,0),(255,0,255),(0,255,255),(0,0,255)]

color_idx=0
label_color={}

def too_light(image):

    return 1 if cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[2] > 50 else 0
    

def draw_bbox(img_path, label_path, out_type):
    global color_idx, label_color, font_color
    img = cv2.imread(img_path)
    with open(label_path, 'r') as label:
        for line in label.readlines():

            raw=line.rstrip('\n').split(" ")
            # get normal bbox
            cls_name,x1,y1,x2,y2 = get_norm_bbox_from_label(img, raw, out_type)
            # choice color
            if cls_name not in label_color.keys():
                label_color[cls_name] = color_table[color_idx]
                color_idx= color_idx+1
            # draw bbox
            cv2.rectangle(img, (x1,y1), (x2,y2), label_color[cls_name], 2)
            # draw label
            font_size, font_thickness, font_pad = 1, 2, 5
            (w, h), _ = cv2.getTextSize( cls_name, cv2.FONT_HERSHEY_SIMPLEX, font_size, font_thickness)
            cv2.rectangle(img, (x1,y1-h), (x1+font_pad+w,y1), label_color[cls_name], -1)

            img = cv2.putText(img, cls_name, (x1+font_pad,y1-h//4), 
                                cv2.FONT_HERSHEY_SIMPLEX, font_size-0.4, 
                                (255,255,255) if label_color[cls_name][1]!=255 else (0,0,0), 
                                font_thickness, 
                                cv2.LINE_AA)
    return img

