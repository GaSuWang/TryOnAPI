import os

import numpy as np
import cv2
from PIL import Image, ImageDraw

import torch

from ACGPN.models.models import create_model
import ACGPN.util.util as util
from ACGPN.ops import get_params, get_transform


class DataDictionary():
    def __init__(self, opt, parse_handler, mask_handler, ps_handler, dir_C):
        self.opt = opt
        self.parse_handler = parse_handler
        self.mask_handler = mask_handler
        self.ps_handler = ps_handler
        self.dir_C = dir_C

        self.fine_height = 256
        self.fine_width = 192
        self.radius = 5

    def make_dict(self, user_imgpath, clothes_imgname):
        user_img = cv2.imread(user_imgpath, cv2.IMREAD_COLOR)
        user_img = cv2.resize(user_img, dsize=(192, 256), interpolation=cv2.INTER_AREA)
        A = self.parse_handler.predict(user_img)
        params = get_params(self.opt, A.size)
        transform_A = get_transform(self.opt, params, method=Image.NEAREST, normalize=False)
        A_tensor = transform_A(A.convert('L')) * 255.0
        A_tensor = torch.reshape(A_tensor, torch.Size((-1, 1, 256, 192)))

        B = Image.fromarray(user_img).convert('RGB')
        params = get_params(self.opt, B.size)
        transform_B = get_transform(self.opt, params)
        B_tensor = transform_B(B)
        B_tensor = torch.reshape(B_tensor, torch.Size((-1, 3, 256, 192)))

        clothes_img = cv2.imread(clothes_imgname, cv2.IMREAD_COLOR)
        clothes_img = cv2.resize(clothes_img, dsize=(192, 256), interpolation=cv2.INTER_AREA)
        C = Image.fromarray(clothes_img).convert('RGB')
        C_tensor = transform_B(C)
        C_tensor = torch.reshape(C_tensor, torch.Size((-1, 3, 256, 192)))

        E = self.mask_handler.predict(clothes_img)
        E = Image.fromarray(E)
        E_tensor = transform_A(E.convert('L'))
        E_tensor = torch.reshape(E_tensor, torch.Size((-1, 1, 256, 192)))

        conf = self.ps_handler.predict(user_img)
        pose_data = np.array(conf)
        pose_data = pose_data.reshape((-1, 3))
        point_num = pose_data.shape[0]
        pose_map = torch.zeros(point_num, self.fine_height, self.fine_width)
        r = self.radius
        im_pose = Image.new('L', (self.fine_width, self.fine_height))
        pose_draw = ImageDraw.Draw(im_pose)
        for i in range(point_num):
            one_map = Image.new('L', (self.fine_width, self.fine_height))
            draw = ImageDraw.Draw(one_map)
            point_x = pose_data[i, 0]
            point_y = pose_data[i, 1]
            if point_x > 1 and point_y > 1:
                draw.rectangle((point_x - r, point_y - r, point_x + r, point_y + r), 'white', 'white')
                pose_draw.rectangle((point_x - r, point_y - r, point_x + r, point_y + r), 'white', 'white')
            one_map = transform_B(one_map.convert('RGB'))
            pose_map[i] = one_map[0]
        P_tensor = pose_map
        print(A_tensor.shape, B_tensor.shape)
        print(C_tensor.shape, E_tensor.shape)

        input_dict = {'label': A_tensor,
                      'image': B_tensor,
                      'edge': E_tensor,
                      'color': C_tensor,
                      'pose': P_tensor}
        
        return input_dict
