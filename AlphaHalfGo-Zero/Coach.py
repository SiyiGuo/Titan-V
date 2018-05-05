from collections import deque
from Arena import Arena
from MCTS import MCTS
import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle
from HalfGo.HalfGoLogic import WHITE, BLACK


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()

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
        trainExamples = [] #move history of this single episode
        board = self.game.getInitBoard() #load the gam setup
        self.curPlayer = WHITE #WHITE goes first
        episodeStep = 0 #record the truns of self play
        
        #star playing the game
        while True:
            # turn objective board into self.curlPlayer POV's board. Ie: black, white -> friend, enemy
            #       two kinds of board:
            #           1: Objective board: Black and White
            #           2: CanonicalBoard:  Friendly and Enemy
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)
            # print("Received CanonicalBoard:\n%s"%canonicalBoard.reshape(8,8))
            # print("Current player:%s"%self.curPlayer)
            # a = input()

            # if episodes > tempThreshold, MCTS will stop updating probs, and just return best move
            #NOTE: mainly for spped up I guess? currently disable, as episodeStep = 24, args.tempThreshold = 25
            temp = int(episodeStep < self.args.tempThreshold) 

            # create probability of winning for each action on board for self.currPlayer's POV
            
            pi = self.mcts.getActionProb(canonicalBoard, episodeStep, temp=temp) 
            

            # one board situation can generate two tranining example # as symmetric does not matter
            sym = self.game.getSymmetries(canonicalBoard, pi)

            #adding tranning example
            #BUG: not showing correctly
            for b,policyVector in sym: 
                # (canonicalBoard,player, polivy vector)
                trainExamples.append([b, self.curPlayer, policyVector, episodeStep])
            
            # #DEBUG: 
            # probs_display = [round(x,2) for x in pi]
            # print("curr_player:%s turn:%s, probs:\n%s"%(self.curPlayer, episodeStep, np.array(probs_display).reshape(8,8)))

            #choose action with highest winning probability
            action = np.random.choice(len(pi), p=pi)

            #DEBUG
            # print("in player point of view \n player %s going to take action %s in turn %s board:\n%s"%(self.curPlayer, action, episodeStep, canonicalBoard.reshape(8,8)))

            #self.curPlayer turn to next player, objective board update, turn update
            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action) #regardless of friendly or enemy, show objective
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

            if r!=0 and self.curPlayer == WHITE:
                #DEBUG
                # print("Objective board")
                # print("game has ended, player %s result %s board:\n%s"%(self.curPlayer, r, board.reshape(8,8)))

                #return board winning result, who won it 
                #(canonicalBoard,policyVector,v)
                # x[0] cannonical board, x[2] policy vector x[1] self.curlPlayer of cannonical board
                # x[1] is BLACK, return -result as -result is in BLACK's POV
                # x[1] is WHITE, return result, as result is in WHITE's POV
                # x[2] policyVector from mcts
                # x[3] turn
                #TODO do I need to add turn for poliicy vector as well?
                generatedTraining = [(x[0],x[2],r*((-1)**(x[1]!=WHITE)), x[3]) for x in trainExamples] #add turn as a input, no need to make change for pi
                # generatedTraining = [(x[0],x[2],r*((-1)**(x[1]!=WHITE))) for x in trainExamples]
                # generatedTraining = [(x[0],x[2],r*((-1)**(x[1]!=self.curPlayer))) for x in trainExamples]


                #DEBUG
                # lastResult = generatedTraining[-1]
                # print("Input to trainExample")
                # print("result:%s, cannonicalboard:\n%s "%(lastResult[2], lastResult[0].reshape(8,8)))

                # a = input()
                return generatedTraining

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
    
                eps_time = AverageMeter()
                bar = Bar('Self Play', max=self.args.numEps)
                end = time.time()
    
                for eps in range(self.args.numEps): #for each self-play of this rounds
                    self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree

                     #reutrn [(canonicalBoard,pi,v), (canonicalBoard,pi,v)]
                     # v is the result
                    selfPlayResult = self.executeEpisode()
                    #play one game, adding the gaming history
                    iterationTrainExamples +=  selfPlayResult
    
                    # bookkeeping + plot progress
                    eps_time.update(time.time() - end)
                    end = time.time()
                    bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args.numEps, et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                    bar.next()
                bar.finish()

                # save the iteration examples to the history 
                self.trainExamplesHistory.append(iterationTrainExamples)
            
            #self-play finished, updating the move history
            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0) #remove the oldest gaming history
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)  
            self.saveTrainExamples(i-1)
            
            # shuffle examlpes before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e) #adding new move record
            shuffle(trainExamples)

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
