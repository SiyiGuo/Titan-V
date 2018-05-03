import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time

class Arena():
    """
    An Arena class where any 2 agents can be pit against each other.
    """
    def __init__(self, player1, player2, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.
        player: lambda board, turn: np.argmax(pmcts.getActionProb(board, turn, temp=0)
        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """

        players = [self.player2, None, self.player1]
        curPlayer = 1
        test = self.generateRandomBoard()
        
        board = self.game.getInitBoard(obBoard = test)
        turn = 0 #turn indicator

        #game start
        while self.game.getGameEnded(board, curPlayer, turn)==0 :# or turn < 256: #this should == trun < 24
            if verbose:
                assert(self.display)
                print("Turn ", str(turn), "Player ", str(curPlayer))
                self.display(board)

            #curPlayer = White = 1, curPlayer +1 = 2 -> players[2] = self.player1
            #curPlayer = Black = -1, curPlayer + 1 = 0 -> players[0] = self.player2
            action = players[curPlayer+1](self.game.getCanonicalForm(board, curPlayer), turn)

            # valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), curPlayer)
            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), 1) #as cannonical board convert to white


            if valids[action]==0:
                print("\n player: %s"%curPlayer)
                print(action)
                print(board)
                a = input()

            #update board, curPlayer, turn at the end, as developmet guide indeicated
            board, curPlayer = self.game.getNextState(board, curPlayer, action, turn)
            turn+=1

        if verbose:
            assert(self.display)
            print("Game over: Turn ", str(turn), "Result ", str(self.game.getGameEnded(board, 1, turn)))
            self.display(board)

        #return single game result
        result = self.game.getGameEnded(board, curPlayer, turn)
        print("Result:%s for player:%s"%(result, curPlayer))
        return result

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        eps_time = AverageMeter()
        bar = Bar('Arena.playGames', max=num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(num/2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult==1:
                oneWon+=1
            elif gameResult==-1:
                twoWon+=1
            else:
                draws+=1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=maxeps, et=eps_time.avg,
                                                                                                       total=bar.elapsed_td, eta=bar.eta_td)
            bar.next()

        self.player1, self.player2 = self.player2, self.player1
        
        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult==-1:
                oneWon+=1                
            elif gameResult==1:
                twoWon+=1
            else:
                draws+=1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=num, et=eps_time.avg,
                                                                                                       total=bar.elapsed_td, eta=bar.eta_td)
            bar.next()
            
        bar.finish()

        return oneWon, twoWon, draws

    def generateRandomBoard(self):
        test = [
            [3,0,0,0,0,0,0,3],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [3,0,0,0,0,0,0,3],
        ]

        curPlayer = 1 #WHite first
        white,black = np.random.randint(low = 6, high = 13, size = 2)
        i = 0
        while i <= white:
            pos = np.random.randint(low = 2, high = 64)
            x = pos // 8
            y = pos % 8
            if test[x][y] == 0:
                test[x][y] = 1
                i += 1
        i = 0
        while i <= black:
            pos = np.random.randint(low = 2, high = 64)
            x = pos // 8
            y = pos % 8
            if test[x][y] == 0:
                test[x][y] = -1
                i += 1
        return test