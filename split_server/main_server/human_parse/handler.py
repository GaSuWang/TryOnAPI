#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :   Peike Li
@Contact :   peike.li@yahoo.com
@File    :   train.py
@Time    :   8/4/19 3:36 PM
@Desc    :
@License :   This source code is licensed under the license found in the
             LICENSE file in the root directory of this source tree.
"""

import os
import json
import timeit
import argparse

from PIL import Image
import numpy as np

import torch
import torch.optim as optim
import torchvision.transforms as transforms
import torch.backends.cudnn as cudnn
from torch.utils import data

from collections import OrderedDict
import human_parse.networks as networks
import human_parse.utils.schp as schp
from human_parse.utils.transforms import BGR2RGB_transform, transform_parsing
from human_parse.utils.encoding import DataParallelModel, DataParallelCriterion
from human_parse.utils.warmup_scheduler import SGDRScheduler
from human_parse.data.data_dict import DataDictionary


class Handler():
    def __init__(self, opt):
        self.opt = opt

        self.multi_scales = [1]
        self.gpus = [int(i) for i in opt.gpu.split(',')]
        cudnn.benchmark = True
        cudnn.enabled = True
        
        h, w = map(int, opt.input_size.split(','))
        self.input_size = [h, w]

        self.model = networks.init_model(opt.arch, num_classes=opt.num_classes, pretrained=None)

        self.IMAGE_MEAN = [0.406, 0.456, 0.485]
        self.IMAGE_STD = self.model.std
        self.INPUT_SPACE = self.model.input_space

        if self.INPUT_SPACE == 'BGR':
            transform = transforms.Compose([transforms.ToTensor(),
                                            transforms.Normalize(mean=self.IMAGE_MEAN,
                                                                 std=self.IMAGE_STD)])
        if self.INPUT_SPACE == 'RGB':
            transform = transforms.Compose([transforms.ToTensor(),
                                            self.BGR2RGB_transform(),
                                            transforms.Normalize(mean=self.IMAGE_MEAN,
                                                                 std=self.IMAGE_STD)])
        self.data_dict = DataDictionary(crop_size=self.input_size, transform=transform)
        
        state_dict = torch.load(opt.model_restore)['state_dict']
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]
            new_state_dict[name] = v
        self.model.load_state_dict(new_state_dict)
        self.model.cuda()
        self.model.eval()

    def get_palette(self, num_cls):
        """ Returns the color map for visualizing the segmentation mask.
        Args:
            num_cls: Number of classes
        Returns:
            The color map
        """
        n = num_cls
        palette = [0] * (n * 3)
        for j in range(0, n):
            lab = j
            palette[j * 3 + 0] = 0
            palette[j * 3 + 1] = 0
            palette[j * 3 + 2] = 0
            i = 0
            while lab:
                palette[j * 3 + 0] |= (((lab >> 0) & 1) << (7 - i))
                palette[j * 3 + 1] |= (((lab >> 1) & 1) << (7 - i))
                palette[j * 3 + 2] |= (((lab >> 2) & 1) << (7 - i))
                i += 1
                lab >>= 3

        return palette
    
    def predict(self, img_path):
        image, meta = self.data_dict.make_dict(img_path)
        palette = self.get_palette(20)
        
        with torch.no_grad():
            c = meta['center'][0]
            s = meta['scale'][0]
            w = meta['width']
            h = meta['height']

            scales = np.zeros((1, 2), dtype=np.float32)
            centers = np.zeros((1, 2), dtype=np.int32)
            scales[0, :] = s
            centers[0, :] = c

            parsing_result = transform_parsing(parsing, c, s, w, h, self.input_size)
            output_img = Image.fromarray(np.asarray(parsing_result, dtype=np.uint8))
            output_img.putpalette(palette)
            output_img.convert('L')
        
        return output_img
