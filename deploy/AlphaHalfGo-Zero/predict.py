import numpy as np
import time

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

def conv_forward(X, W, b, stride = 1, padding = 1):
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
    
def fullDenseLayer(data, wPath, biasPath, gPath, bPath, param):
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

def fullConvLayer(data, pad, stride, wPath, biasPath, gPath, bPath, param):
    weight = param[wPath]
    bias = param[biasPath]
    g = param[gPath]
    b = param[bPath]
    
    data = conv_forward(data, weight, bias, stride, pad)
    data = batchnorm_forward(data, g, b)
    data = ReLU(data)

    return data

param = {}
files = ["conv2dkernel", "conv2dbias", "batch_normalizationgamma", "batch_normalizationbeta.npy", 
"conv2d_1kernel:0.npy", "conv2d_1bias:0.npy", "batch_normalization_1gamma", "batch_normalization_1beta.npy",
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

