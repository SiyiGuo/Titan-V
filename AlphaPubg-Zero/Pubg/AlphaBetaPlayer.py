import numpy as np
import Pubg.PubgGame as pubg
import math

infinity = 9999999999999

class TestPlayer():

    def __init__(self, game, player):
        self.game = game
        self.player = player
                

    def play(self, board, turn):      
        self.alphaBetaSearch(self.game.getCanonicalForm(board, self.player), turn, 4, 0, 0, True)
        return self.bestMove

    def alphaBetaSearch(self, board, turn, depth, a, b, maximizingPlayer):
        currentP = 1 if maximizingPlayer else -1

        if len(board) == 2:
            board = board[0]
        result = self.game.getGameEnded(board, currentP, turn)
        if result != 0:
            return (1 if result*currentP == self.player else (-1))
        if depth == 0:
            return self.boardValue(board, turn, currentP)
        valids = self.game.getValidMoves(board, self.player) #8*8*8+1 vector
        if maximizingPlayer:
            v = -infinity 
            for i in range(len(valids)):
                a = i
                if valids[i]:
                    search = self.alphaBetaSearch(self.game.getNextState(board, currentP, i, turn), turn+1, depth-1, a,b,False)
                    if search > v:
                        v = search
                        self.bestMove = a
                    a = max(a,v)
                    if b <= a:
                        break
            return v   
        else:
            v = infinity 
            for i in range(len(valids)):
                if valids[i]:
                    v = min(v, self.alphaBetaSearch(self.game.getNextState(board, currentP, i, turn), turn+1, depth-1, a,b,True))
                    a = min(a,v)
                    if b <= a:
                        break
            return v       

    def boardValue(self,board,turn, currentP):
        friend = []
        enemy = []

        for i,row in enumerate(board):
            for j,x in enumerate(row):
                if x == currentP:
                    friend.append((i,j))
                elif x == -currentP:
                    enemy.append((i,j))
        diff = len(friend) - len(enemy)
        friendD = self.distancesBetween(friend)
        return np.tanh((0.1*diff+0.01*friendD))       

    def distancesBetween(self, pieces):
        distances = 0
        for x in pieces:
            distances+=self.distance(x)
        return distances
    
    def distance(self, current):
        x1,y1 = current
        x2,y2 = 3,3
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
        
