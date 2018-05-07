import numpy as np
import time

class Predict():
    def __init__(self):
        self.param = {}
        files = ["conv2dkernel", "conv2dbias", "batch_normalizationgamma", "batch_normalizationbeta", 
        "conv2d_1kernel", "conv2d_1bias", "batch_normalization_1gamma", "batch_normalization_1beta",
        "conv2d_2kernel", "conv2d_2bias", "batch_normalization_2gamma", "batch_normalization_2beta",
        "conv2d_3kernel", "conv2d_3bias", "batch_normalization_3gamma", "batch_normalization_3beta",
        "conv2d_4kernel", "conv2d_4bias", "batch_normalization_4gamma", "batch_normalization_4beta",
        "densekernel", "densebias", "batch_normalization_5gamma", "batch_normalization_5beta",
        "dense_1kernel", "dense_1bias", "batch_normalization_6gamma", "batch_normalization_6beta",
        "dense_2kernel", "dense_2bias",
        "dense_3kernel", "dense_3bias",]

        directory = "./param/"
        extension = ".npy"
        for file in files:
            path = directory + file + extension
            self.param[file] = np.load(path)

    def batchnorm_forward(self, X, gamma, beta):
        # print(X.shape)
        if len(X.shape)>2:
            H,W,C = X.shape
            print(H,W,C)
            mu = np.mean(X, axis=(0,1))
            mu_reshape = mu.reshape(1,1,C)
            convert = np.ones((H,W,512))
            mu_broacast = (convert*mu_reshape)
            #Broadcase to (8,8,C)
            # print(mu_reshape.shape)
            # print(X.shape)
            # a = input()
            print(mu_reshape)
            print(mu_broacast.shape)
            print(mu_broacast)
            print(X.shape)
            var = np.var((X-mu_broacast)**2, axis=(0,1))
            print(var)
            a = input()
        else:
            mu = np.mean(X, axis=1)
            var = np.var(X, axis=1)

        print(X.shape)
        print(mu.shape)
        print(var.shape)

        X_norm = (X - mu) / np.sqrt(var)
        out = gamma * X_norm + beta
        return out

    def ReLU(self, x):
        return np.maximum(x, 0)

    def softmax(self, x):
        e = np.exp(x / 1.0)
        dist = e / np.sum(e)
        return dist

    def conv_forward(self, X, W, b, stride = 1, padding = 1):
        h_filter, w_filter, d_filter, n_filters  = W.shape
        h_x, w_x, c_x  = X.shape
        
        h_out = (h_x - h_filter + 2*padding) / stride + 1
        w_out = (w_x - w_filter + 2*padding) / stride + 1
        h_out, w_out = int(h_out), int(w_out)

        X_col = self.im2col_indices(X, h_filter, w_filter, padding = padding, stride = stride) # 8*8*1 -> 9*64
        W_col = W.transpose(3,2,0,1) # 3*3*1*512 -> 512 * 9
        
        W_col = W_col.reshape(n_filters, -1)

        b_col = b.reshape(b.shape[0],-1)  # 512, -> 512*1

        out = np.dot(W_col, X_col) #512*9 dot 9*64 -> 512*64

        out += b_col

        out = out.reshape(n_filters, h_out, w_out).transpose(1,2,0)
        
        return out

    def im2col_indices(self, x, field_height, field_width, padding = 1, stride = 1):
        p = padding
        x_padded = np.pad(x, ((p,p),(p,p),(0,0)), mode = 'constant')

        k,i,j = self.get_im2col_indices(x.shape, field_height, field_width, padding, stride)
    
        cols = x_padded[i,j,k]
        
        C = x.shape[2]
        # print(cols)
        cols = cols.reshape(field_height * field_width * C, -1)
        return cols

    def get_im2col_indices(self, x_shape, field_height, field_width, padding = 1, stride = 1):
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
        
    def fullDenseLayer(self, data, wPath, biasPath, gPath, bPath):
        weight = self.param[wPath]
        bias = self.param[biasPath]
        g = self.param[gPath]
        b = self.param[bPath]
        data = np.dot(data, weight) + bias
        data = self.batchnorm_forward(data,g,b)
        data = self.ReLU(data)
        return data

    def pure_dense(self, data, wPath, biasPath):
        weight = self.param[wPath]
        bias = self.param[biasPath]

        data = np.dot(data, weight) + bias
        return data

    def fullConvLayer(self, data, pad, stride, wPath, biasPath, gPath, bPath):
        weight = self.param[wPath]
        bias = self.param[biasPath]
        g = self.param[gPath]
        b = self.param[bPath]
        
        data = self.conv_forward(data, weight, bias, stride, pad)
        data = self.batchnorm_forward(data, g, b)
        data = self.ReLU(data)

        return data

    def predict(self, board):
        x_image = board.reshape(8,8,1)
    
        conv_1 = self.fullConvLayer(x_image, 1, 1, "conv2dkernel", "conv2dbias", "batch_normalizationgamma", "batch_normalizationbeta")
        conv_2 = self.fullConvLayer(conv_1, 1, 1, "conv2d_1kernel", "conv2d_1bias", "batch_normalization_1gamma", "batch_normalization_1beta")

        conv_3 = self.fullConvLayer(conv_2, 0, 1, "conv2d_2kernel", "conv2d_2bias", "batch_normalization_2gamma", "batch_normalization_2beta")
        conv_4 = self.fullConvLayer(conv_3, 0, 1, "conv2d_3kernel", "conv2d_3bias", "batch_normalization_3gamma", "batch_normalization_3beta")
        conv_5 = self.fullConvLayer(conv_4, 0, 1, "conv2d_4kernel", "conv2d_4bias", "batch_normalization_4gamma", "batch_normalization_4beta")

        conv_5_reshape = conv_5.reshape(-1,2048)

        dense_1 = self.fullDenseLayer(conv_5_reshape,"densekernel", "densebias", "batch_normalization_5gamma", "batch_normalization_5beta")
        dense_2 = self.fullDenseLayer(dense_1,"dense_1kernel", "dense_1bias", "batch_normalization_6gamma", "batch_normalization_6beta")

        pi = self.pure_dense(dense_2, "dense_2kernel", "dense_2bias")
        prob = self.softmax(pi)

        v = self.pure_dense(dense_2, "dense_3kernel", "dense_3bias")
        v = np.tanh(v)

        return prob,v

test = Predict()
data = np.array([0]+[0] * 63)
prob, v = test.predict(data)
print(prob)
print(v)
