import math
import numpy as np
from HalfGo.HalfGoLogic import BLACK, WHITE
import time
class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}       # stores Q values for s,a (as defined in the paper) || the reward for current move a
        self.Nsa = {}       # stores #times edge s,a was visited || the # of time we have taking action a in current situation
        self.Ns = {}        # stores #times board s was visited || the # of this situation we have been in 
        self.Ps = {}        # stores initial policy (returned by neural net)

        self.Es = {}        # stores game.getGameEnded ended for board s || Store the gaming result of current board situation
        self.Vs = {}        # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, turn, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.
        Input:
            cannoicalBoard: board
            turn: int in range(0,24)
            temp: 0 or 1

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        
        # perform exploring first
        
        for i in range(self.args.numMCTSSims):
            self.search(canonicalBoard, turn)
            
        
        
        # find the prob of action we take
        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.Nsa[(s,a)] if (s,a) in self.Nsa else 0 for a in range(self.game.getActionSize())]

        # debug check
        if (float(sum(counts)) ==0):
            print("\nerror in MCTS.getActionProb, before deciding action")
            print("turnindex:%s"%turn)
            print(canonicalBoard.reshape(8,8))
            print("non existing pattern: \n %s"%np.fromstring(s, dtype=int).reshape(8,8)) #could add reshape here
            exit()
        
        if temp==0:
            bestA = np.argmax(counts)  #find the best move in the simulation
            probs = [0]*len(counts) #set prob of winning for other move to be zero
            probs[bestA]=1 #set the best move to be 1 to let it run
            return probs #return the action to make sure we only go this move

        #could remove temp? as it is always 1
        counts = [x**(1./temp) for x in counts]

        #may need to mask probs
        # curr_player =  WHITE if turn % 2 == 0 else BLACK
        # valids = self.game.getValidMoves(canonicalBoard, curr_player)
        probs = [x/float(sum(counts)) for x in counts] # *valids

        return probs


    def search(self, canonicalBoard, turn):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propogated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propogated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """
        # cannonicalboard: on this board, 1=WHITE=Friendly, -1=BLACK=Enemy
        # each level of search, we substitute ourself into the enemy


        # convert to string for hashing
        s = self.game.stringRepresentation(canonicalBoard)

        # if 0,2,...22 than White else 1,3,5.....23 = Black
        curr_player =  WHITE if turn % 2 == 0 else BLACK #read player

        # turn does not end until 24
        self.Es[s] = self.game.getGameEnded(canonicalBoard, 1, turn)
        
        # if game has result
        if self.Es[s]!=0:
            # terminal node
            # print("turn: %s, self.Es[s]:%s board:\n %s"%(turn, self.Es[s], canonicalBoard.reshape(8,8)))
            return -self.Es[s] #NOTE: return the state of the other player

        # if we dont have policy vector for current board
        if s not in self.Ps:
            # leaf node
            # generate policy vector $ value of current board
            # nnet return:
            #   self.Ps[s]:
            #       the policy vector that indicates move
            #       with higher change leads to win
            #   V:
            #       the winning rate of current board, betweem -1 to 1 
            self.Ps[s], v = self.nnet.predict(canonicalBoard, turn)

            # find all valid move for current player
            valids = self.game.getValidMoves(canonicalBoard, curr_player)

            # remove all the invalid move
            before_mask = np.array(self.Ps[s][:-1])
            self.Ps[s] = self.Ps[s]*valids

            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                # renormalize
                self.Ps[s] /= sum_Ps_s    
            else:
                # if all valid moves were masked make all valid moves equally probable
                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.   
                print("All valid moves were masked, do workaround.")
                print(np.array(canonicalBoard).reshape(8,8))
                print(np.array(self.Ps[s][:-1]).reshape(8,8, 8))
                print(before_mask.reshape(8,8))
                print(v)
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            # record valid move, so that we do not need to re calculate
            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        # case we have policy for current string
        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s,a) in self.Qsa:
                    u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
                else:
                    u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])     # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a
        a = best_act

        # 1 = friendly, as this is self-play on each turn
        # so: next_player is always -1
        # -1 means enemy, not BLACK
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a, turn) 

        # substitute ourself to another player, 
        
        #TODO change banned
        next_s = self.game.getCanonicalForm(next_s, next_player) 
        
        # search for it
        v = self.search(next_s, turn + 1)
    
        if (s,a) in self.Qsa:
            self.Qsa[(s,a)] = (self.Nsa[(s,a)]*self.Qsa[(s,a)] + v)/(self.Nsa[(s,a)]+1)
            self.Nsa[(s,a)] += 1
        else:
            self.Qsa[(s,a)] = v
            self.Nsa[(s,a)] = 1

        self.Ns[s] += 1
        return -v
