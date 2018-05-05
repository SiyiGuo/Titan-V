try:
    from HalfGoGame import *
    from HalfGoLogic import *  
except ImportError:
    from .HalfGoGame import *
    from .HalfGoLogic import *


"""
Notation Area
hacked to run first
"""
EMPTY = 0
BANNED = 0
WHITE = 1
BLACK = -1

#Test for Half Game Logic
# board = Board(8)
# board.execute_move((0,1), WHITE)
# print(board.pieces)
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

initBoard = game.getInitBoard()
print(game.getValidMoves(initBoard, WHITE)[:-1])
(WHITE02, nextPlayer) = game.getNextState(initBoard, WHITE, 2)
print(WHITE02)
print("nextPlayer %s"%nextPlayer)
w1 = game.getCanonicalForm(WHITE02, WHITE).reshape(8,8)
print(w1.reshape(8,8))
b1 = game.getCanonicalForm(w1, BLACK).reshape(8,8)
print(b1.reshape(8,8))
w2 = game.getCanonicalForm(b1, WHITE).reshape(8,8)
print(w2.reshape(8,8))
# print("getNextState, BLACK player place at (1,0)")
# (BLACK10, nextPlayer) = game.getNextState(initBoard, BLACK, 8)
# print(BLACK10)
# print("nextPlayer %s"%nextPlayer)

# print("getValidMoves WHITE, groups pieces with same column, so add a Transpose")
# print(game.getValidMoves(initBoard, WHITE)[:-1].reshape(8,8))
# print("WHITE valid after place (1,0)")
# print(game.getValidMoves(WHITE02, WHITE)[:-1].reshape(8,8))
# print("getValidMoves BLACK, groups pieces with same column, so add a Transpose")
# print(game.getValidMoves(initBoard, BLACK)[:-1].reshape(8,8))

# print("getGameEnded")
# print(game.getGameEnded(WHITE02, BLACK, 25))
# print(game.getGameEnded(WHITE02, BLACK, 24))
# print(game.getGameEnded(WHITE02, BLACK, 23))


# print("getCanonicalFoem")
# print(game.getCanonicalForm(WHITE02, WHITE))
# print(game.getCanonicalForm(WHITE02, BLACK))

# print("getSymmetries")
# WHITE0SYM = game.getSymmetries(WHITE02, [i for i in range(64)])
# print("After Symmetric")
# print(WHITE0SYM[0][0])
# print(np.array(WHITE0SYM[0][1]).reshape(8,8))
# print("Original Board")
# print(WHITE0SYM[1][0])
# print(np.array(WHITE0SYM[1][1]).reshape(8,8))

# print("get score")
# print(game.getScore(WHITE02, WHITE))
# print(game.getScore(WHITE02, BLACK))