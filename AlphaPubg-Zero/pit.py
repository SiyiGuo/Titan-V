import Arena
from MCTS import MCTS
from Pubg.PubgGame import HalfGoGame, display
from Pubg.PubgPlayer import *
from Pubg.AlphaBetaPlayer import test_player
from Pubg.tensorflow.NNet import NNetWrapper as NNet

import numpy as np
from utils import *

import os
#0 is gpu with 16 pcie slots
#1 is gpu with 4 pcie slots
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

g = HalfGoGame(8)

# all players
rp = RandomPlayer(g).play
gp = GreedyHalfGoPlayer(g).play
hp = HumanHalfGoPlayer(g).play
abp = test_player(g).play

# nnet players
# n1 = NNet(g)
# n1.load_checkpoint('./temp','best.pth.tar')
# args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
# mcts1 = MCTS(g, n1, args1)
# n1p = lambda x, turn: np.argmax(mcts1.getActionProb(x, turn, temp=0))


n2 = NNet(g)
n2.load_checkpoint('./temp','best.pth.tar')
args2 = dotdict({'numMCTSSims': 25, 'cpuct':1.0})
mcts2 = MCTS(g, n2, args2)
n2p = lambda x, turn: np.argmax(mcts2.getActionProb(x, turn, temp=0))

arena = Arena.Arena(n2p, hp, g, display=display)
print(arena.playGames(2, verbose=True))
