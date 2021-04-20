import numpy as np


def iou(prediction, reference, index=255, eps=1e-8):
    assert prediction.shape == reference.shape
    prediction = prediction.astype(np.float32)
    reference = reference.astype(np.float32)

    intersection = (prediction==index) & (reference==index)
    union = (prediction==index) | (reference==index)

    return (np.sum(intersection)+eps)/(np.sum(union)+eps)


def rgb_std_mean(bgr_img):
    rgb = bgr_img.astype(np.float32)/255.0

    std = np.std(rgb, axis=(0,1))
    mean = np.mean(rgb, axis=(0,1))

    # opencv reads images as bgr, we need to return rgb
    return std[::-1], mean[::-1]

def binary_coverage(binary_img):
    pixel_sum = binary_img.shape[-1] * binary_img.shape[-2]
    return np.count_nonzero(binary_img)/pixel_sum
