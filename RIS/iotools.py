from pathlib import Path
import cv2
import numpy as np
from . import utils
# paths should be either pathlig.Path or str

# read calibration files.
# read calibration files in original format.


def read_calibration_txt(path):
    try:
        path = Path(path)
    except ValueError as ev:
        raise TypeError("path should be %r" % path, ev)
    if not path.exists():
        raise FileNotFoundError("{} does not exist", path)
    
    with open(path, 'r') as calib_txt:
        lines = calib_txt.readlines()
    if len(lines)!=12:
        raise ValueError("check the validity of {}. It should have 12 lines", path)
    
    calib = dict()
    _, w = utils.parse_calib_txt_entry(lines[0])
    _, h = utils.parse_calib_txt_entry(lines[1])
    calib['K1'], calib['D1'] = utils.parse_camera_calib(lines[2:6])
    calib['K2'], calib['D2'] = utils.parse_camera_calib(lines[6:10])
    calib['R'], calib['T'] = utils.parse_RT_calib(lines[10:12])
    return calib
     
def save_calib(path, calib):
    try:
        path = Path(path)
    except ValueError as ev:
        raise TypeError("path should be %r" % path, ev)
    path.parent.mkdir(parents=True, exist_ok=True)

    fs_write = cv2.FileStorage(str(path), cv2.FILE_STORAGE_WRITE)
    for k in calib.keys():
        if calib[k] is not None:
            fs_write.write(k, calib[k])
    fs_write.release()
    return calib
    

# parse datasets and return paths
