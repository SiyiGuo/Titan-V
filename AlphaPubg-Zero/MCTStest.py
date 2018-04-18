from MCTS import *
from utils import *
import numpy as np

from HalfGo.HalfGoGame import HalfGoGame as Game
from HalfGo.tensorflow.NNet import NNetWrapper as nn

args = dotdict({
    'numIters': 1000, #number of rounds the traning will be
    'numEps': 100,    #number of self-play in each round
    'tempThreshold': 25,
    'updateThreshold': 0.6, #if new nnet beat wins old nnet above this ration, update to new nnet
    'maxlenOfQueue': 200000, #TODO: maximum length of the history in memory??
    'numMCTSSims': 25, #number of MCTS simulation rounds
    'arenaCompare': 40,
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

g = Game(8)
nnet = nn(g)
mcts = MCTS(g, nnet, args)

initBoard = g.getInitBoard()
canonicalForm = g.getCanonicalForm(initBoard, 1)
turn = 0

pi = mcts.getActionProb(canonicalForm, 0)
sym = g.getSymmetries(canonicalForm, pi)

