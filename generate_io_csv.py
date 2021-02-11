import argparse
from pathlib import Path
import csv

parser = argparse.ArgumentParser('Create csv files containing input sample paths and destination paths')
parser.add_argument('dataset_dir', help='path to directory')
parser.add_argument('out_csv', help='path to export the path .csv file')
parser.add_argument('--binary', '-b', help='flag to include binary tool segmentation masks', action='store_true')
parser.add_argument('--disparity','-d', help='flag to include disparity', action='store_true')



def glob_paths(dataset_path:Path, binary_masks:bool=True, disparity:bool=False):
    # this function will work on both the root dataset and subdatasets.
    path_dict=dict()
    path_dict['left'] = sorted([p.resolve() for p in dataset_path.rglob('left_frame/*.png')])
    path_dict['right'] = sorted([p.resolve() for p in dataset_path.rglob('right_frame/*.png')])
    if binary_masks:
        path_dict['binary_seg'] = sorted([p.resolve() for p in dataset_path.rglob('ground_truth/binary/*.png')])
    if disparity:
        path_dict['disparity'] = sorted([p.resolve() for p in dataset_path.rglob('disparity/*.png')])
    
    #ensure all path exists
    for pathlist in path_dict.values():
        assert len(path_dict['left'])==len(pathlist)
    return path_dict
    
    
    
if __name__ == '__main__':
    args = parser.parse_args()
    out_p = Path(args.out_csv)
    dataset_dir = Path(args.dataset_dir)
    
    path_dict = glob_paths(dataset_dir, args.binary, args.disparity)
    
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, 'w') as f:
        path_writer = csv.writer(f, delimiter=',')
        path_writer.writerows(zip(*path_dict.values()))
    
    
    
    
