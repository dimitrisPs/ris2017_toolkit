from pathlib import Path
import shutil
import cv2
import numpy as np
import argparse
from tqdm import tqdm

from RIS import utils, iotools
from RIS.stereo_rectification import Stereo_Rectifier

parser = argparse.ArgumentParser('RIS 2017 dataset cleaner')
parser.add_argument('src_dataset', help='root directory containing subdatasets.')
parser.add_argument('dst_dataset', help='root directory to store the resulting dataset.')


if __name__ == '__main__':
    args = parser.parse_args()
    src_root_dir = Path(args.src_dataset)
    dst_root_dir = Path(args.dst_dataset)
    datasets = sorted([ ds for ds in src_root_dir.iterdir() if ds.is_dir()])
    for sub_ds in tqdm(datasets, desc='Dataset'):
        ds_paths = iotools.agg_paths(sub_ds)
        save_l_dir = dst_root_dir/sub_ds.name/'left_frame'
        save_gt_dir = dst_root_dir/sub_ds.name/'ground_truth'
        save_l_dir.mkdir(exist_ok=True, parents=True)
        save_gt_dir.mkdir(exist_ok=True, parents=True)
        for left_img_p in tqdm(ds_paths['left'], desc='RGB samples', leave=False):
            img_l = cv2.imread(str(left_img_p))
            #crop and de-interlace

            img_l_c = utils.frame_crop(img_l)
            img_l_0, img_l_1 = utils.deinterlace(img_l_c, (1024,1280))
                      
            cv2.imwrite(str(save_l_dir/left_img_p.name), img_l_0)
            
        # generate ground truth binary masks. 
        ground_truth_path_dict = ds_paths['ground_truth']
        ground_truth_dst_dirs = [save_gt_dir/name for name in ds_paths['ground_truth'].keys()]
        ground_truth_dst_dirs.append(save_gt_dir/'binary')
        for p in ground_truth_dst_dirs:
            p.mkdir(parents=True, exist_ok=True)
        
        ground_truth_paths = [path_lst for path_lst in ds_paths['ground_truth'].values()]
        for gt_samples in tqdm(zip(*ground_truth_paths), desc='ground truth samples', leave=False, total = len(ground_truth_paths[0])):
            gt_list=[]
            for sample_p in gt_samples:
                # crop resize , rectify and add it to binary mask
                sample = cv2.imread(str(sample_p),0)
                sample_c = utils.frame_crop(sample)
                sample_f = cv2.resize(sample_c, (1280,1024))

                gt_list.append(sample_f)
                cv2.imwrite(str(save_gt_dir/sample_p.parent.name/sample_p.name), sample_f)
            binary_mask = utils.multiclass_masks_to_binary(gt_list)
            cv2.imwrite(str(save_gt_dir/'binary'/sample_p.name), 255*binary_mask)
        
        shutil.copy(ds_paths['mappings'], dst_root_dir/sub_ds.name/(ds_paths['mappings'].name)) 
        
