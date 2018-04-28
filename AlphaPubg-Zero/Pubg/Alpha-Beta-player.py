import numpy as np
import PubgGame as pubg

def test_player():

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def getConicalBoard(self,board, turn):
        for i,row in enumerate(board):
            for j,x in enumerate(row):
                if board[i][j] != 9:
                   board[i][j] = self.player * board[i][j]
        return board                  

    def play(self, board, turn):
        valids = self.game.getValidMoves(board, self.player)
        for move in valids:
            print(1)

    def alphaBetaSearch(self, board, turn, depth, a, b, maximizingPlayer):
        currentP = 1 if maximizingPlayer else -1
        result = this.game.getGameEnded(board, currentP)
        if result != 0:
            return 100 if result*currentP == self.player then -100
        if depth == 0:
            return boardValue(board, turn, currentP)
        valids = self.game.getValidMoves(board, self.player)
        if maximizingPlayer:
            v = -infinity 
            for move in valids: 
                v = max(v, alphaBetaSearch(self.game.getNextState(board, currentP, move, turn), turn+1, depth-1, a,b,False))
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
