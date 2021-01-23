import cv2
import numpy
import numpy as np
class Stereo_Rectifier:
    def __init__(self, calib):
        self.calib = calib.copy()
        self.left_rect_map = None
        self.right_rect_map = None
        self.rect_alpha = None
    
    def _compute_rectification_parameters(self):
        R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(self.calib['K1'],
                                                        self.calib['D1'],
                                                        self.calib['K2'],
                                                        self.calib['D2'],
                                                        self.calib['size'],
                                                        self.calib['R'],
                                                        self.calib['T'],
                                                        alpha=self.rect_alpha)
        
        rect_calib = {'R1': R1,'R2': R2, 'P1': P1, 'P2': P2, 'Q': Q,
                        'roi1': roi1, 'roi2': roi2, 'alpha':self.rect_alpha}
        self.calib.update(rect_calib)

    def rectify(self, left, right, alpha=-1):
        
        
        if alpha != self.rect_alpha:
            self.left_rect_map= None
            self.calib['R1'] = None
            self.rect_alpha = alpha
            
        if (self.left_rect_map is None):
            if self.calib['R1'] is None:
                self._compute_rectification_parameters()
            self.left_rect_map = cv2.initUndistortRectifyMap(self.calib['K1'],
                                                                self.calib['D1'],
                                                                self.calib['R1'],
                                                                self.calib['P1'],
                                                                self.calib['size'][::-1],
                                                                cv2.CV_32FC1)
            self.right_rect_map = cv2.initUndistortRectifyMap(self.calib['K2'],
                                                                self.calib['D2'],
                                                                self.calib['R2'],
                                                                self.calib['P2'],
                                                                self.calib['size'][::-1],
                                                                cv2.CV_32FC1)

        left_rect = cv2.remap(left, self.left_rect_map[0],
                                self.left_rect_map[1], cv2.INTER_LINEAR)
        right_rect = cv2.remap(right, self.right_rect_map[0],
                                self.right_rect_map[1], cv2.INTER_LINEAR)
        return left_rect, right_rect        
    