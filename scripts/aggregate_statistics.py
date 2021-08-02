from pathlib import Path
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from RIS.iotools import agg_paths
from RIS.metrics import rgb_std_mean, binary_coverage

parser = argparse.ArgumentParser('Compute dataset statistics')
parser.add_argument('root_dir', help="dataset's train directory, containing test and train folders")



datasets= ['instrument_dataset_1',
           'instrument_dataset_2',
           'instrument_dataset_3',
           'instrument_dataset_4',
           'instrument_dataset_5',
           'instrument_dataset_6',
           'instrument_dataset_7',
           'instrument_dataset_8',
           'instrument_dataset_9',
           'instrument_dataset_10']




if __name__=='__main__':

    args = parser.parse_args()
    root_dir = Path(args.root_dir)

    image_paths=dict()
    binary_paths=dict()

    dataset_stats=dict()

    for dataset in datasets:
        image_paths[dataset] = sorted([p for p in root_dir.rglob('*/'+dataset+'/left_frame/*.png')])
    
    for dataset in datasets:
        binary_paths[dataset] = sorted([p for p in root_dir.rglob('*/'+dataset+'/ground_truth/binary/*.png')])


    for dataset, pathlist in tqdm(image_paths.items(), total=len(image_paths.keys()), desc='computing color statistics for dataset: '):
        # keep a running average
        dataset_std_ra =np.zeros(3) 
        dataset_mean_ra = np.zeros(3)
        for path in tqdm(pathlist, desc='sample', leave=False):
            std, mean = rgb_std_mean(cv2.imread(str(path)))
            dataset_std_ra +=std
            dataset_mean_ra +=mean
        dataset_mean_ra /= len(pathlist)
        dataset_std_ra /= len(pathlist)
        dataset_stats[dataset]={'std':dataset_std_ra, 'mean':dataset_mean_ra}

    for dataset, pathlist in tqdm(binary_paths.items(), total=len(binary_paths.keys()), desc='computing binary coverage statistics for dataset: '):
        # keep a running average
        percent_coverage_ra = 0
        for path in tqdm(pathlist, desc='sample', leave=False):
            percent_coverage_ra += binary_coverage(cv2.imread(str(path), -1))
        percent_coverage_ra /= len(pathlist)
        dataset_stats[dataset]['coverage']=percent_coverage_ra

    # for every dataset compute load left samples, compute color statistics and store them in a dict


    global_std=np.zeros(3)
    global_mean=np.zeros(3)
    global_coverage=0
    for dataset, statistics in dataset_stats.items():
        print('{} statistics:\t std: {}\t mean: {}\t binary coverage: {}'.format(dataset,
                                                                                 statistics['std'],
                                                                                 statistics['mean'],
                                                                                 statistics['coverage']))
        global_std += statistics['std']
        global_mean += statistics['mean']
        global_coverage += statistics['coverage']



    global_std /= len(dataset_stats.keys())
    global_mean /= len(dataset_stats.keys())
    global_coverage /= len(dataset_stats.keys())

    print("std: {}\tmean: {}\t coverage: {}".format(global_std, global_mean, global_coverage))



