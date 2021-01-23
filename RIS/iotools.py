from pathlib import Path
import cv2
import numpy as np
from . import utils
import json
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
    w = int(utils.parse_calib_txt_entry(lines[0])[1][0])
    h = int(utils.parse_calib_txt_entry(lines[1])[1][0])
    calib['K1'], calib['D1'] = utils.parse_camera_calib(lines[2:6])
    calib['K2'], calib['D2'] = utils.parse_camera_calib(lines[6:10])
    calib['R'], calib['T'] = utils.parse_RT_calib(lines[10:12])
    calib['size'] = (h,w)
    return calib
     
def save_calib(path, calib):
    try:
        path = Path(path)
    except ValueError as ev:
        raise TypeError("path should be %r" % path, ev)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    fs_write = cv2.FileStorage(str(path), cv2.FILE_STORAGE_WRITE)
    for k in calib.keys():
        if type(calib[k]) is tuple:
            fs_write.write(k, np.array(calib[k], dtype=int))
        else:
            fs_write.write(k, calib[k])
    fs_write.release()
    return path


def cvjson_to_np(entry_dict):
    """parse a json entry containing opencv calibration parameter and returns
    the contents in the correct format.

    Args:
        entry_dict (dict): calibration parameter

    Returns:
        np.matrix: calibration parameter
    """
    if (type(entry_dict) is dict):
        if ('type_id' in entry_dict) and (entry_dict['type_id'] == 'opencv-matrix'):
            rows = entry_dict['rows']
            cols = entry_dict['cols']        
            if entry_dict['dt'] == 'i':
                #tuples contain integer values.
                return tuple(entry_dict['data'])
            mat = np.array(entry_dict['data']).reshape(rows, cols).astype(np.double)
            return mat
        return None
    return entry_dict


def load_calib(path):
    try:
        path = Path(path)
    except ValueError as ev:
        raise TypeError("path should be %r" % path, ev)
    if not path.exists():
        raise FileNotFoundError("{} does not exist", path)
    
    calib = dict()
    with open(path, 'r') as calib_file:
        calib_data = json.load(calib_file)
        for key in calib_data:
            calib[key] = cvjson_to_np(calib_data[key])
    return calib
    

# parse datasets and return paths
