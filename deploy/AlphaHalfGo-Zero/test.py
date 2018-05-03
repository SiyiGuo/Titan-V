import tensorflow as tf
import tfdeploy as td

# setup tfdeploy (only when creating models)
td.setup(tf)

# build your graph
sess = tf.Session()

# use names for input and output layers
x = tf.placeholder("float", shape=[None, 784], name="input")
W = tf.Variable(tf.truncated_normal([784, 100], stddev=0.05))
b = tf.Variable(tf.zeros([100]))
y = tf.nn.softmax(tf.matmul(x, W) + b, name="output")

sess.run(tf.global_variables_initializer())
all_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
# print (all_vars)
for i in all_vars:
    print ("Name:%s"%i)
    # print("Params:\n%s"%i.eval(session=sess))
# ... training ...

# create a tfdeploy model and save it to disk
model = td.Model()
model.add(y, sess) # y and all its ops and related tensors are added recursively
model.save("model.pkl")