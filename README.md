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
        "dataset":"/path/to/your/dataset",
        "mode_option":["convert", "only-show"],
        "mode":"mode option",
        "in_type":"input type",
        "out_type":"output type",
        "sample_path":"./sample.png",
        "sample_grid":"3x3",
        "map_class":{
            "0":"name you want to replace",
            "1":"name you want to replace"
        }
    }
    ```
    * dataset: path of your dataset.
    * mode: choice a mode from mode_option.
    * in_type: the dataset's format which you want to convert.
    * out_type: final output format of dataset.
    * sample_path: path of sample which generate after converting.
    * sample_gird: you can define the grid of the sample image.
    * map_class: you can change the class's name via setup `map_classes` like the sample.

3. convert dataset's format
    ```bash
    $ python3 fmt_converter.py
    ```

## Demo
1. Convert
    ```json
    {
        "dataset":"mask",
        "mode_option":["convert", "only-show"],
        "mode":"convert",
        "in_type":"yolo",
        "out_type":"kitti",
        "sample_grid_path":"./sample.jpg",
        "sample_grid":"3x5",
        "map_class":{
            "0":"mask",
            "1":"no-mask",
            "2":"abnormal"
        }
    }
    ```

    ```bash
    $ python3 fmt_converter.py

    [ Start Convert ]
    100%|█████████████████████| 51/51 [00:00<00:00, 6933.86it/s]
    Press 'q' and 'esc' to leave, 's' to save in sample.png ... 
    Saved Image ('./sample.png') 
    ```

    ![image](./figures/sample.jpg)

2. Only-Show
    Dependence on "out_type"
    ```json
    {
        "dataset":"mask",
        "mode_option":["convert", "only-show"],
        "mode":"only-show",
        "in_type":"yolo",
        "out_type":"yolo",
        "sample_grid_path":"./sample_org.jpg",
        "sample_grid":"3x5",
        "map_class":{
            "0":"mask",
            "1":"no-mask",
            "2":"abnormal"
        }
    }
    ```

    ![image](./figures/sample_org.jpg)