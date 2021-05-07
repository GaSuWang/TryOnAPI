import os
import time
import random
import string

import numpy as np
import cv2
from PIL import Image

import torch
from torch.autograd import Variable

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from options.server_options import ServerOptions

from ACGPN.handler import Handler as ACGPNHandler
from ACGPN.models.models import create_model
import ACGPN.util.util as util
from ACGPN.ops import get_params, get_transform


app = Flask(__name__)

opt = ServerOptions().parse()
acgpn_handler = ACGPNHandler(opt)
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
        img_name = f_filename.format(time=str(int(time.time())), rand=rand)
        img_path = 'img_upload/' + img_name
        dest = secure_filename(img_path)
        user_i.save(dest)

        B_path = 'data_preprocessing/' + str(request.args['clothes']) + '_1.'

        data = make_input_dict(A_path, B_path)
        img = generate_image(data)
        cv2.imwrite('results/' + img_name, img)

        return send_file('results/' + img_name, mimetype='image')


if __name__ == "__main__":
    app.run(host='202.31.200.237',
            port=8080,
            debug=True)
