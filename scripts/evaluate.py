import argparse
import numpy as np
from pathlib import Path
from RIS.iotools import agg_paths
from RIS.metrics import iou
from tqdm import tqdm
import cv2

parser = argparse.ArgumentParser('evaluate on RIS Dataset')
parser.add_argument('--segmentation_task', help='benchmark task [binary]', default='binary')
parser.add_argument('--gt_dir', help='test dataset root directory', required=True)
parser.add_argument('--algorithm_output_dir', help='directory where the samples to evaluate are stored. The directory should have the same structure as the gt_dir', required=True)


if __name__ == '__main__':
    args = parser.parse_args()

    if args.segmentation_task == 'binary':
        prediction_paths = sorted([p for p in Path(args.algorithm_output_dir).resolve().rglob('*instrument_dataset_*/binary/*.png')])
        ref_paths = sorted([p for p in Path(args.gt_dir).resolve().rglob('*instrument_dataset_*/ground_truth/binary/*.png')])
    else:
        #aggregate paths and put them to prediction_paths and ref_paths
        raise NotImplementedError
    assert len(prediction_paths) == len(ref_paths)
    scores=dict()
    for r_p, p_p in tqdm(zip(ref_paths, prediction_paths),desc='samples', total=len(prediction_paths)):
        # define assertions
        # print(list(r_p.parents))
        dataset_name = list(r_p.parents)[2].name
        if dataset_name not in scores:
            scores[dataset_name]=[]
        
        reference = cv2.imread(str(r_p), -1)
        prediction = cv2.imread(str(p_p), -1)

        scores[dataset_name].append(iou(reference, prediction, 255))

    # aggregate_scores
    final_scores=dict()
    total_score=0
    for dataset, score_list in scores.items():
        dataset_score = np.array(score_list).mean()
        total_score+=dataset_score
        final_scores[dataset]=dataset_score
        print('{} IoU score: {}'.format(dataset, dataset_score))

    total_score = total_score/len(final_scores.keys())
    print(total_score)
