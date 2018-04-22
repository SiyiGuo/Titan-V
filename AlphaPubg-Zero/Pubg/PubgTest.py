from PubgGame import PubgGame as Game
from PubgLogic import Board as Board
import numpy as np
g = Game(8)
test = np.array([
            [9,0,0,0,0,0,0,9],
            [0,0,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,0],
            [0,-1,0,1,0,0,0,0],
            [0,0,1,0,-1,0,0,0],
            [0,0,0,0,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [9,0,0,0,0,0,0,9],
        ])
board = g.getInitBoard(obBoard = test) #load the gam setup
b1 = Board(8, board)
print(b1.pieces)

print(g.getBoardSize())
print(g.getActionSize())


#get move for one piece
print(b1.getValidMoveForPiece((4,2))) #row, column

#get Valid Moves
print(np.array(g.getValidMoves(board, 1)[:-1]).reshape(8,8,8))

print(g.getGameEnded(board, 1))

print(g.getCanonicalForm(board, 1))
print(g.getCanonicalForm(board, -1))
