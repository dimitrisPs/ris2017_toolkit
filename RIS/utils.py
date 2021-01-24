import cv2
import numpy as np

def parse_calib_txt_entry(line):
    #remove comment and trailing white spaces
    line = line.split('//')[0].rstrip()

    description, value_str = line.split(': ')
    values_str_lst = value_str.split(' ')
    values_lst = [float(val) for val in values_str_lst]
    
    return description, values_lst
    
def parse_camera_calib(lines):
    K = np.eye(3)
    _, (K[0,0], K[1,1]) = parse_calib_txt_entry(lines[0])
    _, (K[0,2], K[1,2]) = parse_calib_txt_entry(lines[1])
    K[0,1] = parse_calib_txt_entry(lines[2])[1][0]
    D = np.array(parse_calib_txt_entry(lines[3])[1]).reshape(-1,1)
    
    return K.astype(np.double), D.astype(np.double)
    
def parse_RT_calib(lines):
    R = np.eye(3)
    _, R = parse_calib_txt_entry(lines[0])
    _, T = parse_calib_txt_entry(lines[1])
    # most likely R is expressed using the rodrigues formula
    # print('check R')
    R = np.array(R).reshape(-1)
    R, _ = cv2.Rodrigues(R)
    T = np.array(T).reshape(-1,1)
    
    return R.astype(np.double), T.astype(np.double)

def center_crop(img, size):
    # size should be a (h,w)
    in_h, in_w = img.shape[:2]
    out_h, out_w = size
    assert in_h>out_h
    assert in_w>out_w
    start_x = int((in_w - out_w)//2)
    start_y = int((in_h - out_h)//2)
    return img[start_y:start_y+out_h, start_x:start_x+out_w].copy()


def frame_crop(img):
    img=img[37:1047, 328:1591]
    return img.copy()
    

def deinterlace(img, out_size=None):
    if out_size is None:
        out_size = img.shape
    img0 = img[::2].copy()
    img1 = img[1::2].copy()
    img0 =cv2.resize(img0, out_size[::-1])
    img1 =cv2.resize(img1, out_size[::-1])
    return img0, img1

def multiclass_masks_to_binary(img_list):
    bin_mask = np.full(img_list[0].shape[:2], False, dtype=bool)
    
    for mask_img in img_list:
        bin_mask = (bin_mask | (mask_img>0))    
    return bin_mask