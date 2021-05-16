import os
import time
import random
import string

import numpy as np
import cv2
from PIL import Image

import torch
from torch.autograd import Variable

from ACGPN.models.models import create_model
import ACGPN.util.util as util
from ACGPN.ops import get_params, get_transform


SIZE=320
NC=14
f_filename = '{time}{rand}'


class Handler():
    def __init__(self, opt):
        self.opt = opt
        
        self.model = create_model(opt)
        print(self.model.name())

    def generate_image(self, data):
        mask_clothes = torch.FloatTensor((data['label'].cpu().numpy() == 4).astype(np.int))
        mask_fore = torch.FloatTensor((data['label'].cpu().numpy() > 0).astype(np.int))
        img_fore = data['image'] * mask_fore
        all_clothes_label = self.changearm(data['label'], data)

        _, fake_image, real_image, _, _, _, _, _, _, _ = self.model(Variable(data['label'].cuda()),
                                                                    Variable(data['edge'].cuda()),
                                                                    Variable(img_fore.cuda()),
                                                                    Variable(mask_clothes.cuda()),
                                                                    Variable(data['color'].cuda()),
                                                                    Variable(all_clothes_label.cuda()),
                                                                    Variable(data['image'].cuda()),
                                                                    Variable(data['pose'].cuda()),
                                                                    Variable(data['image'].cuda()),
                                                                    Variable(mask_fore.cuda()))
        c = fake_image.float().cuda()
        cv_img = (c[0].detach().cpu().numpy() + 1) / 2
        rgb = (cv_img * 255).astye(np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        
        return bgr

    def generate_label_plain(self, inputs):
        size = inputs.size()
        pred_batch = []
        for input in inputs:
            input = input.view(1, NC, 256,192)
            pred = np.squeeze(input.data.max(1)[1].cpu().numpy(), axis=0)
            pred_batch.append(pred)

        pred_batch = np.array(pred_batch)
        pred_batch = torch.from_numpy(pred_batch)
        label_batch = pred_batch.view(size[0], 1, 256,192)

        return label_batch

    def generate_label_color(self, inputs):
        label_batch = []

        for i in range(len(inputs)):
            label_batch.append(util.tensor2label(inputs[i], self.opt.label_nc))
        
        label_batch = np.array(label_batch)
        label_batch = label_batch * 2 - 1
        input_label = torch.from_numpy(label_batch)

        return input_label

    def complete_compose(self, img, mask, label):
        label = label.cpu().numpy()
        M_f = label > 0
        M_f = M_f.astype(np.int)
        M_f = torch.FloatTensor(M_f).cuda()
        masked_img = img * (1 - mask)
        M_c = (1 - mask.cuda()) * M_f
        M_c = M_c + torch.zeros(img.shape).cuda()##broadcasting

        return masked_img,M_c,M_f

    def compose(self, label, mask, color_mask, edge, color, noise):
        masked_label = label * (1 - mask)
        masked_edge = mask * edge
        masked_color_strokes = mask * (1 - color_mask) * color
        masked_noise = mask * noise

        return masked_label, masked_edge, masked_color_strokes, masked_noise


    def changearm(self, old_label, data):
        label = old_label
        arm1 = torch.FloatTensor((data['label'].cpu().numpy()==11).astype(np.int))
        arm2 = torch.FloatTensor((data['label'].cpu().numpy()==13).astype(np.int))
        noise = torch.FloatTensor((data['label'].cpu().numpy()==7).astype(np.int))
        label = label * (1 - arm1) + arm1 * 4
        label = label * (1 - arm2) + arm2 * 4
        label = label * (1 - noise) + noise * 4

        return label
