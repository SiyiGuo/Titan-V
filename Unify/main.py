from Coach import Coach
from HalfGo.HalfGoGame import HalfGoGame
from HalfGo.tensorflow.NNet import NNetWrapper as hnn
from Pubg.PubgGame import PubgGame
from Pubg.tensorflow.NNet import NNetWrapper as pnn
from utils import *

import os
#0 is gpu with 16 pcie slots
#1 is gpu with 4 pcie slots
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
 

Half_Go_args = dotdict({
    'numIters': 1000, #number of rounds the traning will be
    'numEps': 100,    #number of self-play in each round
    'tempThreshold': 25,
    'updateThreshold': 0.525, #if new nnet beat wins old nnet above this ration, update to new nnet 21 out of 40
    'maxlenOfQueue': 200000, #TODO: maximum length of the history in memory??
    'numMCTSSims': 25, #number of MCTS simulation rounds
    'arenaCompare': 40, #num of game New Model VS Old Model will play
    'cpuct': 1,

    'load_model': True,
    'checkpoint': './temp_Half_Go/',
    'load_folder_file': ('./temp_Half_Go/','checkpoint_103.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

Pubg_args = dotdict({
    'numIters': 1000, #number of rounds the traning will be
    'numEps': 100,    #number of self-play in each round
    'tempThreshold': 25,
    'updateThreshold': 0.55, #if new nnet beat wins old nnet above this ration, update to new nnet 21 out of 40
    'maxlenOfQueue': 10000, #TODO: maximum length of the history in memory??
    'numMCTSSims': 10, #number of MCTS simulation rounds
    'arenaCompare': 10, #num of game New Model VS Old Model will play
    'cpuct': 1,

    'load_model': True,
    'checkpoint': './temp_Pubg/',
    'load_folder_file': ('./temp_Pubg/','checkpoint_103.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})




if __name__=="__main__":
    halfGo = HalfGoGame(8)
    half_go_nnet = hnn(g)
    if Half_Go_args.load_model:
        half_go_nnet.load_checkpoint(Half_Go_args.load_folder_file[0], Half_Go_args.load_folder_file[1])

    pubG = PubgGame(8)
    pubg_nnet = pnn(g)
    if Pubg_args.load_model:
        pubg_nnet.load_checkpoint(Pubg_args.load_folder_file[0], Pubg_args.load_folder_file[1])

    

    c = Coach(halfGo, half_go_nnet, Half_Go_args,
                pubG, pubg_nnet, Pubg_args)

    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
