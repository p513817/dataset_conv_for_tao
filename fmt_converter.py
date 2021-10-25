#!/usr/bin/python3
# -*- coding: utf-8 -*-

###################################################################
# Import Lib
import argparse
import os
from tqdm import tqdm
import json
import cv2
import glob
import numpy as np
from utils import check_path, bbox_yolo2norm, parse_json, dset_format, name_mapping, dset_check_parse, draw_bbox

def init_args():
    # Initial argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input", help="input files folder")
    parser.add_argument("-m","--map", help="mapping-format file")
    parser.add_argument("-n","--num", default=9, type=int, help="number of samples")
    parser.add_argument("-s","--show", default=True, help="show samples")
    parser.add_argument("--only-show", action="store_true", help="only show samples, not convert")
    args = parser.parse_args()
    return args

###################################################################
# 初始化

# 初始化 argparse
args=init_args()

# 檢查輸入的位置是否正確、是否存在
check_path(args.input)

# 取得 map_table.json 的資訊
content_temp=[]                                         # 用於更換標籤內容的變數
in_type, out_type, map_class = parse_json(args.map)    # 解析 json 檔案 
print(f"* Convert from '{in_type}' to '{out_type}'")
print(f"* Convert Classes Map: {map_class}")
if in_type != "yolo": print("* Warning: Default format is 'yolo'")

# 取得所有標籤檔
txt_files=glob.glob(f'{args.input}/*.txt')

# 取得所有圖檔，使用第一張取得圖片大小
img_files=glob.glob(f'{args.input}/*.jpg')
img_sample=cv2.imread(img_files[0])             # 讀取樣本
height, width, channel= img_sample.shape        # 取得高寬通道
frames, row_frames=[],[]                        # 為了顯示用的

###################################################################
# 開啟標籤檔並將內容按照 map_table 上的參數進行偵測與替代
#   [1] 開啟標籤檔並逐行讀取
#   [2] 解析內容，先將行末的 \n 去除 接著依據空白進行切割
#   [3] 針對不同的輸入輸出格式進行轉換，接著將標籤也進行轉換, 
#       e.g.將 bbox 從 yolo 轉換成 kitti 後，從 map_class 中去檢查是否有相同的並且更換
#   [4] 將剛剛更新後的內容 ( content_temp ) 寫入標籤檔

if not args.only_show:

    print("\n[ Start Convert ]")
    # 將所有的標籤檔逐一讀取
    for txt in tqdm(txt_files):
        
        # 如果讀取到 classes.txt 就跳過
        if txt == os.path.join(args.input, "classes.txt"): continue

        # 每讀取一張，就刷新 content_temp 以免寫到之前的內容
        content_temp=[]

        # [1]
        with open(txt,'r') as label:
            for line in label.readlines():
                # [2]
                raw = (line.rstrip('\n').split(" "))    
                if raw[0] == '': continue               # Some label will contain a space at end line
                
                # [3]
                if in_type == 'yolo':
                    classes, cx, cy, w, h = dset_check_parse(raw, in_type) 

                    if out_type == 'kitti':
                        x1,y1,x2,y2=bbox_yolo2norm(cx, cy, w, h, width, height)     
                        trg_format=dset_format(out_type)
                        content_temp.append( trg_format( name_mapping(classes, map_class), x1, y1, x2, y2) )
                                            
                else:
                    classes, cx, cy, w, h = dset_check_parse(raw, in_type) 
                    trg_format=dset_format(in_type)
                    content_temp.append( trg_format(name_mapping(classes, map_class), cx, cy, w, h) )
        
        # [4]
        with open(txt,'w') as label:
            for cnt in content_temp:
                label.write(cnt+'\n')

###################################################################
# 顯示轉換後的結果
#   [1] 按照 args.num  隨機產生 ID
#   [2] 解析圖片路徑，取得檔名與副檔名，並且使用 OpenCV 讀取圖片
#   [3] 從檔名取得標籤檔並且解析取得對應資訊，其中需要將座標轉換 string->float->int
#   [4] 繪製相關資訊
#   [5] 每張圖片都將其進行水平合併
#   [6] 如果儲存到平方次數，則進行儲存，e.g.num=9, 則每合併3張就儲存一次
#   [7] 將過水平合併的圖片，進行垂直合併
#   [8] 一些輸出的動作

if args.show:
    # [1]    
    for idx, img_id in enumerate(np.random.randint(len(img_files), size=args.num)):
        # [2]
        img_path = img_files[img_id]
        name, ext = os.path.splitext(img_path)
        frame = cv2.imread(img_path)
        # [3]
        with open(name+'.txt', 'r') as label:
            for line in label.readlines():
                raw=line.rstrip('\n').split(" ")
                classes=raw[0]

                if out_type=="kitti":
                    x1,y1,x2,y2=map(lambda x:int(float(x)), raw[4:8])
                elif out_type=="yolo":
                    x1,y1,x2,y2=map(lambda x:int(x), bbox_yolo2norm(raw[1], raw[2], raw[3], raw[4], frame.shape[1], frame.shape[0]))

                # [4]
                cv2.putText(frame, f"{img_path}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
                frame = draw_bbox(frame, classes, (x1,y1,x2,y2) )

        # [5]
        row_frames = frame if (idx)%(np.sqrt(args.num))==0 else np.hstack((row_frames, frame))
        # [6]
        if ((idx+1)%(np.sqrt(args.num)))==0:
            frames.append(row_frames)
            row_frames=[]
    # [7]
    frames=np.vstack((frames))

    # [8]
    cv2.namedWindow('Sample', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Sample", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
    cv2.imshow('Sample', frames)
    print("Press 'q' and 'esc' to leave, 's' to save in sample.png ... ")
    while(1):
        key=cv2.waitKey(1)
        if key in [ord('q'), 27]: 
            print('Quit')
            break
        elif key == ord('s'): 
            print("Saved Image ('./sample.png') ")
            cv2.imwrite('./sample.png', frames)
            break
        else: 
            pass
    
    cv2.destroyAllWindows()
    