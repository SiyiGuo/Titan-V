from collections import deque
from Arena import Arena
from MCTS import MCTS
import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle


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
        self.curPlayer = 1
        episodeStep = 0 #record the truns that has passed of current game
        
        #star playing the game
        while True:
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer) #current situation of the board in the player's point of view
            temp = int(episodeStep < self.args.tempThreshold) # if episodes more than the tempThreshold, MCTS will search will stop searching?
            # print("self.curPlayer:%s, turn:%s, board;\n %s"%(self.curPlayer, episodeStep, canonicalBoard.reshape(8,8)))

            pi = self.mcts.getActionProb(canonicalBoard, episodeStep, temp=temp) #NOTE: ???the probability of winnning for different move on current situation?
            sym = self.game.getSymmetries(canonicalBoard, pi)
            for b,policyVector in sym: #bug come from here using the same board variable
                trainExamples.append([b, self.curPlayer, policyVector, None])
            
            probs_display = [round(x,2) for x in pi]
            print("curr_player:%s turn:%s, probs:\n%s"%(self.curPlayer, episodeStep, np.array(probs_display).reshape(8,8)))

            action = np.random.choice(len(pi), p=pi)

            # print("player %s take action %s in turn %s"%(self.curPlayer, action, episodeStep))

            #self.curPlayer turn to next player, board update, turn update
            print("in player point of view player %s going to take action %s in turn %s board:\n%s"%(self.curPlayer, action, episodeStep, canonicalBoard.reshape(8,8)))
            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action) #regardless of friendly or enemy, show objective
            episodeStep += 1
            print("after action, show objective board \n ")
            print( board.reshape(8,8))
            print("next player %s turn %s"%(self.curPlayer, episodeStep))
            a = input()
            
            
            # print(board)
            
            #check the new board status
            r = self.game.getGameEnded(board, self.curPlayer, episodeStep) #return 0 if game continue, 1 if player1 win, -1 if player 2 win
            # print("turn %s, game status: %s, take action: %s"%(episodeStep, r, action))

            if r!=0: 
                print("Objective board")
                print("game has ended, player %s result %s board:\n%s"%(self.curPlayer, r, board.reshape(8,8)))
                lastTurn = trainExamples[-1]
                print("last turn suggest player:%s, board:\n%s"%(lastTurn[1], lastTurn[0].reshape(8,8)))
                #return board winning result, who won it 
                generatedTraining = [(x[0],x[2],r*((-1)**(x[1]!=self.curPlayer))) for x in trainExamples]
                lastResult = generatedTraining[-1]
                print("input to train example player:%s, result:%s, board:\n%s "%(lastResult[2], r, lastResult[0].reshape(8,8)))
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

                    print("\n-----------game "+str(eps)+" start-----------")
                    selfPlayResult = self.executeEpisode() #reutrn [(canonicalBoard,pi,v), (canonicalBoard,pi,v)]
                    # a = input("do You want to continue?")
                    iterationTrainExamples +=  selfPlayResult#play one game, adding the gaming history
                    print("\n-----------game "+str(eps)+" end-----------")
    
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
