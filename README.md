# MICCAI 2017 Robotic Instrument Segmentation toolkit


## Features
The project provides code to manipulate RIS 2017 data and supports:

- [x] Porting calibration files to opencv format
- [x] Stereo Rectification of sample Data.
- [x] sample De-interlacing
- [x] Segmentation mask combination.
- [x] Binary tool segmentation dataset generation
- [ ] generation of .csv file containing samples paths.

## Known issues
- the dataset generation program assumes that the original dataset is stored
with a specific file structure, different from the one it's provided.

- stereo rectifing segmentation masks, their might be umbiguious mask values near
tool boarders. This is due to interpolation. In the future this can get fixed by
discritizing the mask after rectification.

## Notes on the Dataset

### Calibration

- Extrinsics Rotation matrix

The provided calibration includes a three value entry named `Extrinsic-Omega`
which describes to the rotation from left to right camera frame. Assuming that
the rotation is expressed using the Rorigues' formula, we converted to a 3x3
Rotation matrix and use it for stereo rectification.

- Calibration Erros

Using the calibration files provided with with datasets 3 and 6 to rectify
the stereo pairs, results to poor stereo rectifications where corresponding features
do not lie in the same scanlines.

### Data format

- Sample image Dimentions

Based on the provided calibration parameters, albeat the frame size is
indicated to be `1280x1024`, the provided samples are of size `1920x1080` with
the rgb image places in the midle of the samples and black borders around it.
Center cropping the frames to `1280x1024`, results, again, to images with borders.

- Interlacing

Sample are extructed from interlaced video frames. This results to atrifacts
whenever an object is moving fast between frames. Furthermore, because the full
video sequence is not provided, we are limited to simple deinterlacing techniques.
An additional issue comes from the fact that the provided samples are not
provided in the original size(`1280x1024`) as explain in the above section.

<!-- ### Left-Right Frame syncronisation -->

### Solution

To remove the borders completely and make to make use of the provided calibration
we crop frames to `1263x1009` starting from pixel `328,37`.
Next, we deinterlace the the rgb samples which results to two frames, for each
stereo channel, with half the vertical resolution of the original interlaced frame.
We keep the first frame and resize it to `1280x1024` interpolating the missing
lines.
Segmentation marks are cropped and to `1009x1263` image and upsampled to `1280x1024`.
