import numpy as np
import Pubg.PubgGame as pubg
import math
import operator

infinity = 999999

class TestPlayer():
    totalWhite = 0
    totalBlack = 0
    def __init__(self, game, player):
        self.game = game
        self.player = player
                

    def play(self, board, turn):
        results = {}
        valids = self.game.getValidMoves(board, self.player)
        for i in range(len(valids)):
            if valids[i]:
                # print(i)
                results[i] = self.alphaBetaSearch(self.game.getNextState(board, 1, i, turn), turn+1, 3, 0,0,False)   
        # a = input()     
        return max(results, key=results.get)

    def alphaBetaSearch(self, board, turn, depth, a, b, maximizingPlayer):
        board, currentP = board
        board = self.game.getCanonicalForm(board, currentP)
        result = self.game.getGameEnded(board, 1, turn)
        if result != 0:
            return (1 if result*currentP == self.player else (-1)) * 10000
        if depth == 0:
            return self.boardValue(board, turn)
        valids = self.game.getValidMoves(board, self.player) #8*8*8+1 vector
        if maximizingPlayer:
            v = -infinity 
            for i in range(len(valids)):
                if valids[i]:
                    search = self.alphaBetaSearch(self.game.getNextState(board, currentP, i, turn), turn+1, depth-1, a,b,False)
                    #print(search, v)
                    if search >= v:
                        v = max(v,search)
                        self.bestMove = i
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

    def boardValue(self,board,turn):
        friend = []
        enemy = []

        for i,row in enumerate(board):
            for j,x in enumerate(row):
                if x == 1:
                    friend.append((i,j))
                elif x == -1:
                    enemy.append((i,j))
        diff = len(friend) - len(enemy)
        friendD = self.distancesBetween(friend)
        return (100*diff-0.01*friendD)  

    def distancesBetween(self, pieces):
        distances = 0
        for x in pieces:
            distances+=self.distance(x)
        return distances
    
    def distance(self, current):
        x1,y1 = current
        x2,y2 = 3.5,3.5
        return math.sqrt((2*x1-x2)**2 + (2*y1-y2)**2)
        
