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

    def generate_image(self, person_path, fashion_path):
        pass

    def make_input_dict(self, A_path, B_path):
        A = Image.open(A_path).convert('L')
        params = get_params(self.opt, A.size)
        transform_A = get_transform(self.opt, params, method=Image.NEAREST, normalize=False)
        A_tensor = transform_A(A) * 255.0

        B = Image.open(B_path).convert('RGB')
        params = get_params(self.opt, B.size)
        transform_B = get_transform(self.opt, params)
        B_tensor = transform_B(B)

        E = Image.open()

    def generate_label_plain(inputs):
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

    def complete_compose(img,mask,label):
        label = label.cpu().numpy()
        M_f = label > 0
        M_f = M_f.astype(np.int)
        M_f = torch.FloatTensor(M_f).cuda()
        masked_img = img * (1 - mask)
        M_c = (1 - mask.cuda()) * M_f
        M_c = M_c + torch.zeros(img.shape).cuda()##broadcasting

        return masked_img,M_c,M_f

    def compose(label,mask,color_mask,edge,color,noise):
        masked_label = label * (1 - mask)
        masked_edge = mask * edge
        masked_color_strokes = mask * (1 - color_mask) * color
        masked_noise = mask * noise

        return masked_label, masked_edge, masked_color_strokes, masked_noise


    def changearm(old_label, data):
        label = old_label
        arm1 = torch.FloatTensor((data['label'].cpu().numpy()==11).astype(np.int))
        arm2 = torch.FloatTensor((data['label'].cpu().numpy()==13).astype(np.int))
        noise = torch.FloatTensor((data['label'].cpu().numpy()==7).astype(np.int))
        label = label * (1 - arm1) + arm1 * 4
        label = label * (1 - arm2) + arm2 * 4
        label = label * (1 - noise) + noise * 4

        return label
