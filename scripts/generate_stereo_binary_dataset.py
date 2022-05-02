from pathlib import Path
import shutil
import cv2
import argparse
from tqdm import tqdm

from RIS import utils, iotools
from RIS.stereo_rectification import Stereo_Rectifier

parser = argparse.ArgumentParser('RIS 2017 dataset modifier')
parser.add_argument('src_dataset', help='root directory containing subdatasets.')
parser.add_argument('dst_dataset', help='root directory to store the resulting dataset.')
parser.add_argument('--rect_alpha', help='alpha rectification values, default is 0.', default=0., type=float)


if __name__ == '__main__':
    args = parser.parse_args()
    src_root_dir = Path(args.src_dataset)
    dst_root_dir = Path(args.dst_dataset)
    datasets = sorted([ ds for ds in src_root_dir.iterdir() if ds.is_dir()])
    for sub_ds in tqdm(datasets, desc='Dataset'):
        ds_paths = iotools.agg_paths(sub_ds)
        calib = iotools.read_calibration_txt(ds_paths['calib'])
        rectifier = Stereo_Rectifier(calib)
        save_l_dir = dst_root_dir/sub_ds.name/'left_frame'
        save_r_dir = dst_root_dir/sub_ds.name/'right_frame'
        save_gt_dir = dst_root_dir/sub_ds.name/'ground_truth'
        save_l_dir.mkdir(exist_ok=True, parents=True)
        save_r_dir.mkdir(exist_ok=True, parents=True)
        save_gt_dir.mkdir(exist_ok=True, parents=True)
        for left_img_p, right_img_p in tqdm(list(zip(ds_paths['left'], ds_paths['right'])), desc='RGB samples', leave=False):
            img_l = cv2.imread(str(left_img_p))
            img_r = cv2.imread(str(right_img_p))
            #crop and de-interlace
            img_l_c = utils.frame_crop(img_l)
            img_l_0, img_l_1 = utils.deinterlace(img_l_c, (1024,1280))
            img_r_c = utils.frame_crop(img_r)
            img_r_0, img_r_1 = utils.deinterlace(img_r_c, (1024,1280))
            
            img_rect_l, img_rect_r = rectifier.rectify(img_l_0, img_r_0, args.rect_alpha)
                        
            cv2.imwrite(str(save_l_dir/left_img_p.name), img_rect_l)
            cv2.imwrite(str(save_r_dir/right_img_p.name), img_rect_r)
            
        # rectify ground truth samples and create a the binary samples.
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
                sample_r, _ = rectifier.rectify(sample_f, sample_f, args.rect_alpha)
                # quite possibly the interpolation will mesh things up here. I need to find a
                # way to deal with it.
                gt_list.append(sample_r)
                cv2.imwrite(str(save_gt_dir/sample_p.parent.name/sample_p.name), sample_r)
            binary_mask = utils.multiclass_masks_to_binary(gt_list)
            cv2.imwrite(str(save_gt_dir/'binary'/sample_p.name), 255*binary_mask)
        
        iotools.save_calib(dst_root_dir/sub_ds.name/'stereo_calib.json',rectifier.calib)
        shutil.copy(ds_paths['mappings'], dst_root_dir/sub_ds.name/(ds_paths['mappings'].name)) 
        
