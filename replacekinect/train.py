import os
import h5py
import numpy as np
from keras.applications import vgg16
from keras.layers import Flatten, Dense, Input
from keras.models import Model

datafile = '/scratch/mtanveer/automanner_dataset.h5'
trainset = (34,55)
testset = (55,63)
nb_iter = 100
batch_size = 128

# Data stream generator to flow the frames from the h5 file
# TODO: Real-time augmentation (apply blur)
def data_stream(datafile,datrng,batchsize=128):
    if not os.path.isfile(datafile):
        raise IOError('File not found')
    assert type(datrng) in {list,tuple} and len(datrng) == 2 and datrng[0]<=datrng[1]
    with h5py.File(datafile,'r') as f:
        allsubj = f.keys()
        np.random.shuffle(allsubj)
        for subj in allsubj:
            if int(subj)>=datrng[0] and int(subj)<datrng[1]:
                allvids = f[subj].keys() 
                np.random.shuffle(allvids)
                for vid in allvids:
                    v = subj+'/'+vid+'/video_frames'
                    s = subj+'/'+vid+'/joints'
                    ind = 0
                    N = np.size(f[v],axis=0)
                    while ind<N:
                        end = min(ind+batchsize,N)
                        i = np.arange(end-ind)
                        np.random.shuffle(i)
                        frames,joints = f[v][ind:end,:,:,:],f[s][ind:end,:]
                        yield frames[i,:,:,:],joints[i,:]
                        ind+=batchsize

# Vgg model without fully connected layer
vggmodel = vgg16.VGG16(include_top=False)
#vggmodel.summary()

# create fully connected layer
fc_input = Input(shape=(512,5,10))
x = Flatten(name='flatten')(fc_input)
x = Dense(1024, activation='relu',name='fc1')(x)
x = Dense(1024, activation='relu',name='fc2')(x)
x = Dense(60,activation='linear',name='predictions')(x)
fcmodel = Model(fc_input,x)
fcmodel.compile(loss='mean_squared_error',optimizer='adagrad',metrics=['accuracy'])
fcmodel.summary()
print 'Fully-Connected model prepared'

# Create batch and feed the fully connected neural network
count = 0
test_stream = data_stream(datafile,testset,batchsize=1)
print 'Starting Training ... '
for iter in range(nb_iter):
    for frames, joints in data_stream(datafile,trainset):
        newinput = vggmodel.predict(frames)
        tr_loss = fcmodel.train_on_batch(newinput,joints)
        tst_frame,tst_joints = next(test_stream)
        tst_frame = vggmodel.predict(tst_frame)
        tst_loss = fcmodel.test_on_batch(tst_frame,tst_joints)
        count+=len(frames)
        print '# of Data fed:',count, 'Mean Train Loss:',np.mean(tr_loss),\
            'Test Loss:',tst_loss[0]
    print 'saving weights ...',
    fcmodel.save_weights('weightfile.h5')
    print 'done.'
print 'Training Finished'

# Create batch over test dataset and compute loss
#print 'loss calculation'
#for frames,joints in data_stream(datafile,testset):
#    newinput = vggmodel.predict(frames)
#    loss = fcmodel.test_on_batch(frames,joints)
#    print loss


    
