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

import numpy as np

import torch
import torch.optim as optim
import torchvision.transforms as transforms
import torch.backends.cudnn as cudnn
from torch.utils import data

import human_parse.networks as networks
import human_parse.utils.schp as schp
from human_parse.datasets.datasets import LIPDataSet
from human_parse.datasets.target_generation import generate_edge_tensor
from human_parse.utils.transforms import BGR2RGB_transform
from human_parse.utils.criterion import CriterionAll
from human_parse.utils.encoding import DataParallelModel, DataParallelCriterion
from human_parse.utils.warmup_scheduler import SGDRScheduler


args = {}
args['arch'] = 'resnet101'


class Handler():
    def __init__(self, opt):
        self.opt = opt

        self.multi_scales = [float(i) for i in args.multi_scales.splt(',')]
        self.gpus = [int(i) for i in args.gpu.split(',')]
        cudnn.benchmark = True
        cudnn.enabled = True
        
        h, w = map(int, args.input_size.split(','))
        self.input_size = [h, w]

        self.model = networks.init_model(args.arch, num_classes=args.num_classes, pretrained=None)

        self.IMAGE_MEAN = self.model.mean
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
        
        state_dict = torch.load(args.model_restore)['state_dict']
        from collections import OrderedDict
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]
            new_state_dict[name] = v
        self.model.load_state_dict(new_state_dict)
        self.model.cuda()
        self.model.eval()

        sp_results_dir = os.path.join(args.log_dir, 'sp_results')
        if not os.path.exists(sp_results_dir):
            os.makedirs(sp_results_dir)
        
        palette = self.get_palette(20)
        parsing_preds = []
        scales = np.zeros((1, 2), dtype=np.float32)
        centers = np.zeros((1, 2), dtype=np.int32)


    def get_palette(num_cls):
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


    def multi_scale_testing(model, batch_input_im, crop_size=[473, 473], flip=True, multi_scales=[1]):
        flipped_idx = (15, 14, 17, 16, 19, 18)
        if len(batch_input_im.shape) > 4:
            batch_input_im = batch_input_im.squeeze()
        if len(batch_input_im.shape) == 3:
            batch_input_im = batch_input_im.unsqueeze(0)

        interp = torch.nn.Upsample(size=crop_size, mode='bilinear', align_corners=True)
        ms_outputs = []
        for s in multi_scales:
            interp_im = torch.nn.Upsample(scale_factor=s, mode='bilinear', align_corners=True)
            scaled_im = interp_im(batch_input_im)
            parsing_output = model(scaled_im)
            parsing_output = parsing_output[0][-1]
            output = parsing_output[0]
            if flip:
                flipped_output = parsing_output[1]
                flipped_output[14:20, :, :] = flipped_output[flipped_idx, :, :]
                output += flipped_output.flip(dims=[-1])
                output *= 0.5
            output = interp(output.unsqueeze(0))
            ms_outputs.append(output[0])
        ms_fused_parsing_output = torch.stack(ms_outputs)
        ms_fused_parsing_output = ms_fused_parsing_output.mean(0)
        ms_fused_parsing_output = ms_fused_parsing_output.permute(1, 2, 0)  # HWC
        parsing = torch.argmax(ms_fused_parsing_output, dim=2)
        parsing = parsing.data.cpu().numpy()
        ms_fused_parsing_output = ms_fused_parsing_output.data.cpu().numpy()
        return parsing, ms_fused_parsing_output
