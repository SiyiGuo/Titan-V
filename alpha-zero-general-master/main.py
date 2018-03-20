from Coach import Coach
from othello.OthelloGame import OthelloGame as Game
from othello.tensorflow.NNet import NNetWrapper as nn
from utils import *

args = dotdict({
    'numIters': 1000, #number of rounds the traning will be
    'numEps': 100,    #number of self-play in each round
    'tempThreshold': 15,
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

if __name__=="__main__":
    g = Game(6)
    nnet = nn(g)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
