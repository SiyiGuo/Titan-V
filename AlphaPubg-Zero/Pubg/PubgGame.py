from PubgLogic import Board, WHITE, BLACK, EMPTY
from Game import Game
import numpy as np


#coordinate system: (column, row)
class PubgGame(Game):
    def __init__(self, n):
        self.n = n

    def getInitBoard(self, obBoard = None):
        board = Board(self.n, obBoard)
        return np.array(board.pieces)
    
    def getBoardSize(self):
        return (self.n, self.n)
    
    def getActionSize(self, color):
        """
        64 piece each with 8 direction
        +1 for the bias of pi vector
        """
        return 8*8*8 + 1
    
    def getNextState(self, board, player, action, turn):
        """
        Input:
            board: current board as np array
            player: current player (1 or -1)
            action: an Integer Number

        Returns:
            nextBoard: board after applying action,
            nextPlayer: player who plays in the next turn (should be -player)
        
        Turn1: turn = 0
        Turn 128: turn = 127
        First Shrink
        Turn 129: turn = 128
        Turn 192: turn = 191
        Second Srhink
        Turn 193: turn = 192
        """
        board = Board(self.n, np.copy(board))
        if turn == 128:
            board.shrink(turn)
        if turn == 192:
            #can be optimized here
            board.shrink(turn)
            board.shrink(turn)
        board.executeMove(action["orig"], action["dest"])
        return (np.copy(board.pieces), -player)

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player's color

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        moves = []
        board = Board(self.n, np.copy(board))
        for x in range(self.n):
            for y in range(self.n):
                if self.board[y][x] == player:
                    moves += board.getValidMoveForPiece(x,y)
        #for bias vector
        moves += [0]
        assert(len(moves) = 8*8*8+1)
        return moves

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1(WHITE) or -1(BLACK))

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.
               
        """
        board = Board(self.n, np.copy(board))
        blackCount, whiteCount = board.countPieces
        
        if whiteCount < 2 and blackCount < 2:
            return 0
        if whiteCount < 2:
            return BLACK*player
        if blackCount < 2:
            return WHITE*player

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        return player*board

    def getSymmetries(self, board, pi):
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (8, 8, 8))
        l = []
        for j in [True, False]:
            newB = board
            newPi = pi_board
            if j:
                newB = np.fliplr(newB)
                newPi = np.fliplr(newPi)

            l+= [(newB, list(newPi.ravel())+[pi[-1]])]
        return l

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        return board.tostring()