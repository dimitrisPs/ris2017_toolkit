# MICCAI 2017 Robotic Instrument Segmentation toolkit

## Features

The project provides code to manipulate RIS 2017 data and supports:

- [x] Porting calibration files to OpenCV format
- [x] Stereo Rectification of sample Data.
- [x] De-interlacing
- [x] Segmentation mask combination.
- [x] Binary tool segmentation dataset generation
- [x] generation of .csv file containing samples paths.
- [x] Computation of dataset statistics
- [x] Evaluation script for binary segmentation.

The dataset generation program assumes that the original dataset is stored
with a specific file structure, different from the one it's provided.

## Dataset statistics

The table below, lists color statistics and binary segmentation pixel coverage
per dataset. Color statistics were computed only using the left frame from each
sample, after de-interlacing and cropping it. The statistics corresponds to images
in range 0-1.

|        Dataset        | Mean  |       |       | Stdev |       |       | Coverage |
| :-------------------: | :---: | :---: | :---: | :---: | :---: | :---: | :------: |
|                       |  Red  | Green | Blue  |  Red  | Green | Blue  |    %     |
| instrument_dataset_1  | 0.510 | 0.318 | 0.354 | 0.187 | 0.161 | 0.175 |  0.167   |
| instrument_dataset_2  | 0.482 | 0.318 | 0.367 | 0.154 | 0.144 | 0.161 |  0.132   |
| instrument_dataset_3  | 0.463 | 0.300 | 0.324 | 0.209 | 0.184 | 0.195 |  0.160   |
| instrument_dataset_4  | 0.531 | 0.313 | 0.351 | 0.161 | 0.150 | 0.162 |  0.155   |
| instrument_dataset_5  | 0.494 | 0.324 | 0.380 | 0.184 | 0.173 | 0.196 |  0.135   |
| instrument_dataset_6  | 0.469 | 0.291 | 0.317 | 0.193 | 0.169 | 0.188 |  0.153   |
| instrument_dataset_7  | 0.443 | 0.309 | 0.336 | 0.190 | 0.175 | 0.195 |  0.143   |
| instrument_dataset_8  | 0.503 | 0.284 | 0.348 | 0.187 | 0.150 | 0.174 |  0.164   |
| instrument_dataset_9  | 0.509 | 0.324 | 0.371 | 0.141 | 0.130 | 0.146 |  0.106   |
| instrument_dataset_10 | 0.492 | 0.293 | 0.321 | 0.190 | 0.151 | 0.168 |  0.125   |
|        Average        | 0.489 | 0.307 | 0.347 | 0.180 | 0.159 | 0.176 |  0.144   |

## Calibration

- Extrinsic Rotation matrix

The provided calibration includes a three value entry named `Extrinsic-Omega`
which describes to the rotation from left to right camera frame. Assuming that
the rotation is expressed using the Rodrigues' formula, we converted to a 3x3
Rotation matrix and use it for stereo rectification.

- Calibration Errors

Using the calibration files provided with with datasets 3 and 6 to rectify
the stereo pairs, results to poor stereo rectifications where corresponding features
do not lie in the same scan-lines. The calibration of datasets 5,7,8,9 and 10 are
mostly ok but they are not very accurate. calibration files for datasets 1,2 and 4
are ok.

## Data format

### Sample image Dimensions

Based on the provided calibration parameters, albeit the frame size is
indicated to be `1280x1024`, the provided samples are of size `1920x1080` with
the rgb image places in the middle of the samples and black borders around it.
Center cropping the frames to `1280x1024`, results, again, to images with borders.

### Interlacing

Sample are extracted from interlaced video frames. This results to artifacts
whenever an object is moving fast between frames. Furthermore, because the full
video sequence is not provided, we are limited to simple de-interlacing techniques.
An additional issue comes from the fact that the provided samples are not
provided in the original size(`1280x1024`) as explain in the above section.

## Known issues

### Time Synchronization

The left and right view are not synchronized in time. This can be easily seen in
views where a tool is moving fast in the vertical direction. In addition to the
interlacing artifacts, tools do not appear to be in the same scanlines.

Dataset 1- Frame 207

![stereo pair time synchronization issue](media/time_sync_issue_fs1f207_ris17.png)

### Ground truth

There are are frames with missing masks for some parts of tools. Most of those
samples have been found in dataset 8. In addition, mask are not exact and often
they include tissue or do not include the whole tool area.

Dataset8 - Frame 72

![missing masks](media/missing_mask_issue_fs1f207_ris17.png)

### Solution

- Data format

To remove the borders completely and make to make use of the provided calibration
we crop frames to `1263x1009` starting from pixel `328,37`.
Next, we de-interlace the the rgb samples which results to two frames, for each
stereo channel, with half the vertical resolution of the original interlaced frame.
We keep the first frame and resize it to `1280x1024` interpolating the missing
lines.
Segmentation marks are cropped and to `1009x1263` image and up-sampled to `1280x1024`.

## How to run the code

### Environment setup

This project was build using anaconda. Assuming that anaconda is already installed
in the target machine, a anaconda environment suitable to run this code can be
created using the following steps.

- navigate to this project's folder
- create an environments (e.g. ris_toolkit) using the provided requirements.txt

```bash
conda create --name ris_toolkit --file requirements.txt
```

- activate the anaconda environment

```bash
conda activate ris_toolkit
```

- generate the data as described in the following section.

### Data generation and cleaning

Assuming that the original dataset follows the following file structure.

```tree
.
├── train_set                       # folder containing train samples
│   └── instrument_dataset_i        # i corresponds to dataset number (0-8)
│       ├── left_frame              # dir containing left frames
│       ├── right_frame             # dir containing right frames
│       ├── ground_truth 
│       │   └── label_1             # dir contains ground truth labels for tool 1
│       │   └── label_n             # dir contains ground truth labels for tool n
│       ├── mappings.json
│       └── camera_calibration.txt  # 12 line calibration file.
└── test_set                        # folder containing test samples
    └── instrument_dataset_i        # i corresponds to dataset number (0-10)
        ├── left_frame              # dir containing left frames
        ├── right_frame             # dir containing right frames
        ├── ground_truth 
        │   └── label_1             # dir contains ground truth labels for tool 1
        │   └── label_n             # dir contains ground truth labels for tool n
        ├── mappings.json
        └── camera_calibration.txt  # 12 line calibration file.
```

the following program creates a modified dataset following the above file structure.
The new dataset will contain stereo rectified frames (based on `--rect_alpha`)
de-interlaced cropped and interpolated to `1280x1024` as described above.
Additionally a stereo_calib.json, OpenCV compatible, calibration file will be
generated, in place of camera_calibration.txt. This calibration file contains
original the stereo parameters plus the computed rectification parameters.

```bash
python -m scripts.generate_stereo_binary_dataset /path_to_original/train_set /path_to_store_the_new/train_set --alpha_rect -1
python -m scripts.generate_stereo_binary_dataset /path_to_original/test_set /path_to_store_the_new/test_set --alpha_rect -1
```

```bash
python -m scripts.generate_clean_monocular_dataset /path_to_original/train_set /path_to_store_the_new/train_set 
python -m scripts.generate_clean_monocular_dataset /path_to_original/test_set /path_to_store_the_new/test_set 
```

### Generate Sample CSV

```bash
python -m scripts.generate_io_csv.py path/to/dataset ./path/to/write/csv [--binary] [--disparity] 
```
### Evaluate Binary Segmentation
```bash
python -m scripts.evaluate  --gt_dir /path/to/test/dataset/root/dir --algorithm_output_dir /path/to directory/samples/for/eval/are/stored 
```