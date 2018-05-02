import numpy as np

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board, turn):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a

class HumanPubgPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board, turn):
        # display(board)
        valid = self.game.getValidMoves(board, 1)
        __directions = [(-1,0), (1,0), (0,-1), (0,1)]
        __jumpDirections = [(-2,0), (2,0), (0,-2), (0,2)]
        direction_combine = __directions + __jumpDirections
        for i in range(len(valid)):
            if valid[i]:
                # print(int(i/self.game.n), int(i%self.game.n))
                action = i
                
                
                piece_index = action // 8
                direction_index = action % 8
                direction = direction_combine[direction_index] #note in board, it is row, column
                y_dir, x_dir = direction
                piece_column, piece_row = piece_index //8, piece_index % 8
               
                action = {}
                action["orig"] = (piece_column, piece_row)
                action["dest"] = (piece_column + x_dir, piece_row + y_dir)

                print("%s: move from %s to %s"%(i, action["orig"], action["dest"]))
        while True:
            a = int(input())

            # x,y = [int(x) for x in a.split(' ')]
            # a = self.game.n * x + y if x!= -1 else self.game.n ** 2
            if valid[a]:
                break
            else:
                print('Invalid')
        return a


class GreedyPubgPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board,turn):
        valids = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valids[a]==0:
                continue
            nextBoard, _ = self.game.getNextState(board, 1, a)
            score = self.game.getScore(nextBoard, 1)
            candidates += [(-score, a)]
        candidates.sort()
        return candidates[0][1]