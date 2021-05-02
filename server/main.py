import os

import numpy as np

import torch
from torch.autograd import Variable

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename


app = Flask(__name__)
SIZE=320
NC=14


@app.route('/')
def test_page():
    return render_template('index.html')


@app.route('/img_upload', methods=['GET', 'POST'])
def image_upload():
    if request.method == 'POST':
        i = request.files['img_file']
        dest = 'img_upload/' + secure_filename(i.filename)
        i.save(dest)
        '''
        이미지 처리 부분
        '''
        return '{} uploaded'.format(dest)


if __name__ == "__main__":
    app.run(host='202.31.200.237',
            port=8080,
            debug=True)
