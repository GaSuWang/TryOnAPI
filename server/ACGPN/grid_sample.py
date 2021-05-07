###############################################################################
# Code from
# https://github.com/switchablenorms/DeepFashion_Try_On/blob/master/ACGPN_inference/util/image_pool.py
###############################################################################


# encoding: utf-8

import torch.nn.functional as F
from torch.autograd import Variable

def grid_sample(input, grid, canvas = None):
    output = F.grid_sample(input, grid)
    if canvas is None:
        return output
    else:
        input_mask = Variable(input.data.new(input.size()).fill_(1))
        output_mask = F.grid_sample(input_mask, grid)
        padded_output = output * output_mask + canvas * (1 - output_mask)
        return padded_output
