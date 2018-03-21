import unittest
from HalfGoGame import *
from HalfGoLogic import *

"""
Notation Area
hacked to run first
"""
EMPTY = 0
BANNED = 0
WHITE = 1
BLACK = -1

# #Test for Half Game Logic
# board = Board(8)
# print("get_legal_moves")
# print(sorted(board.get_legal_moves(WHITE)))
# print(sorted(board.get_legal_moves(BLACK)))
# print("execute_move")
# board.execute_move((0,1), WHITE)
# board.execute_move((2,3), BLACK)
# board.execute_move((2,2), WHITE)
# print(np.array(board.pieces))
# board.execute_move((2,1), BLACK)
# print(np.array(board.pieces))
# board.execute_move((1,0), WHITE)
# board.execute_move((7,6), BLACK)
# print(np.array(board.pieces))
# print(sorted(board.get_legal_moves(WHITE)))
# print(sorted(board.get_legal_moves(BLACK)))

game = HalfGoGame(8)

print("getInitBoard")
initBoard = game.getInitBoard()
print(initBoard)

print("getBoardSize")
print(game.getBoardSize())

print("getActionSize")
print(game.getActionSize())

print("getNextState")
print(game.getNextState(initBoard, 1, 2))

print("getValidMoves")
print(game.getValidMoves(initBoard, 1))

