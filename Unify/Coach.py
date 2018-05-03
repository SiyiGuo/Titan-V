from collections import deque
import numpy as np
import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle

#Util input
from pytorch_classification.utils import Bar, AverageMeter

#Half Go Input
from Arena import Arena
from MCTS import MCTS
from HalfGo.HalfGoLogic import WHITE, BLACK

#Pubg Input
from PubgArenaCoach.Arena import Arena as Arena2
from PubgArenaCoach.MCTS import MCTS as MCTS2


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, game, nnet, args, game2, nnet2, args2):
        #For half go
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()

        #For pubg
        self.game2 = game2
        self.nnet2 = nnet2
        self.pnet2 = self.nnet2.__class__(self.game2)  # the competitor network
        self.args2 = args2
        self.mcts2 = MCTS2(self.game2, self.nnet2, self.args2)
        self.trainExamplesHistory2 = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay2 = False # can be overriden in loadTrainExamples()

    def executeEpisode(self):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        #HalfGo Setup
        trainExamples = [] #move history of this single episode
        board = self.game.getInitBoard() #load the gam setup
        self.curPlayer = WHITE #WHITE goes first
        episodeStep = 0 #record the truns of self play

        #Pubg Setup
        trainExamples2 = []
        
        #Flag change
        pubg_now = False
        #star playing the game
        while True:
            # turn objective board into self.curlPlayer POV's board. Ie: black, white -> friend, enemy
            #       two kinds of board:
            #           1: Objective board: Black and White
            #           2: CanonicalBoard:  Friendly and Enemy
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)

            # if episodes > tempThreshold, MCTS will stop updating probs, and just return best move
            #NOTE: mainly for spped up I guess? currently disable, as episodeStep = 24, args.tempThreshold = 25
            temp = int(episodeStep < self.args.tempThreshold) 

            # create probability of winning for each action on board for self.currPlayer's POV
            
            print("turn:%s"%episodeStep, end="\r")
            pi = self.mcts.getActionProb(canonicalBoard, episodeStep, temp=temp) 
            

            # one board situation can generate two tranining example # as symmetric does not matter
            sym = self.game.getSymmetries(canonicalBoard, pi)

            #adding tranning example
            #BUG: not showing correctly
            for b,policyVector in sym: 
                # (canonicalBoard,player, polivy vector)
                if pubg_now:
                    trainExamples2.append([b, self.curPlayer, policyVector, episodeStep])
                else:
                    trainExamples.append([b, self.curPlayer, policyVector, episodeStep])
            
            # #DEBUG: 
            # probs_display = [round(x,2) for x in pi]
            # print("curr_player:%s turn:%s, probs:\n%s"%(self.curPlayer, episodeStep, np.array(probs_display).reshape(8,8)))

            #choose action with highest winning probability
            action = np.random.choice(len(pi), p=pi)

            #DEBUG
            # print("in player point of view \n player %s going to take action %s in turn %s board:\n%s"%(self.curPlayer, action, episodeStep, canonicalBoard.reshape(8,8)))

            #self.curPlayer turn to next player, objective board update, turn update
            if not pubg_now:
                board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action) #regardless of friendly or enemy, show objective
            else:
                board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action, episodeStep)
            episodeStep += 1

            #DEBUG
            # print("after action, objective board \n ")
            # print( board.reshape(8,8))
            # print("next player %s next turn %s"%(self.curPlayer, episodeStep))
            
            #check the new board status
            #return 0 if game continue, 1 if WHITE win, -1 if BLACK win. 
            #thgouth the last turn was BLACK's Move, we updated self.curPlayer after Black action
            #so we judge result in WHITE's POV
            # the last turn after black does not added to the trainExample, as we already know who won
            # we add winning result in next if Statement
            r = self.game.getGameEnded(board, self.curPlayer, episodeStep) #in WHITE's POV

            if r!=0 and not pubg_now: 
                print("Time to switch the game at turn:%s"%episodeStep)
                
                
                self.game, self.game2 = self.game2, self.game
                self.nnet, self.nnet2 = self.nnet2, self.nnet
                self.pnet, self.pnet2 = self.pnet2, self.pnet
                self.args, self.args2 = self.args2, self.args
                self.mcts, self.mcts2 = self.mcts2, self.mcts

                #Restarting
                episodeStep = 0
                # Add corner stuff
                board[0][0] = 3
                board[7][7] = 3
                board[0][7] = 3
                board[7][0] = 3
                print("restarted turn:%s, End board is:\n%s"%(episodeStep, np.array(board).reshape(8,8)))

                board = self.game.getInitBoard(obBoard = board)

                pubg_now = True
                # a = input()

            
                
            elif r != 0 and pubg_now:
                #The real exit point
                generatedTraining = [(x[0],x[2],r*((-1)**(x[1]!=WHITE)), x[3]) for x in trainExamples] #add turn as a input, no need to make change for pi
                generatedTraining2 = [(x[0],x[2],r*((-1)**(x[1]!=WHITE)), x[3]) for x in trainExamples2]

                #Set things back
                self.game, self.game2 = self.game2, self.game
                self.nnet, self.nnet2 = self.nnet2, self.nnet
                self.pnet, self.pnet2 = self.pnet2, self.pnet
                self.args, self.args2 = self.args2, self.args
                self.mcts, self.mcts2 = self.mcts2, self.mcts
                print("Episode ended:%s,result:%s, board:%s"%(episodeStep, r, np.array(board).reshape(8,8)))
                return generatedTraining, generatedTraining2

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximium length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters+1): #for number of rounds
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration
            if not self.skipFirstSelfPlay or i>1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)  #remove the previous training example
                """
                Pubg
                """
                iterationTrainExamples2 = deque([], maxlen=self.args2.maxlenOfQueue) 

                eps_time = AverageMeter()
                bar = Bar('Self Play', max=self.args.numEps)
                end = time.time()
    
                for eps in range(self.args.numEps): #for each self-play of this rounds
                    self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree
                    """
                    pubg
                    """
                    self.mcts2 = MCTS2(self.game2, self.nnet2, self.args2)

                     #reutrn [(canonicalBoard,pi,v), (canonicalBoard,pi,v)]
                     # v is the result
                    selfPlayResult, selfPlayResult2 = self.executeEpisode()
                    #play one game, adding the gaming history
                    iterationTrainExamples +=  selfPlayResult
                    """
                    Pubg
                    """
                    iterationTrainExamples2 +=  selfPlayResult2
                    
    
                    # bookkeeping + plot progress
                    eps_time.update(time.time() - end)
                    end = time.time()
                    bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args.numEps, et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                    bar.next()
                bar.finish()

                # save the iteration examples to the history 
                self.trainExamplesHistory.append(iterationTrainExamples)
                self.trainExamplesHistory2.append(iterationTrainExamples2)

            #self-play finished, updating the move history
            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0) #remove the oldest gaming history
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)  
            self.saveTrainExamples(i-1)

            """
            pubg
            """
            if len(self.trainExamplesHistory2) > self.args2.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory2), " => remove the oldest trainExamples")
                self.trainExamplesHistory2.pop(0) #remove the oldest gaming history
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples2(i-1)


            # shuffle examlpes before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e) #adding new move record
            shuffle(trainExamples)
            """
            PUBG
            """
            trainExamples2 = []
            for e in self.trainExamplesHistory2:
                trainExamples2.extend(e)  # adding new move record
            shuffle(trainExamples2)


            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar') #save the previous net
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar') #read the previous net
            pmcts = MCTS(self.game, self.pnet, self.args) #reset previous models' mcts
            
            #using new data to train the new model
            self.nnet.train(trainExamples) #trin the network with new move record
            nmcts = MCTS(self.game, self.nnet, self.args) #rest new models' mcts

            #OLD VS NEW
            print('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda board, turn: np.argmax(pmcts.getActionProb(board, turn, temp=0)),
                          lambda board, turn: np.argmax(nmcts.getActionProb(board, turn, temp=0)), self.game)
            pwins, nwins, draws = arena.playGames(self.args.arenaCompare) #playing new mode against old models

            print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            if pwins+nwins > 0 and float(nwins)/(pwins+nwins) < self.args.updateThreshold:
                #OLD WIN!
                print('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar') #using previous mode, as it beat new model
            else:
                #NEW WIN!
                print('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar') #save the new model, as this is the best

            """
            pubg
            """
            # training new network, keeping a copy of the old one
            self.nnet2.save_checkpoint(folder=self.args2.checkpoint, filename='temp.pth.tar')  # save the previous net
            self.pnet2.load_checkpoint(folder=self.args2.checkpoint, filename='temp.pth.tar')  # read the previous net
            pmcts2 = MCTS2(self.game2, self.pnet2, self.args2)  # reset previous models' mcts

            # using new data to train the new model
            self.nnet2.train(trainExamples2)  # trin the network with new move record
            nmcts2 = MCTS2(self.game2, self.nnet2, self.args2)  # rest new models' mcts

            # OLD VS NEW
            print('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena2(lambda board, turn: np.argmax(pmcts2.getActionProb(board, turn, temp=0)),
                          lambda board, turn: np.argmax(nmcts2.getActionProb(board, turn, temp=0)), self.game2)
            pwins, nwins, draws = arena.playGames(self.args2.arenaCompare)  # playing new mode against old models

            print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            if pwins + nwins > 0 and float(nwins) / (pwins + nwins) < self.args.updateThreshold:
                # OLD WIN!
                print('REJECTING NEW MODEL')
                self.nnet2.load_checkpoint(folder=self.args2.checkpoint,
                                          filename='temp.pth.tar')  # using previous mode, as it beat new model
            else:
                # NEW WIN!
                print('ACCEPTING NEW MODEL')
                self.nnet2.save_checkpoint(folder=self.args2.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet2.save_checkpoint(folder=self.args2.checkpoint,
                                          filename='best.pth.tar')  # save the new model, as this is the best

    def getCheckpointFile(self, iteration): #reading the tranined network
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    """
    pubg
    """
    def saveTrainExamples2(self, iteration):
        folder = self.args2.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examplesFile = modelFile+".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True

    """
    Pubg
    """
    def loadTrainExamples2(self):
        modelFile = os.path.join(self.args2.load_folder_file[0], self.args2.load_folder_file[1])
        examplesFile = modelFile+".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay2 = True
