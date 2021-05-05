import os
import time
import random
import string

import numpy as np
import cv2
from PIL import Image

import torch
from torch.autograd import Variable

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from options.server_options import ServerOptions
from models.models import create_model
import util.util as util
from ops import get_params, get_transform


app = Flask(__name__)

opt = ServerOptions().parse()
model = create_model(opt)

SIZE=320
NC=14
f_filename = '{time}{rand}'

dir_A = os.path.join(opt.dataroot, opt.phase + '_label')

@app.route('/')
def test_page():
    return render_template('index.html')


@app.route('/img_upload', methods=['GET', 'POST'])
def image_upload():
    if request.method == 'POST':
        user_i = request.files['img_file']
        rand = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        A_path = 'img_upload/' + f_filename.format(time=str(int(time.time())), rand=rand)
        dest = secure_filename(A_path)
        user_i.save(dest)

        B_path = 'data_preprocessing/' + str(request.args['clothes']) + '_1.jpg'

        data = make_input_dict(A_path, B_path)
        img = generate_image(data)

        return '{} uploaded'.format(dest)


def generate_image(data):
    pass


def make_input_dict(A_path, B_path):
    A = Image.open(A_path).convert('L')
    params = get_params(opt, A.size)
    transform_A = get_transform(opt, params)
    A_tensor = transform_A(A.convert)

    B = Image.open(B_path).convert('RGB')



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


def generate_label_color(inputs):
    label_batch = []
    for i in range(len(inputs)):
        label_batch.append(util.tensor2label(inputs[i], opt.label_nc))
    label_batch = np.array(label_batch)
    label_batch = label_batch * 2 - 1
    input_label = torch.from_numpy(label_batch)

    return input_label


def complete_compose(img,mask,label):
    label=label.cpu().numpy()
    M_f=label>0
    M_f=M_f.astype(np.int)
    M_f=torch.FloatTensor(M_f).cuda()
    masked_img=img*(1-mask)
    M_c=(1-mask.cuda())*M_f
    M_c=M_c+torch.zeros(img.shape).cuda()##broadcasting
    return masked_img,M_c,M_f


def compose(label,mask,color_mask,edge,color,noise):
    masked_label=label*(1-mask)
    masked_edge=mask*edge
    masked_color_strokes=mask*(1-color_mask)*color
    masked_noise=mask*noise
    return masked_label,masked_edge,masked_color_strokes,masked_noise


def changearm(old_label, data):
    label=old_label
    arm1=torch.FloatTensor((data['label'].cpu().numpy()==11).astype(np.int))
    arm2=torch.FloatTensor((data['label'].cpu().numpy()==13).astype(np.int))
    noise=torch.FloatTensor((data['label'].cpu().numpy()==7).astype(np.int))
    label=label*(1-arm1)+arm1*4
    label=label*(1-arm2)+arm2*4
    label=label*(1-noise)+noise*4
    return label


if __name__ == "__main__":
    app.run(host='202.31.200.237',
            port=8080,
            debug=True)
