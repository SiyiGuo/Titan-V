import numpy as np
import time

def zero_pad(X, pad):
    
    ### START CODE HERE ### (≈ 1 line)
    X_pad = np.pad(X,((pad,pad),(pad,pad), (0,0)), 'constant', constant_values = 0)
    ### END CODE HERE ###
    
    return X_pad

def conv_single_step(a_slice_prev, W, b):
    ### START CODE HERE ### (≈ 2 lines of code)
    # Element-wise product between a_slice and W. Do not add the bias yet.
    s = a_slice_prev * W
    # Sum over all entries of the volume s.
    Z = np.sum(s)
    # Add bias b to Z. Cast b to a float() so that Z results in a scalar value.
    Z = Z + float(b)
    ### END CODE HERE ###

    return Z

def conv_forward(A_prev, W, b, hparameters):
    """
    Implements the forward propagation for a convolution function
    
    Arguments:
    A_prev -- output activations of the previous layer, numpy array of shape (m, n_H_prev, n_W_prev, n_C_prev)
    W -- Weights, numpy array of shape (f, f, n_C_prev, n_C)
    b -- Biases, numpy array of shape (1, 1, 1, n_C)
    hparameters -- python dictionary containing "stride" and "pad"
        
    Returns:
    Z -- conv output, numpy array of shape (m, n_H, n_W, n_C)
    cache -- cache of values needed for the conv_backward() function
    """
    
    ### START CODE HERE ###
    # Retrieve dimensions from A_prev's shape (≈1 line)  
    (n_H_prev, n_W_prev, n_C_prev) = A_prev.shape
    
    # Retrieve dimensions from W's shape (≈1 line)
    (f, f, n_C_prev, n_C) = W.shape
    
    # Retrieve information from "hparameters" (≈2 lines)
    stride = hparameters['stride']
    pad = hparameters['pad']
    
    # Compute the dimensions of the CONV output volume using the formula given above. Hint: use int() to floor. (≈2 lines)
    n_H = int((n_H_prev - f + 2*pad)/stride)+1
    n_W = int((n_W_prev - f + 2*pad)/stride)+1
    
    # Initialize the output volume Z with zeros. (≈1 line)
    Z = np.zeros((n_H,n_W,n_C))
    
    # Create A_prev_pad by padding A_prev
    A_prev_pad = zero_pad(A_prev, pad)
    
    for h in range(n_H):                           # loop over vertical axis of the output volume
        for w in range(n_W):                       # loop over horizontal axis of the output volume
            for c in range(n_C):                   # loop over channels (= #filters) of the output volume            
                # Find the corners of the current "slice" (≈4 lines)
                vert_start = h * stride
                vert_end = vert_start + f
                horiz_start = w * stride
                horiz_end = horiz_start + f
                    
                # Use the corners to define the (3D) slice of a_prev_pad (See Hint above the cell). (≈1 line)
                a_slice_prev = A_prev_pad[vert_start:vert_end,horiz_start:horiz_end,:]
                   
                # Convolve the (3D) slice with the correct filter W and bias b, to get back one output neuron. (≈1 line)
                Z[h, w, c] = conv_single_step(a_slice_prev, W[:,:,:,c], b[c])
                                        
    ### END CODE HERE ###
    
    # Making sure your output shape is correct
    assert(Z.shape == (n_H,n_W,n_C))
    # Save information in "cache" for the backprop
    cache = (A_prev, W, b, hparameters)
    
    return Z

def batchnorm_forward(X, gamma, beta):
    print(X.shape)
    if len(X.shape)>2:
        mu = np.mean(X, axis=(0,1,2))
        var = np.var(X, axis=(0,1,2))
    else:
        mu = np.mean(X, axis=1)
        var = np.var(X, axis=1)
    X_norm = (X - mu) / np.sqrt(var + 0.001)
    out = gamma * X_norm + beta

    return out

def ReLU(x):
    return np.maximum(x, 0)

def softmax(x):
    e = np.exp(x / 1.0)
    dist = e / np.sum(e)
    return dist

def conv_forward1(X, W, b, stride = 1, padding = 1):
    h_filter, w_filter, d_filter, n_filters  = W.shape
    h_x, w_x, c_x  = X.shape
    
    h_out = (h_x - h_filter + 2*padding) / stride + 1
    w_out = (w_x - w_filter + 2*padding) / stride + 1
    h_out, w_out = int(h_out), int(w_out)

    X_col = im2col_indices(X, h_filter, w_filter, padding = padding, stride = stride) # 8*8*1 -> 9*64
    W_col = W.transpose(3,2,0,1) # 3*3*1*512 -> 512 * 9
    
    W_col = W_col.reshape(n_filters, -1)

    b_col = b.reshape(b.shape[0],-1)  # 512, -> 512*1

    out = W_col @ X_col #512*9 dot 9*64 -> 512*64

    out += b_col

    out = out.reshape(n_filters, h_out, w_out).transpose(1,2,0)
    
    return out

def im2col_indices(x, field_height, field_width, padding = 1, stride = 1):
    p = padding
    x_padded = np.pad(x, ((p,p),(p,p),(0,0)), mode = 'constant')

    k,i,j = get_im2col_indices(x.shape, field_height, field_width, padding, stride)
   
    cols = x_padded[i,j,k]
    
    C = x.shape[2]
    # print(cols)
    cols = cols.reshape(field_height * field_width * C, -1)
    return cols

def get_im2col_indices(x_shape, field_height, field_width, padding = 1, stride = 1):
    H,W,C = x_shape
    
    assert(H+2*padding - field_height) % stride == 0
    assert(W+2*padding - field_width) % stride == 0
    out_height = int((H + 2*padding - field_height) / stride + 1)
    out_width = int((H + 2*padding - field_width) / stride + 1)

    i0 = np.repeat(np.arange(field_height),field_width)
    i0 = np.tile(i0,C)
    i1 = stride * np.repeat(np.arange(out_height), out_width)
    j0 = np.tile(np.arange(field_width), field_height * C)
    j1 = stride * np.tile(np.arange(out_width), out_height)
    i = i0.reshape(-1,1) + i1.reshape(1,-1)
    j = j0.reshape(-1,1) + j1.reshape(1,-1)

    k = np.repeat(np.arange(C),field_height*field_width).reshape(-1,1)

    return (k.astype(int),i.astype(int),j.astype(int))
    
def dense(data, wPath, biasPath, gPath, bPath, param):
    weight = param[wPath]
    bias = param[biasPath]
    g = param[gPath]
    b = param[bPath]
    data = np.dot(data, weight) + bias
    data = batchnorm_forward(data,g,b)
    data = ReLU(data)
    return data

def pure_dense(data, wPath, biasPath, param):
    weight = param[wPath]
    bias = param[biasPath]

    data = np.dot(data, weight) + bias
    return data

def conv2d(data, pad, stride, wPath, biasPath, gPath, bPath, param):
    weight = param[wPath]
    bias = param[biasPath]
    g = param[gPath]
    b = param[bPath]

    # data = conv_forward(data, weight, bias, {"pad": pad, "stride": stride})
    data = conv_forward1(data, weight, bias, stride, pad)

    data = batchnorm_forward(data, g, b)
    data = ReLU(data)
    return data

def conv2d1(data, pad, stride, wPath, biasPath, gPath, bPath, param):
    weight = param[wPath]
    bias = param[biasPath]
    g = param[gPath]
    b = param[bPath]

    data = conv_forward(data, weight, bias, {"pad": pad, "stride": stride})
    # data = conv_forward1(data, weight, bias, pad, stride)
    data = batchnorm_forward(data, g, b)
    data = ReLU(data)
    return data    

param = {}
files = ["conv2dkernel:0.npy", "conv2dbias:0.npy", "batch_normalizationgamma:0.npy", "batch_normalizationbeta:0.npy", 
"conv2d_1kernel:0.npy", "conv2d_1bias:0.npy", "batch_normalization_1gamma:0.npy", "batch_normalization_1beta:0.npy",
"conv2d_2kernel:0.npy", "conv2d_2bias:0.npy", "batch_normalization_2gamma:0.npy", "batch_normalization_2beta:0.npy",
 "conv2d_3kernel:0.npy", "conv2d_3bias:0.npy", "batch_normalization_3gamma:0.npy", "batch_normalization_3beta:0.npy",
  "conv2d_4kernel:0.npy", "conv2d_4bias:0.npy", "batch_normalization_4gamma:0.npy", "batch_normalization_4beta:0.npy",
  "densekernel:0.npy", "densebias:0.npy", "batch_normalization_5gamma:0.npy", "batch_normalization_5beta:0.npy",
  "dense_1kernel:0.npy", "dense_1bias:0.npy", "batch_normalization_6gamma:0.npy", "batch_normalization_6beta:0.npy",
  "dense_2kernel:0.npy", "dense_2bias:0.npy",
   "dense_3kernel:0.npy", "dense_3bias:0.npy",]
for file in files:
    p = np.load(file)
    param[file] = p

s = time.time()
data = [0]+[1] * 63
x_image = np.array(data).reshape(8,8,1)
conv_1 = conv2d(x_image, 1, 1, "conv2dkernel:0.npy", "conv2dbias:0.npy", "batch_normalizationgamma:0.npy", "batch_normalizationbeta:0.npy", param)
conv_2 = conv2d(conv_1, 1, 1, "conv2d_1kernel:0.npy", "conv2d_1bias:0.npy", "batch_normalization_1gamma:0.npy", "batch_normalization_1beta:0.npy", param)

conv_3 = conv2d(conv_2, 0, 1, "conv2d_2kernel:0.npy", "conv2d_2bias:0.npy", "batch_normalization_2gamma:0.npy", "batch_normalization_2beta:0.npy", param)
conv_4 = conv2d(conv_3, 0, 1, "conv2d_3kernel:0.npy", "conv2d_3bias:0.npy", "batch_normalization_3gamma:0.npy", "batch_normalization_3beta:0.npy", param)
conv_5 = conv2d(conv_4, 0, 1, "conv2d_4kernel:0.npy", "conv2d_4bias:0.npy", "batch_normalization_4gamma:0.npy", "batch_normalization_4beta:0.npy", param)

conv_5_reshape = conv_5.reshape(-1,2048)

dense_1 = dense(conv_5_reshape,"densekernel:0.npy", "densebias:0.npy", "batch_normalization_5gamma:0.npy", "batch_normalization_5beta:0.npy", param)
dense_2 = dense(dense_1,"dense_1kernel:0.npy", "dense_1bias:0.npy", "batch_normalization_6gamma:0.npy", "batch_normalization_6beta:0.npy", param)

pi = pure_dense(dense_2, "dense_2kernel:0.npy", "dense_2bias:0.npy", param)
prob = softmax(pi)

v = pure_dense(dense_2, "dense_3kernel:0.npy", "dense_3bias:0.npy", param)
v = np.tanh(v)

e =time.time()
print(s-e)

# s = time.time()
# data1 = [0]+[1] * 63
# x_image = np.array(data1).reshape(8,8,1)
# data1 = conv2d1(x_image, 1, 1, "conv2dkernel:0.npy", "conv2dbias:0.npy", "batch_normalizationgamma:0.npy", "batch_normalizationbeta:0.npy", param)
# data1 = conv2d1(data1, 1, 1, "conv2d_1kernel:0.npy", "conv2d_1bias:0.npy", "batch_normalization_1gamma:0.npy", "batch_normalization_1beta:0.npy", param)
# data1 = conv2d1(data1, 1, 1, "conv2d_2kernel:0.npy", "conv2d_2bias:0.npy", "batch_normalization_2gamma:0.npy", "batch_normalization_2beta:0.npy", param)
# data1 = conv2d1(data1, 1, 1, "conv2d_3kernel:0.npy", "conv2d_3bias:0.npy", "batch_normalization_3gamma:0.npy", "batch_normalization_3beta:0.npy", param)
# data1 = conv2d1(data1, 1, 1, "conv2d_4kernel:0.npy", "conv2d_4bias:0.npy", "batch_normalization_4gamma:0.npy", "batch_normalization_4beta:0.npy", param)
# e =time.time()
# print(s-e)

print(prob)
print(v)
# print("----------------")
# print(data1[-1][-1][-1])
# print("------------")
# print(data[-1][-1][-1] == data1[-1][-1][-1])
