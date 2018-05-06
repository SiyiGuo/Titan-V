import numpy as np
import math
import operator
import time

infinity = 999999

class AbpPlayer():

    abpDepth = 2 # actual depth = abpdepth + 1

    def __init__(self, game, player, abpDepth = 2):
        #Player will always be White(1/friend), as we pass in canonical board
        self.game = game
        self.player = player
        self.abpDepth = abpDepth        

    def play(self, board, turn):
        """
        input: A canonical board
        return: a action number in range(513)
        """
        s = time.time()
        results = {}
        v = - infinity
        a = -infinity
        b = infinity
        valids = self.game.getValidMoves(board, self.player)
        for i in range(len(valids)):
            if valids[i]:
                # print(i)
                results[i] = self.alphaBetaSearch(self.game.getNextState(board, 1, i, turn), turn+1, self.abpDepth, a,b,False)   
                v = max(v,results[i])
                a = max(a,v)     
                if b <= a:
                    break
        e = time.time()
        print(s-e)
        try:
            action = max(results, key=results.get)
        except:
            action = None
        return action

    def alphaBetaSearch(self, board, turn, depth, a, b, maximizingPlayer = False):
        board, currentP = board
        board = self.game.getCanonicalForm(board, currentP)
        # result = self.game.getGameEnded(board, currentP, turn)
        result = self.game.getGameEnded(board, 1, turn)
        if result != 0:
            # print("Board:\n%s"%np.array(board.reshape(8,8)))
            # print("result:%s"%result)
            # print("Another result:%s"%self.game.getCanonicalForm(board, currentP))
            return (1 if result*currentP == self.player else (-1)) * 10000
        if depth == 0:
            return self.boardValue(board, turn)
        valids = self.game.getValidMoves(board, 1) #8*8*8+1 vector
        if maximizingPlayer:
            v = -infinity 
            for i in range(len(valids)):
                if valids[i]:
                    search = self.alphaBetaSearch(self.game.getNextState(board, currentP, i, turn), turn+1, depth-1, a, b ,False)
                    #print(search, v)
                    v = max(v,search)
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

        #i is column
        #j is row
        #X is the piece
        for col,row in enumerate(board):
            for row_index,piece in enumerate(row):
                if piece == 1:
                    friend.append((col,row_index))
                elif piece == -1:
                    enemy.append((col,row_index))

        diff = len(friend) - len(enemy)
        friendD = self.distancesBetween(friend)
        return (100*diff-0.01*friendD)  

    def distancesBetween(self, pieces):
        distances = 0
        for position in pieces:
            distances+=self.distance(position)
        return distances
    
    def distance(self, current):
        x1,y1 = current
        x2,y2 = 3.5,3.5
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
        
