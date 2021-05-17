import cv2
import numpy as np

from human_parse.utils.transforms import get_affine_transform


class DataDictionary():
    def __init__(self, crop_size=[473, 473], transform=None):
        self.crop_size = np.asarray(crop_size)
        self.transform = transform

        self.aspect_ratio = crop_size[1] * 1. / crop_size[0]

    def _box2cs(self, box):
        x, y, w, h = box[:4]
        return self._xywh2cs(x, y, w, h)

    def _xywh2cs(self, x, y, w, h):
        center = np.zeros((2), dtype=np.float32)
        center[0] = x + w * .5
        center[1] = y + h * .5

        if w > self.aspect_ratio * h:
            h = w * 1. / self.aspect_ratio
        elif w < self.aspect_ratio * h:
            w = h * self.aspect_ratio
        
        scale = np.array([w * 1., h * 1.], dtype=np.float32)

        return center, scale
    
    def make_dict(self, img):
        img = cv2.resize(img, dsize=(473, 473), interpolation=cv2.INTER_AREA)
        h, w, _ = img.shape

        person_center, s = self._box2cs([0, 0, w - 1, h - 1])
        r = 0
        transform = get_affine_transform(person_center, s, r, self.crop_size)
        input = cv2.warpAffine(img,
                               transform,
                               (int(self.crop_size[1]), int(self.crop_size[0])),
                               flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_CONSTANT,
                               borderValue=(0, 0, 0))
        input = self.transform(input)
        meta = {'center': person_center,
                'height': h,
                'width': w,
                'scale': s,
                'rotation': r}
        
        return input, meta
