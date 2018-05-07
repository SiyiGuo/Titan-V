import tensorflow as tf
import os
import numpy as np

# read Graph + Checkpoint
with tf.Session() as sess:
    print ("Path is")
    graph_path = "./temp/temp.pth.tar.meta"
    model_path = os.path.dirname(graph_path)

    loader = tf.train.import_meta_graph(graph_path)
    loader.restore(sess, tf.train.latest_checkpoint(model_path))

    Model_variables = tf.GraphKeys.MODEL_VARIABLES
    Global_Variables = tf.GraphKeys.GLOBAL_VARIABLES
    all_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
    
    directory = "./param/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for i in all_vars:
        print ("Name:%s"%i)
        name = str(i).split("'")[1].replace("/","")[:-2]
        path = directory+str(name)+".npy"
        np.save(path ,i.eval())

    