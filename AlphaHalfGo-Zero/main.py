from Coach import Coach
from HalfGo.HalfGoGame import HalfGoGame as Game
from HalfGo.tensorflow.NNet import NNetWrapper as nn
from utils import *

import os
#0 is gpu with 16 pcie slots
#1 is gpu with 4 pcie slots
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
 

args = dotdict({
    'numIters': 1000, #number of rounds the traning will be
    'numEps': 100,    #number of self-play in each round
    'tempThreshold': 25,
    'updateThreshold': 0.525, #if new nnet beat wins old nnet above this ration, update to new nnet 21 out of 40
    'maxlenOfQueue': 200000, #TODO: maximum length of the history in memory??
    'numMCTSSims': 25, #number of MCTS simulation rounds
    'arenaCompare': 40, #num of game New Model VS Old Model will play
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp/','checkpoint_5.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

if __name__=="__main__":
    g = Game(8)
    nnet = nn(g)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
