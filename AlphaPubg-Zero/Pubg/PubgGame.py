from PubgLogic import Board, WHITE, BLACK, EMPTY
from Game import Game
import numpy as np

class PubgGame(Game):
    def __init__(self, n):
        self.n = n

    def getInitBoard(self, cannoicalBoard = None):
        board = Board(self.n, cannoicalBoard)
        return np.array(board.pieces)
    
    def getBoardSize(self):
        return (self.n, self.n)
    
    def getActionSize(self, color):
        """
        ？？？
        Input:
            color: the color of current player
        Returns:
            actionSize: number of all possible actions
        """
        return self.board.getAllLegalMoves(color);
    
    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player ()

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        board = Board(self.n, np.copy(board))
        board.executeMove(action["orig"], action["dest"])
        return (np.copy(board.pieces), -player)

    def getValidMoves(self, board, player):
        """
        ？？？
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        board = Board(self.n, np.copy(board))
        return board.getAllLegalMoves(player);

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

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
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
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