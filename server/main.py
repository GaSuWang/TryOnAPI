import os
import time
import random
import string

import numpy as np
import cv2
from PIL import Image

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from options.server_options import ServerOptions

from ACGPN.handler import Handler as ACGPNHandler
from human_parse.handler import Handler as ParseHandler
from mask.handler import Handler as MaskHandler
from pose_estimator.handler import Handler as PEHandler
from data.data_dict import DataDictionary


app = Flask(__name__)

ps_checkpoints = 'pose_estimator/checkpoints'

opt = ServerOptions().parse()
acgpn_handler = ACGPNHandler(opt)
parse_handler = ParseHandler(opt)
mask_handler = MaskHandler()
pe_handler = PEHandler(ps_checkpoints)

f_filename = '{time}{rand}'
dir_C = ' data_preprocessing/test_color'
data_dict = DataDictionary(opt, parse_handler, mask_handler, pe_handler, dir_C)


'''
 For Testing
'''
@app.route('/')
def test_page():
    return render_template('test.html')


@app.route('/img_upload', methods=['GET', 'POST'])
def image_upload():
    if request.method == 'POST':
        user_img = request.files['img_file']
        clothes_imgpath = os.path.join('data_preprocessing/test_color', request.form['clothes'])
        rand_digits = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        img_name = f_filename.format(time=str(int(time.time())), rand=rand_digits)
        img_name = secure_filename(img_name)
        dest = os.path.join('img_upload/', img_name)
        user_img.save(dest)

        data = data_dict.make_dict(dest, clothes_imgpath)
        res_img = acgpn_handler.generate_image(data)
        res_path = os.path.join('results/', img_name)
        cv2.imwrite(res_path, res_img)

        return send_file(res_path, mimetype='image')
    
    else:
        return '404'


'''
 For Publishing
'''

if __name__ == "__main__":
    app.run(host='202.31.200.237',
            port=8080,
            debug=True)
