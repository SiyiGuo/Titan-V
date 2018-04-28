import numpy as np
import PubgGame as pubg

def test_player():

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def getConicalBoard(self,board, turn):
        for i,row in enumerate(board):
            for j,x in enumerate(row):
                if board[i][j] != 3:
                   board[i][j] = self.player * board[i][j]
        return board                  

    def play(self, board, turn):
        alphaBetaSearch(board, turn, 4, 0, 0, True)
        return self.bestMove

    def alphaBetaSearch(self, board, turn, depth, a, b, maximizingPlayer):
        currentP = 1 if maximizingPlayer else -1
        result = this.game.getGameEnded(board, currentP)
        if result != 0:
            return (1 if result*currentP == self.player then -1)
        if depth == 0:
            return boardValue(board, turn, currentP)
        valids = self.game.getValidMoves(board, self.player)
        if maximizingPlayer:
            v = -infinity 
            for move in valids: 
                search = alphaBetaSearch(self.game.getNextState(board, currentP, move, turn), turn+1, depth-1, a,b,False)
                if search > v:
                    v = search
                    self.bestMove = move
                a = max(a,v)
                if b <= a:
                    break
            return v   
        else:
            v = infinity 
            for move in valids: 
                v = min(v, alphaBetaSearch(self.game.getNextState(board, currentP, move, turn), turn+1, depth-1, a,b,True))
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
        friendD = distancesBetween(friend)
        return np.tanh((0.1*diff+0.01*friendD))       

    def distancesBetween(self, pieces):
        current = pieces[0]
        distances = 0
        for x in pieces[1:]:
            distances+=distance(current,x)
        return distances
    
    def distance(self, current, target):
        x1,y1 = current
        x2,y2 = target
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
        

