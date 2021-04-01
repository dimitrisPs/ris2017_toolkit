import numpy as np
def iou(prediction, reference, index=255, eps=1e-8):
    assert prediction.shape == reference.shape
    prediction = prediction.astype(np.float32)
    reference = reference.astype(np.float32)

    intersection = (prediction==index) & (reference==index)
    union = (prediction==index) | (reference==index)

    return (np.sum(intersection)+eps)/(np.sum(union)+eps)