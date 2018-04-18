import sys
sys.path.append('..')
from utils import *
import time

import tensorflow as tf

class PubgNNet():
    def __init__(self, game, args):
        #main calculation mode
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize() #should add 1 as our implementation return 64 now, where as it should return 65 in other implementation
        self.args = args

        # Renaming functions to make the call easier
        Relu = tf.nn.relu
        Tanh = tf.nn.tanh
        BatchNormalization = tf.layers.batch_normalization
        Dropout = tf.layers.dropout #function used to prevent overfitting
        Dense = tf.layers.dense #function to create a fully connected layer #NOTE: In a dense layer, every node in the layer is connected to every node in the preceding layer.

        # Neural Net
        self.graph = tf.Graph()
        with self.graph.as_default(): 
            #input board
            self.input_boards = tf.placeholder(tf.float32, shape=[None, self.board_x, self.board_y])    # s: batch_size x board_x x board_y
            # self.turn = tf.placeholder(tf.float32, shape=[None, 1]) #batch size x 1
            self.dropout = tf.placeholder(tf.float32) #prevent overfitting
            self.isTraining = tf.placeholder(tf.bool, name="is_training") #indicate whether we are training or not

            #convolution Layer setup
            x_image = tf.reshape(self.input_boards, [-1, self.board_x, self.board_y, 1])                    # batch_size  x board_x x board_y x 1
            h_conv1 = Relu(BatchNormalization(self.conv2d(x_image, args.num_channels, 'same'), axis=3, training=self.isTraining))     # batch_size  x board_x x board_y x num_channels
            h_conv2 = Relu(BatchNormalization(self.conv2d(h_conv1, args.num_channels, 'same'), axis=3, training=self.isTraining))     # batch_size  x board_x x board_y x num_channels
            h_conv3 = Relu(BatchNormalization(self.conv2d(h_conv2, args.num_channels, 'valid'), axis=3, training=self.isTraining))    # batch_size  x (board_x-2) x (board_y-2) x num_channels
            h_conv4 = Relu(BatchNormalization(self.conv2d(h_conv3, args.num_channels, 'valid'), axis=3, training=self.isTraining))    # batch_size  x (board_x-4) x (board_y-4) x num_channels
            h_conv5 = Relu(BatchNormalization(self.conv2d(h_conv4, args.num_channels, 'valid'), axis=3, training=self.isTraining))    # batch_size  x (board_x-6) x (board_y-6) x num_channels
            h_conv5_flat = tf.reshape(h_conv5, [-1, args.num_channels*(self.board_x-6)*(self.board_y-6)]) 

            # h_conv5_flat_turn = tf.concat(axis=1, values=[self.turn, h_conv5_flat])

            

            #two dense layer as suggested in URL: https://www.tensorflow.org/tutorials/layers Building the CNN MNIST Classifier
            s_fc1 = Dropout(Relu(BatchNormalization(Dense(h_conv5_flat, 1024), axis=1, training=self.isTraining)), rate=self.dropout) # batch_size x 1024
            s_fc2 = Dropout(Relu(BatchNormalization(Dense(s_fc1, 512), axis=1, training=self.isTraining)), rate=self.dropout)         # batch_size x 512

            # s_fc2_tmp = tf.concat(axis=1, values=[self.turn, s_fc2])
            # print(s_fc2_tmp)
            print(s_fc2)
            self.pi = Dense(s_fc2, self.action_size)                                                        # batch_size x self.action_size
            print(self.pi)
            self.prob = tf.nn.softmax(self.pi) #fotmax function, final layer of the network
            print(self.prob)
            self.v = Tanh(Dense(s_fc2, 1))                                                               # batch_size x 1
            print(self.v)

            self.calculate_loss()

    def conv2d(self, x, out_channels, padding):
      return tf.layers.conv2d(x, out_channels, kernel_size=[3,3], padding=padding)
    

    def calculate_loss(self):
        self.target_pis = tf.placeholder(tf.float32, shape=[None, self.action_size])
        self.target_vs = tf.placeholder(tf.float32, shape=[None])
        self.loss_pi =  tf.losses.softmax_cross_entropy(self.target_pis, self.prob)
        self.loss_v = tf.losses.mean_squared_error(self.target_vs, tf.reshape(self.v, shape=[-1,]))
        self.total_loss = self.loss_pi + self.loss_v
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            self.train_step = tf.train.AdamOptimizer(self.args.lr).minimize(self.total_loss)