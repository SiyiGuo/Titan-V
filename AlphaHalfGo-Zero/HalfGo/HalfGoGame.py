from __future__ import print_function
import sys
import os
sys.path.append("..")
from Game import Game
import numpy as np
try:
    from .HalfGoLogic import Board, EMPTY, BANNED, WHITE, BLACK, CORNER
except ImportError:
    from HalfGoLogic import Board, EMPTY, BANNED, WHITE, BLACK, CORNER

from .AlphaBetaPlayer import AbpPlayer

from .PubgGame import PubgGame
from .PubgArena import Arena
pubg = PubgGame(8)
abp2 = AbpPlayer(pubg, 1, abpDepth = 2).play
endEvaluator = Arena(abp2, abp2, pubg)


class HalfGoGame(Game):
    def __init__(self, n):
        self.n = n

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        """
        use in: 
            for action in range(getActionsize)
        return:
            total number of valid action
        Note:
            somehow there is self.n*self.n + 1 in all Othello and Gobang
            Implementation, why?
            Answer:
                64 notes in the final layer of CNN,
                need to +1 for the bias
                this is why return self.n*self.n + 1
        """

        return self.n*self.n + 1

    def blackActionConverter(self, action):
        """
        input: action, canonical board action
        output: black's real action
        !!!
        NOTICE: pi vector and valid action is GROUP BY ROW!!!!!
        """
        return 63 - action

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        # 2 = (2,0)
        # currently action = an Integer
        if action == self.n*self.n: 
            return (board, -player)
        b = Board(self.n)
        b.pieces = np.copy(board)
        #even in string representation, we concat column by column
        #picese are grouped by column
        move = (action%self.n, action//self.n,) #(column, row) (int(a/b))
        b.execute_move(move, player)

        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        # moves, on the same ROWWWWWWWWWWW are grouped together
        valids = [0]*self.getActionSize()
        b = Board(self.n)
        b.pieces = np.copy(board)
        legalMoves =  b.get_legal_moves(player) #in the form (column, row)
        if len(legalMoves)==0:
            valids[-1]=1
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n*y+x]=1 #since all rows are grouped together
        return np.array(valids)

    def getGameEnded(self, board, player, turn, end_Evaluate = False):
        """
        Input:
            board: cannoical board
            player: int, 1 = white, -1 = black
            turn: [0.......23] = 24 turns in total = for i in range(0,24)
        return:
            0 nothing
            1 player Won
            -1 player Lost
        """
        if end_Evaluate:
            print("Start Board:\n%s"%(np.array(board).reshape(8,8)))
            result = endEvaluator.playGame(board)
            return result
        else:
            b = Board(self.n)
            b.pieces = np.copy(board)
            if turn < 24: #4: for adding turn parameter
                return 0
            else:
                if b.countDiff(player) > 0:
                    return 1
                elif b.countDiff == 0:
                    return 1e-4 #tie condiitiion
            
            return -1

    def getCanonicalForm(self, board, player):
        """
        Input:
            Board, 
            player: the perspective
        return:
            current situation of the board in the player's point of view
            1 = friendly army
            -1 = enemy
        Yes! this is correct understanding
        """
        # return player*board
        board = np.array(board).reshape(8,8)
        result = player*board
        result[result == -3] = CORNER
        if player == BLACK:
            result = np.rot90(result, k = 2)
        return result#.flatten()

    def getSymmetries(self, board, pi):
        """
        Due to nature of HalfGo, We only flip the board accoring to vertical middle line
        This function is trying to generate more traning example from a single game
        For half go, each game = 2 tranining example.

        Input:
            board: current board
            pi: policy vector of size self.getActionSize() (64)

        Returns:
            symmForms: a list of [(board,pi)] where 
                       each tuple is
                         a symmetrical form of the board 
                       and the 
                         corresponding pi vector. 
                       This is used when training the neural network from examples.
        """
        # mirror
        assert(len(pi) == self.n**2 + 1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for j in [True, False]:
            newB = board
            newPi = pi_board
            if j:
                #np.fliplr flip the matrix
                newB = np.fliplr(newB) 
                newPi = np.fliplr(newPi)
            
            #np.ravel: turn matrix into one row
            l += [(newB, list(newPi.ravel()) + [pi[-1]])] 
        return l

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    def getScore(self, board, player):
        """
        Input:
            board: np array
            player: WHITE BLACK
        return:
            score of player
        """
        b = Board(self.n)
        b.pieces = np.copy(board)
        return b.countDiff(player)

def display(board):
    n = board.shape[0]

    print ("   ",end="")
    for y in range(n):
        print ("%s "%y,end="")
        
    print("")
    print(" -----------------------")
    for y in range(n):
        print(y, "|",end="")    # print the row #
        for x in range(n):
            piece = board[y][x]    # get the piece to print
            if piece == -1: print("b ",end="")
            elif piece == 1: print("W ",end="")
            else:
                if x==n:
                    print("-",end="")
                else:
                    print("- ",end="")
        print("|")

    print("   -----------------------")