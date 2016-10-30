from keras.applications import vgg16
from keras.layers import Flatten, Dense, Input, Dropout
from keras.layers import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.models import Model, Sequential
import h5py


# This is the original preset model configuration for 
# replacekinect project
def original(loadweights,weightfile,stop_summary):
    # Vgg model without fully connected layer
    vggmodel = vgg16.VGG16(include_top=False)
    # create fully connected layer
    fc_input = Input(shape=(512,5,10))
    x = Flatten(name='flatten')(fc_input)
    x = Dense(1024, activation='relu',name='fc1')(x)
    x = Dense(1024, activation='relu',name='fc2')(x)
    x = Dense(60,activation='linear',name='predictions')(x)
    fcmodel = Model(fc_input,x)
    # Load the model weights if instructed
    if loadweights:
        fcmodel.load_weights(weightfile)
    # Compile and print summary
    fcmodel.compile(loss='mean_squared_error',optimizer='adagrad',\
        metrics=['accuracy'])
    if not stop_summary:
        print 'Convolutional Part:'
        vggmodel.summary()
        print 'Fully Connected Part:'
        fcmodel.summary()
    print 'Model loaded'
    return vggmodel, fcmodel

# This is a preset model with four convolutional blocks
def lesscnn (loadweights,weightfile,stop_summary,nb_cnnblocks):
    # Vgg model without fully connected layer
    vggmodel = custom_vgg16(4)
    if loadweights:
        vggmodel = load_pretrained_weights(weightfile,vggmodel)
    # create fully connected layer
    fc_input = Input(shape=(512,11,20))
    x = Flatten(name='flatten_fourcnn')(fc_input)
    x = Dense(1024, activation='relu',name='fc1_fourcnn')(x)
    x = Dense(1024, activation='relu',name='fc2_fourcnn')(x)
    x = Dense(60,activation='linear',name='predictions_fourcnn')(x)
    fcmodel = Model(fc_input,x)
    # Compile and print summary
    fcmodel.compile(loss='mean_squared_error',optimizer='adagrad',\
        metrics=['accuracy'])
    if not stop_summary:
        print 'Convolutional Part:'
        vggmodel.summary()
        print 'Fully Connected Part:'
        fcmodel.summary()
    print 'Model loaded'
    return vggmodel, fcmodel

# Returns a custom vgg16 model with specified number of blocks
def custom_vgg16(total_blks):
    model = Sequential()
    model.add(ZeroPadding2D((1,1), input_shape=(3,None,None)))
    model.add(Convolution2D(64,3,3, activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Convolution2D(64,3,3, activation='relu'))
    model.add(MaxPooling2D((2,2), strides=(2,2)))

    if total_blks > 1:
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(128,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(128,3,3, activation='relu'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

    if total_blks > 2:
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(256,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(256,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(256,3,3, activation='relu'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

    if total_blks > 3:        
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512,3,3, activation='relu'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

    if total_blks > 4:
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512,3,3, activation='relu'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512,3,3, activation='relu'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))
    return model

# Loads the pretrained weights for a given vgg16 model
def load_pretrained_weights(weightfile, model):
    # Open vgg16_weights.h5
    f = h5py.File(weightfile)
    # Total number of layers in the model
    n = len(model.layers)
    for k in range(n):
        g = f['layer_{}'.format(k)]
        weights = [g['param_{}'.format(p)] for \
            p in range(g.attrs['nb_params'])]
        model.layers[k].set_weights(weights)
    f.close()
    return model