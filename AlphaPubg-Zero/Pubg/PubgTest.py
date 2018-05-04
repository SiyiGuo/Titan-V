from PubgGame import PubgGame as Game
from PubgLogic import Board as Board
import numpy as np
g = Game(8)
test = np.array([
            [3,0,0,0,0,0,0,3],
            [0,0,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,0],
            [0,-1,-1,1,0,1,0,0],
            [0,0,1,0,-1,-1,0,0],
            [0,0,0,-1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [3,0,0,0,0,0,0,3],
        ])
# board = g.getInitBoard(obBoard = test) #load the gam setup
# print(board.pieces.reshape(8,8))
# b1 = Board(8, board)
# print("Read board")
# print(b1.pieces)
#
# print("board Size")
# print(g.getBoardSize())
# print("action size")
# print(g.getActionSize())
#
#
# #get move for one piece
# print("valid move for 4,2 column, row")
# print(b1.getValidMoveForPiece((4,2))) #row, column
#
# #get Valid Moves
# # print("valid move fo white, column by column")
# # print(np.array(g.getValidMoves(board, 1)[:-1]).reshape(8,8,8))
# print("valid move fo Black, column by column")
# print(np.array(g.getValidMoves(board, -1)[:-1]).reshape(8,8,8))
#
# print("game ended")
# print(g.getGameEnded(board, 1))
#
# print("Canonical Form")
# print(g.getCanonicalForm(board, 1))
# print(g.getCanonicalForm(board, -1))

board = Board(8, obBoard = test) #load the gam setup
print(board.pieces.reshape(8,8))
board.shrink(128)
print(board.pieces.reshape(8,8))
board.shrink(192)
print(board.pieces.reshape(8,8))
