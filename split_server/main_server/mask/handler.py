import numpy as np
import cv2


class Handler():
    def __init__(self):
        pass

    def predict(self, image):
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        rect = (1, 1, mask.shape[1], mask.shape[0])
        fgModel = np.zeros((1, 65), dtype=np.float64)
        bgModel = np.zeros((1, 65), dtype=np.float64)
        (mask, bgModel, fgModel) = cv2.grabCut(image, mask, rect, bgModel,
                                               fgModel, iterCount=10, mode=cv2.GC_INIT_WITH_RECT)
        outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1)
        outputMask = (outputMask * 255).astype(np.uint8)

        return outputMask
