# MICCAI 2017 Robotic Instrument Segmentation toolkit

## Features

The project provides code to manipulate RIS 2017 data and supports:

- [x] Porting calibration files to OpenCV format
- [x] Stereo Rectification of sample Data.
- [x] sample De-interlacing
- [x] Segmentation mask combination.
- [x] Binary tool segmentation dataset generation
- [ ] generation of .csv file containing samples paths.

## Known issues

- the dataset generation program assumes that the original dataset is stored
with a specific file structure, different from the one it's provided.
- stereo rectifying segmentation masks, their might be ambiguous mask values near
tool boarders. This is due to interpolation. In the future this can get fixed by
discrediting the mask after rectification.

## Notes on the Dataset

### Calibration

- Extrinsic Rotation matrix

The provided calibration includes a three value entry named `Extrinsic-Omega`
which describes to the rotation from left to right camera frame. Assuming that
the rotation is expressed using the Prorogues' formula, we converted to a 3x3
Rotation matrix and use it for stereo rectification.

- Calibration Errors

Using the calibration files provided with with datasets 3 and 6 to rectify
the stereo pairs, results to poor stereo rectifications where corresponding features
do not lie in the same scan-lines.

### Data format

- Sample image Dimensions

Based on the provided calibration parameters, albeit the frame size is
indicated to be `1280x1024`, the provided samples are of size `1920x1080` with
the rgb image places in the middle of the samples and black borders around it.
Center cropping the frames to `1280x1024`, results, again, to images with borders.

- Interlacing

Sample are extracted from interlaced video frames. This results to artifacts
whenever an object is moving fast between frames. Furthermore, because the full
video sequence is not provided, we are limited to simple de-interlacing techniques.
An additional issue comes from the fact that the provided samples are not
provided in the original size(`1280x1024`) as explain in the above section.

<!-- ### Left-Right Frame synchronization -->

### Solution

To remove the borders completely and make to make use of the provided calibration
we crop frames to `1263x1009` starting from pixel `328,37`.
Next, we de-interlace the the rgb samples which results to two frames, for each
stereo channel, with half the vertical resolution of the original interlaced frame.
We keep the first frame and resize it to `1280x1024` interpolating the missing
lines.
Segmentation marks are cropped and to `1009x1263` image and up-sampled to `1280x1024`.

## How to use it

### Environment setup

This project was build using anaconda. Assuming that anaconda is already installed
in the target machine, a anaconda environment suitable to run this code can be
created using the following steps.

- navigate to this project's folder
- create an environments (e.g. ris_toolkit) using the provided requirements.txt

    `conda create --name ris_toolkit --file requirements.txt`
- activate the anaconda environment

    `conda activate ris_toolkit`
- generate the data as described in the following section.

### Data generation

Assuming that the original dataset follows the following file structure.

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

the following program creates a modified dataset following the above file structure.
The new dataset will contain stereo rectified frames (based on `--rect_alpha`)
de-interlaced cropped and interpolated to `1280x1024` as described above.
Additionally a stereo_calib.json, OpenCV compatible, calibration file will be
generated, in place of camera_calibration.txt. This calibration file contains
original the stereo parameters plus the computed rectification parameters.

    python generate_stereo_binary_dataset.py /path_to_original/train_set /path_to_store_the_new/train_set --alpha_rect -1
    python generate_stereo_binary_dataset.py /path_to_original/test_set /path_to_store_the_new/test_set --alpha_rect -1
