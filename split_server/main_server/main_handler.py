import os

import cv2
from PIL import Image


class MainHandler():
    def __init__(self, opt, parse_handler, mask_handler, ps_handler, dir_C):
        self.opt = opt
        self.parse_handler = parse_handler
        self.mask_handler = mask_handler
        self.ps_handler = ps_handler
        self.dir_C = dir_C

        self.fine_height = 256
        self.fine_width = 192
        self.radius = 5
        self.json_format1 = '{"version": 1.0, "people": [{"face_keypoints": [], "pose_keypoints": '
        self.josn_format2 = ', "hand_right_keypoints": [], "hand_left_keypoints": []}]}'

    def generate_image(self, user_imgpath, clothes_imgname, img_name):
        path = os.path.join('results/', img_name)
        user_img = cv2.imread(user_imgpath, cv2.IMREAD_COLOR)
        user_img = cv2.resize(user_img, dsize=(192, 256), interpolation=cv2.INTER_AREA)
        A = self.parse_handler.predict(user_img)
        A.convert('L').save(path + '_A.png')

        B = Image.open(user_imgpath).convert('RGB')
        B.save(path + '_B.png')

        clothes_img = cv2.imread(clothes_imgname, cv2.IMREAD_COLOR)
        clothes_img = cv2.resize(clothes_img, dsize=(192, 256), interpolation=cv2.INTER_AREA)
        C = Image.fromarray(clothes_img).convert('RGB')
        C.save(path + '_C.png')

        E = self.mask_handler.predict(clothes_img)
        E = Image.fromarray(E)
        E.save(path + '_E.png')

        conf = self.ps_handler.predict(user_img)
        with open(path + '_keypoints.json', 'w') as f:
            f.write(self.get_json_dat(conf))

    def get_json_dat(self, conf):
        res = self.json_format1 + str(conf) + self.josn_format2
        return res
