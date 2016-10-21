import os
import h5py
import numpy as np
from keras.applications import vgg16
from keras.layers import Flatten, Dense, Input
from keras.models import Model
from skeletonutils import skelviz_mayavi as sviz
from skeletonutils import data_stream_shuffle
import matplotlib.pyplot as plt

#datafile = '/scratch/mtanveer/automanner_dataset.h5'
datafile = '/Users/itanveer/Data/ROCSpeak_BL/allData_h5/automanner_dataset.h5'
trainset = (34,55)
testset = (55,63)

# Vgg model without fully connected layer
vggmodel = vgg16.VGG16(include_top=False)

# create fully connected layer
fc_input = Input(shape=(512,5,10))
x = Flatten(name='flatten')(fc_input)
x = Dense(1024, activation='relu',name='fc1')(x)
x = Dense(1024, activation='relu',name='fc2')(x)
x = Dense(60,activation='linear',name='predictions')(x)
fcmodel = Model(fc_input,x)
fcmodel.summary()
#fcmodel.compile(loss='mean_squared_error',optimizer='adagrad',metrics=['accuracy'])
fcmodel.load_weights('weightfile.h5')
fcmodel.compile(loss='mean_squared_error',optimizer='adagrad',metrics=['accuracy'])
print 'Model Loaded'

# Create batch over test dataset and compute loss
print 'loss calculation'
for frames,joints in data_stream_shuffle(datafile,trainset):
    # Get the prediction
    newinput = vggmodel.predict(frames[:1,:,:,:])
    newoutput = np.insert(fcmodel.predict(newinput)[0,:],0,[0,0])    
    plt.imshow(np.transpose(frames[0,:,:,:],axes=[1,2,0]))
    plt.ion()
    plt.show()
    sviz.drawskel(newoutput)


