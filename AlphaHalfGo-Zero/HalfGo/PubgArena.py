import numpy as np



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

    def playGame(self, initBoard, verbose=False):
        """
        Executes one episode of a game.
        player: lambda board, turn: np.argmax(pmcts.getActionProb(board, turn, temp=0)
        Returns:
            1 white win
            -1 black win
            0.001 draw
        """
        # # For recors of a single game
        # self.boards = []
        # self.turns = []
        # self.pis = []
        # self.curPlayers = []

        players = [self.player2, None, self.player1]
        curPlayer = 1
        
        board = initBoard
        turn = 0 #turn indicator

        curPlayer = 1 #WHite first
        #game start
        while self.game.getGameEnded(board, curPlayer, turn)==0 :# or turn < 256: #this should == trun < 24
            if verbose:
                assert(self.display)
                print("Turn ", str(turn), "Player ", str(curPlayer))
                self.display(board)

            #curPlayer = White = 1, curPlayer +1 = 2 -> players[2] = self.player1
            #curPlayer = Black = -1, curPlayer + 1 = 0 -> players[0] = self.player2
            canonicalBoard = self.game.getCanonicalForm(board, curPlayer)
            action = players[curPlayer+1](canonicalBoard, turn)

            # valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), curPlayer)
            valids = self.game.getValidMoves(canonicalBoard, 1) #as cannonical board convert to white

            if action != None and action != self.game.getActionSize():
                if valids[action]==0:
                    print("\n player: %s"%curPlayer)
                    print(action)
                    print(board)
                    a = input()


                # #Recording the data
                # self.boards.append(canonicalBoard)
                # pis = [0] * self.game.getActionSize()
                # pis[action] = 1
                # self.pis.append(pis)
                # self.turns.append(turn)
                # self.curPlayers.append(curPlayer)

            #update board, curPlayer, turn at the end, as developmet guide indeicated
            board, curPlayer = self.game.getNextState(board, curPlayer, action, turn)

            turn+=1

        if verbose:
            assert(self.display)
            print("Game over: Turn ", str(turn), "Result ", str(self.game.getGameEnded(board, 1, turn)))
            self.display(board)

        #As get Game wnded return a player won or not
        #here we want white or balck wwin or not
        #so we passs object board, with 1 as player
        result = self.game.getGameEnded(board, 1, turn)
        # Continus
        print("Object board:\n%s"%np.array(board).reshape(8,8))
        print("Player:%s won"%result)
        print("Tuen:%s"%turn)

        # # recording the data
        # for i in range(len(self.turns)):
        #     canonicalBoard = self.boards[i]
        #     pis = self.pis[i]
        #     turn = self.turns[i]
        #     curPlayer = self.curPlayers[i]
        #     self.records.append((canonicalBoard, pis, result*((-1)**(curPlayer!=1)), turn))

        return result