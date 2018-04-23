from Pubg.PubgLogic import Board, WHITE, BLACK, EMPTY, BANNED
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
    
    def getActionSize(self):
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
        # if turn == 128:
        #     board.shrink(turn)
        # if turn == 192:
        #     #can be optimized here
        #     board.shrink(turn)
        #     board.shrink(turn)
        
        #Move piece first
        piece_index = action // 8
        direction_index = action % 8
        direction = board.direction_combine[direction_index] #note in board, it is row, column
        y_dir, x_dir = direction

        piece_column, piece_row = piece_index //8, piece_index % 8
        # print("Pubg Game, turn:%s, action:%s, piece_index:%s, piece_cor:%s, %s, direction_index:%s, direction:%s"%(turn, action, piece_index, piece_column, piece_row, direction_index, direction))
        action = {}
        action["orig"] = (piece_column, piece_row)
        action["dest"] = (piece_column + x_dir, piece_row + y_dir)
        # print("Pubg Game Piece:%s, %s, From:%s to :%s"%(piece_column, piece_row, action["orig"], action["dest"]))
        # print("PubgGame (column, row): \n%s"%board.pieces)
        board.executeMove(action["orig"], action["dest"])

        #After turn 127 has made move, shrink baord now
        if turn == 127:
            board.shrink(turn)
        if turn == 191:
            #can be optimized here
            board.shrink(turn)
            board.shrink(turn)
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
        # print("getValidMoves:\n%s"%board.reshape(8,8))
        board = Board(self.n, np.copy(board))
        for x in range(self.n):
            for y in range(self.n):
                if board.pieces[y][x] == player: #column, row -> row, column, as board.pieces is in PubgLogic
                    # print("getValidMoves: place:%s, %s, player:%s"%(x,y, player))
                    pieceMove = board.getValidMoveForPiece((x,y))
                    moves += pieceMove #pass in column, row index
                    # print("getValidMoves: moves:%s"%pieceMove)
                else:
                    moves += [0] * 8
        #for bias vector
        moves += [0]
        assert(len(moves) == 8*8*8+1)
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
        blackCount, whiteCount = board.countPieces()
        
        if whiteCount < 2 and blackCount < 2:
            return 0
        if whiteCount < 2:
            return BLACK*player
        if blackCount < 2:
            return WHITE*player
        
        return 0

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

        #TODO: Resolve the BANNED Place
        result = player*board
        result[result == -9] = BANNED
        return result

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
        assert(len(pi) == 8*8*8+1)  # 1 for pass
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