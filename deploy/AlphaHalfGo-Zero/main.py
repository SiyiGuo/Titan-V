from HalfGo.HalfGoGame import HalfGoGame as Game
from HalfGo.tensorflow.NNet import NNetWrapper as nn
from utils import *

import os
#0 is gpu with 16 pcie slots
#1 is gpu with 4 pcie slots
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
 

args = dotdict({
    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp/','checkpoint_5.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

if __name__=="__main__":
    g = Game(8)
    nnet = nn(g)

    print("Model deploy")
    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    print("Model is loaded")

