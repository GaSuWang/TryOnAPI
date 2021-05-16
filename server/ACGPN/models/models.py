###############################################################################
# Code from
# https://github.com/switchablenorms/DeepFashion_Try_On/blob/master/ACGPN_inference/util/image_pool.py
###############################################################################


import torch
from .pix2pixHD_model import Pix2PixHDModel, InferenceModel


def create_model(opt):
    model = Pix2PixHDModel()
    model.initialize(opt)

    return model
