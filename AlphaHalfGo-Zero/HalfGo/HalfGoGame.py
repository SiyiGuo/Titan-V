from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from HalfGoLogic import Board
import numpy as np

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

        return self.n*self.n

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        # currently action = an Integer
        if action == self.n*self.n:
            return (board, -player)
        b = Board(self.n)
        b.pieces = np.copy(board)
        #even in string representation, we concat column by column
        #picese are grouped by column
        move = (int(action/self.n), action%self.n) #(colmn, row)
        b.execute_move(move, player)

        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(self.n)
        b.pieces = np.copy(board)
        legalMoves =  b.get_legal_moves(player)
        if len(legalMoves)==0:
            valids[-1]=1
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n*x+y]=1
        return np.array(valids)

    def getGameEnded(self, board, player, turn):
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
        b = Board(self.n)
        b.pieces = np.copy(board)
        if turn < 24:
            return 0
        else:
            if b.countDiff(player) > 0:
                return 1
        
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
        """
        return player*board

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
        # mirror, rotational
        # assert(len(pi) == self.n**2+1)  # 1 for pass as action size is 64
        pi_board = np.reshape(pi, (self.n, self.n)) #turn pi vector into board form
        l = []

        for j in [True, False]:
            newB = board
            newPi = pi_board
            if j:
                #np.fliplr flip the matrix
                newB = np.fliplr(newB) 
                newPi = np.fliplr(newPi)
            
            #np.ravel: turn matrix into one row
            l += [(newB, list(newPi.ravel()))] 
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

    for y in range(n):
        print (y,"|",end="")
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