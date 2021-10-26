#!/usr/bin/python3
# -*- coding: utf-8 -*-

###################################################################
# Import Lib
import os
from tqdm import tqdm
import cv2
import glob
import numpy as np
from utils import check_path, bbox_yolo2norm, parse_json, dset_format, name_mapping, dset_check_parse, draw_bbox


# 取得 map_table.json 的資訊
content_temp=[]                                         # 用於更換標籤內容的變數
dataset, mode, in_type, out_type, sample_grid, sample_grid_path, map_class = parse_json('./map_table.json')    # 解析 json 檔案 

# 檢查輸入的位置是否正確、是否存在
check_path(dataset)

# 取得所有標籤檔
txt_files=glob.glob(f'{dataset}/*.txt')

# 取得所有圖檔，使用第一張取得圖片大小
img_files=glob.glob(f'{dataset}/*.jpg')
img_sample=cv2.imread(img_files[0])             # 讀取樣本
        # 取得高寬通道
frames, row_frames=[],[]                        # 為了顯示用的

# 定義視窗
NAME = "SAMPLES"
cv2.namedWindow(NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);

###################################################################
# 開啟標籤檔並將內容按照 map_table 上的參數進行偵測與替代
#   [1] 開啟標籤檔並逐行讀取
#   [2] 解析內容，先將行末的 \n 去除 接著依據空白進行切割
#   [3] 針對不同的輸入輸出格式進行轉換，接著將標籤也進行轉換, 
#       e.g.將 bbox 從 yolo 轉換成 kitti 後，從 map_class 中去檢查是否有相同的並且更換
#   [4] 將剛剛更新後的內容 ( content_temp ) 寫入標籤檔

if mode != "only-show":

    print("\n[ Start Convert ]")
    # 將所有的標籤檔逐一讀取
    for img_path in tqdm(img_files):
        
        height, width, _ = cv2.imread(img_path).shape

        label_path=os.path.splitext(img_path)[0]+'.txt'

        # 每讀取一張，就刷新 content_temp 以免寫到之前的內容
        content_temp=[]

        # [1]
        with open(label_path,'r') as label:
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
        with open(label_path,'w') as label:
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
  
row, col = [ int(x) for x in sample_grid.split("x")]
sample_id_list = np.random.choice(len(img_files), size=row*col, replace=False)

avg_size = int(np.average([cv2.imread(img_files[idx]).shape[1] for idx in sample_id_list]))

for idx, img_id in enumerate(sample_id_list):
    

    img_path = img_files[img_id] 
    label_path=os.path.splitext(img_path)[0]+'.txt'

    frame = draw_bbox(img_path, label_path, out_type)
    frame = cv2.resize(frame, (avg_size,avg_size))
    frame = cv2.putText(frame, f"{img_path}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

    row_frames = frame if (idx)%(col)==0 else np.hstack((row_frames, frame))
    
    if ((idx+1)%(col))==0:
        frames.append(row_frames)
        row_frames=[]

frames=np.vstack((frames))

cv2.imshow(NAME, frames)

print(f"Press 'q' and 'esc' to leave, 's' to save in {sample_grid_path} ... ")
while(1):
    key=cv2.waitKey(1)
    if key in [ord('q'), 27]: 
        print('Quit')
        break
    elif key == ord('s'): 
        print(f"Saved Image ('{sample_grid_path}') ")
        cv2.imwrite(sample_grid_path, frames)
        break
    else: 
        pass

cv2.destroyAllWindows()
