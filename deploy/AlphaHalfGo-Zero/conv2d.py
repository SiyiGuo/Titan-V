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
                a_slice_prev = A_prev_pad[vert_start:vert_end,horiz_start:horiz_end]
                   
                # Convolve the (3D) slice with the correct filter W and bias b, to get back one output neuron. (≈1 line)
                Z[h, w, c] = conv_single_step(a_slice_prev, W[:,:,:,c], b[c])
                                        
    ### END CODE HERE ###
    
    # Making sure your output shape is correct
    assert(Z.shape == (n_H,n_W,n_C))
    
    # Save information in "cache" for the backprop
    cache = (A_prev, W, b, hparameters)
    
    return Z

def batchnorm_forward(X, gamma, beta):
    mu = np.mean(X, axis=0)
    var = np.var(X, axis=0)

    X_norm = (X - mu) / np.sqrt(var + 1e-8)
    out = gamma * X_norm + beta

    cache = (X, X_norm, mu, var, gamma, beta)

    return out

def ReLU(x):
    return np.maximum(x, 0)

def conv2d(data, pad, stride, wPath, biasPath, gPath, bPath, param):
    weight = param[wPath]
    bias = param[biasPath]
    g = param[gPath]
    b = param[bPath]

    data = conv_forward(x_image, weight, bias, {"pad": pad, "stride": stride})
    data = batchnorm_forward(data, g, b)
    data = ReLU(data)
    return data

    
s = time.time()
param = {}
files = ["conv2dkernel:0.npy", "conv2dbias:0.npy", "batch_normalizationgamma:0.npy", "batch_normalizationbeta:0.npy", 
"conv2d_1kernel:0.npy", "conv2d_1bias:0.npy", "batch_normalization_1gamma:0.npy", "batch_normalization_1beta:0.npy",
"conv2d_2kernel:0.npy", "conv2d_2bias:0.npy", "batch_normalization_2gamma:0.npy", "batch_normalization_2beta:0.npy",
 "conv2d_3kernel:0.npy", "conv2d_3bias:0.npy", "batch_normalization_3gamma:0.npy", "batch_normalization_3beta:0.npy",
  "conv2d_4kernel:0.npy", "conv2d_4bias:0.npy", "batch_normalization_4gamma:0.npy", "batch_normalization_4beta:0.npy"]
for file in files:
    p = np.load(file)
    param[file] = p
e =time.time()

data = [1] * 64
x_image = np.array(data).reshape(8,8,1)
data = conv2d(x_image, 1, 1, "conv2dkernel:0.npy", "conv2dbias:0.npy", "batch_normalizationgamma:0.npy", "batch_normalizationbeta:0.npy", param)
data = conv2d(x_image, 1, 1, "conv2d_1kernel:0.npy", "conv2d_1bias:0.npy", "batch_normalization_1gamma:0.npy", "batch_normalization_1beta:0.npy", param)
data = conv2d(x_image, 1, 1, "conv2d_2kernel:0.npy", "conv2d_2bias:0.npy", "batch_normalization_2gamma:0.npy", "batch_normalization_2beta:0.npy", param)
data = conv2d(x_image, 1, 1, "conv2d_3kernel:0.npy", "conv2d_3bias:0.npy", "batch_normalization_3gamma:0.npy", "batch_normalization_3beta:0.npy", param)
data = conv2d(x_image, 1, 1, "conv2d_4kernel:0.npy", "conv2d_4bias:0.npy", "batch_normalization_4gamma:0.npy", "batch_normalization_4beta:0.npy", param)

print(s-e)
print(data.shape)
