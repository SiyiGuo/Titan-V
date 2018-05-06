import os
import shutil
import time
import random
import numpy as np
import math
import sys
sys.path.append('../../')
from utils import *
from pytorch_classification.utils import Bar, AverageMeter
from NeuralNet import NeuralNet

import tensorflow as tf
from .PubgNNet import PubgNNet as pnnet

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10, #rounds of training
    'batch_size': 128, # take 2 games as input
    'num_channels': 512,
})

class NNetWrapper(NeuralNet):
    def __init__(self, game):
        self.nnet = pnnet(game, args) #Core Algorithm Part
        self.board_x, self.board_y = game.getBoardSize() #Board Dimension
        self.action_size = game.getActionSize() #number of possible actions

        self.sess = tf.Session(graph=self.nnet.graph) #SPECIFY WHICH GPU to USE
        self.saver = None
        with tf.Session() as temp_sess:
            temp_sess.run(tf.global_variables_initializer())
        self.sess.run(tf.variables_initializer(self.nnet.graph.get_collection('variables')))

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v, turn) || past data
        """

        for epoch in range(args.epochs):
            print('EPOCH ::: ' + str(epoch+1))
            data_time = AverageMeter()
            batch_time = AverageMeter()
            pi_losses = AverageMeter()
            v_losses = AverageMeter()
            end = time.time()

            bar = Bar('Training Net', max=int(len(examples)/args.batch_size))
            batch_idx = 0

            # self.sess.run(tf.local_variables_initializer())
            while batch_idx < int(len(examples)/args.batch_size):
                sample_ids = np.random.randint(len(examples), size=args.batch_size)
                boards, pis, vs , turns= list(zip(*[examples[i] for i in sample_ids])) #boards,possible winning on each position, winning result


                turns = [[turn] for turn in turns]

                # predict and compute gradient and do SGD step
                input_dict = {self.nnet.input_boards: boards, #input X
                                      self.nnet.turn: turns,
                                self.nnet.target_pis: pis,  #for calculating loss
                                 self.nnet.target_vs: vs, #for calculating loss
                                   self.nnet.dropout: args.dropout, 
                                self.nnet.isTraining: True}

                # measure data loading time
                data_time.update(time.time() - end)

                # record loss and do the training
                #training
                self.sess.run(self.nnet.train_step, feed_dict=input_dict)
                #record loss value
                pi_loss, v_loss = self.sess.run([self.nnet.loss_pi, self.nnet.loss_v], feed_dict=input_dict)
                pi_losses.update(pi_loss, len(boards))
                v_losses.update(v_loss, len(boards))

                # measure elapsed time
                batch_time.update(time.time() - end)
                end = time.time()
                batch_idx += 1

                # plot progress
                bar.suffix  = '({batch}/{size}) Data: {data:.3f}s | Batch: {bt:.3f}s | Total: {total:} | ETA: {eta:} | Loss_pi: {lpi:.4f} | Loss_v: {lv:.3f}'.format(
                            batch=batch_idx,
                            size=int(len(examples)/args.batch_size),
                            data=data_time.avg,
                            bt=batch_time.avg,
                            total=bar.elapsed_td,
                            eta=bar.eta_td,
                            lpi=pi_losses.avg,
                            lv=v_losses.avg,
                            )
                bar.next()
            bar.finish()

    def predict(self, board, turn):
        """
        board: np array with board
        Making the prediction of winning for different move on the board
        """
        # timing
        start = time.time()

        # preparing input
        board = board[np.newaxis, :, :]
        turn = [[turn]]

        # run
        prob, v = self.sess.run([self.nnet.prob, self.nnet.v], feed_dict={self.nnet.input_boards: board, 
                                                                            self.nnet.turn: turn,
                                                                            self.nnet.dropout: 0, 
                                                                            self.nnet.isTraining: False})

        # print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        return prob[0], v[0] #to flatten the tensor into a list

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        """
        Save the model with filename in folder
        """
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        if self.saver == None:            
            self.saver = tf.train.Saver(self.nnet.graph.get_collection('variables'))
        with self.nnet.graph.as_default():
            self.saver.save(self.sess, filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        """
        Load the model with filename in folder
        """
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath+'.meta'):
            raise("No model in path {}".format(filepath))
        with self.nnet.graph.as_default():
            self.saver = tf.train.Saver()
            self.saver.restore(self.sess, filepath)