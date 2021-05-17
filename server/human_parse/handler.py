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

import cv2
from PIL import Image
import numpy as np

import torch
import torchvision.transforms as transforms
import torch.backends.cudnn as cudnn

from collections import OrderedDict
import human_parse.networks as networks
from human_parse.data.data_dict import DataDictionary
from human_parse.utils.transforms import transform_logits


class Handler():
    def __init__(self, opt):
        self.opt = opt

        self.multi_scales = [1]
        self.gpus = [int(i) for i in opt.gpu.split(',')]
        cudnn.benchmark = True
        cudnn.enabled = True
        
        h, w = map(int, opt.input_size.split(','))
        self.input_size = [h, w]

        self.model = networks.init_model('resnet101', num_classes=20, pretrained=None)

        self.IMAGE_MEAN = [0.406, 0.456, 0.485]
        self.IMAGE_STD = [0.225, 0.224, 0.229]
        self.img_size = (256, 192)

        transform = transforms.Compose([transforms.ToTensor(),
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

        self.trans_dict = {
            0:0,
            1:1, 2:1,
            5:4, 6:4, 7:4, 
            18:5,
            19:6,
            9:8, 12:8,
            16:9,
            17:10,
            14:11,
            4:12, 13:12,
            15:13
        }
    
    def predict(self, img):
        image, meta = self.data_dict.make_dict(img)
        
        with torch.no_grad():
            c = meta['center'][0]
            s = meta['scale'][0]
            w = meta['width']
            h = meta['height']
            image = torch.reshape(image, (1, 3, 473, 473))
            output = self.model(image.cuda())
            upsample = torch.nn.Upsample(size=torch.Size((473, 473)), mode='bicubic', align_corners=True)
            upsample_output = upsample(output[0][-1][0].unsqueeze(0))
            upsample_output = upsample_output.squeeze()
            upsample_output = upsample_output.permute(1, 2, 0)

            logits_result = transform_logits(upsample_output.data.cpu().numpy(), c, s, w, h, input_size=[473, 473])
            parsing_result = np.argmax(logits_result, axis=2)
            output_arr = np.asarray(parsing_result, dtype=np.uint8)
            
            new_arr = np.full(output_arr.shape, 7)
            for old, new in self.trans_dict.items():
                new_arr = np.where(output_arr == old, new, new_arr)
            output_img = cv2.resize(np.asarray(new_arr, dtype=np.uint8), dsize=(192, 256), interpolation=cv2.INTER_AREA)
            output_img = Image.fromarray(output_img)
        
        return output_img
