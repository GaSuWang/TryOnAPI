import numpy as np
import cv2


PATH_IMG ="5.jpg"
image = cv2.imread(PATH_IMG)
mask = np.zeros(image.shape[:2], dtype="uint8")
rect = (1, 1, mask.shape[1], mask.shape[0])
fgModel = np.zeros((1, 65), dtype="float")
bgModel = np.zeros((1, 65), dtype="float")
(mask, bgModel, fgModel) = cv2.grabCut(image, mask, rect, bgModel,
                                       fgModel, iterCount=10, mode=cv2.GC_INIT_WITH_RECT)
outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD),0, 1)
outputMask = (outputMask * 255).astype("uint8")
