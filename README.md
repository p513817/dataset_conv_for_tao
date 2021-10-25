# dataset_conv_for_tao
convert dataset's format for NVIDIA TAO Toolkit.

* Supported List:
    * [yolo-to-kitti](#yolo-to-kitti)

# yolo to kitti

## How to use

1. clone repo between dataset which you want to format:
    ```bash
    git clone https://github.com/p513817/dataset_conv_for_tao.git
    cd dataset_conv_for_tao
    ```
2. modify `map_table.json`
    ```json
    {
        "in_type":"yolo",
        "out_type":"kitti",
        "map_class":{
            "0":"usb",
            "1":"usb"
        }
    }
    ```
    * in_type: the dataset's format which you want to convert.
    * out_type: final output format of dataset.
    * map_class: you can change the class's name via setup `item` like sample.
3. convert dataset's format
    ```bash
    $ task='/path/to/your/dataset'
    $ python3 fmt_converter.py -i ${task} -m ./map_table.json 
    ```

## DEMO
```bash
$ python3 fmt_converter.py -i ./usb/ -m ./map_table.json 
* Convert from 'yolo' to 'kitti'
* Convert Classes Map: {'0': 'usb', '1': 'usb'}

[ Start Convert ]
100%|█████████████████████| 51/51 [00:00<00:00, 6933.86it/s]
Press 'q' and 'esc' to leave, 's' to save in sample.png ... 
Saved Image ('./sample.png') 
```

![image](./figures/sample.png)

## help
```bash
$ python3 fmt_converter.py --help
usage: fmt_converter.py [-h] [-i INPUT] [-m MAP] [-n NUM] [-s SHOW] [--only-show]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input files folder
  -m MAP, --map MAP     mapping-format file
  -n NUM, --num NUM     number of samples
  -s SHOW, --show SHOW  show samples
  --only-show           only show samples, not convert
```
