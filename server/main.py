import os
import time
import random
import string
from glob import glob

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


ps_checkpoints = 'pose_estimator/checkpoints'

opt = ServerOptions().parse()
acgpn_handler = ACGPNHandler(opt)
parse_handler = ParseHandler(opt)
mask_handler = MaskHandler()
pe_handler = PEHandler(ps_checkpoints)

f_filename = '{time}{rand}'
dir_C = 'data_preprocessing/test_color'
data_dict = DataDictionary(opt, parse_handler, mask_handler, pe_handler, dir_C)
clothes_img = glob(dir_C + '/*.jpg')

app = Flask(__name__)


def save_request_file(req_file, dest='img_upload/'):
    rand_digits = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    f_name = f_filename.format(time=str(int(time.time())), rand=rand_digits)
    f_name = secure_filename(f_name)
    f_dest = os.path.join(dest, f_name)
    req_file.save(f_dest)

    return f_name, f_dest

'''
 For Testing
'''
@app.route('/')
def test_page():
    return render_template('test.html')


@app.route('/img_upload', methods=['GET', 'POST'])
def image_upload():
    if request.method == 'POST':
        if 'clothes' in request.form.keys():
            clothes_imgpath = clothes_img[int(request.form['clothes'])]
        elif 'clothes' in request.files.keys():
            c_img = request.files['clothes']
            _, clothes_imgpath = save_request_file(c_img)
        else:
            return 'Not Found', 404
            
        user_img = request.files['img_file']
        img_name, dest = save_request_file(user_img)

        data = data_dict.make_dict(dest, clothes_imgpath)
        res_img = acgpn_handler.generate_image(data)
        res_path = os.path.join('results/', img_name) + '.png'
        cv2.imwrite(res_path, res_img)

        return send_file(res_path, mimetype='image')
    
    else:
        print(request.method)
        return 'Not Found', 404


'''
 For Publishing
'''
@app.route('/image_query', methods=['GET'])
def image_query():
    id = int(request.args['id'])
    if id >= 0 and id < len(clothes_img):
        return send_file(clothes_img[id], mimetype='image')
    else:
        return 'Not Found', 404


if __name__ == "__main__":
    app.run(host='202.31.200.237',
            port=2010,
            debug=True)
