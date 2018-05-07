import tensorflow as tf
import os
import numpy as np

# read Graph + Checkpoint
with tf.Session() as sess:
    graph_path = "./temp/best.pth.tar.meta"
    model_path = os.path.dirname(graph_path)

    #Model has been restored
    loader = tf.train.import_meta_graph(graph_path)
    loader.restore(sess, tf.train.latest_checkpoint(model_path))
    #Model finish loading, do waht ever you want not#

    # ##########method1#####################
    # print("method1")
    # train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
    # for v in train_vars:
    #     name = v.name
    #     tshape = v.get_shape()
    #     # numpy from here
    #     value = v.eval()
    #     shape = value.shape
    #     print("name:%s, tshape:%s, shape:%s"%(name, tshape, shape))

    ############method2##################
    print("method2")
    Model_variables = tf.GraphKeys.MODEL_VARIABLES
    Global_Variables = tf.GraphKeys.GLOBAL_VARIABLES
    ##
    all_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
    for i in all_vars:
        print ("Name:%s"%i)
        name = str(i).split("'")[1].replace("/","")
        np.save(str(name)+".npy" ,i.eval())

    