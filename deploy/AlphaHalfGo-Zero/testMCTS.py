import math
import numpy as np
from HalfGo.HalfGoLogic import BLACK, WHITE
import time
class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.nnet = nnet


    def search(self, canonicalBoard, turn):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propogated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propogated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """
        # cannonicalboard: on this board, 1=WHITE=Friendly, -1=BLACK=Enemy
        # each level of search, we substitute ourself into the enemy
        print(canonicalBoard)
        P, v = self.nnet.predict(canonicalBoard, turn)
        print(P,v) 
        abc = input()