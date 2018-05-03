import Arena
from MCTS import MCTS
from Pubg.PubgGame import PubgGame, display
from Pubg.PubgPlayer import *
from Pubg.AlphaBetaPlayer import TestPlayer
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

g = PubgGame(8)

# all players
rp = RandomPlayer(g).play
gp = GreedyPubgPlayer(g).play
hp = HumanPubgPlayer(g).play
abp = TestPlayer(g, 1).play

# nnet players
# n1 = NNet(g)
# n1.load_checkpoint('./temp','best.pth.tar')
# args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
# mcts1 = MCTS(g, n1, args1)
# n1p = lambda x, turn: np.argmax(mcts1.getActionProb(x, turn, temp=0))


#n2 = NNet(g)
#n2.load_checkpoint('./temp','best.pth.tar')
#args2 = dotdict({'numMCTSSims': 25, 'cpuct':1.0})
#mcts2 = MCTS(g, n2, args2)
#n2p = lambda x, turn: np.argmax(mcts2.getActionProb(x, turn, temp=0))

arena = Arena.Arena(abp, abp, g, display=display)
oneWon, twoWon, draws = arena.playGames(3, verbose=True)
print("\n1st player win:%s, 2nd player win:%s, draw:%s"%(oneWon, twoWon, draws))
