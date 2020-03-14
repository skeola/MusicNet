import argparse
import numpy as np
import glob
import os

import tensorflow as tf
from tensorflow import keras

# ARG PARSING
parser = argparse.ArgumentParser()
parser.add_argument("nps", help="Number of notes per block", type=int)
group = parser.add_mutually_exclusive_group()
group.add_argument("-l", "--left", help="Use left hand data", action="store_true")
group.add_argument("-r", "--right", help="Use right hand data", action="store_true")
group.add_argument("-s", "--single", help="Use single track data", action="store_true")
args = parser.parse_args()

# Notes per block
nps = args.nps
# Flag to merge tracks or keep separate
single = args.single
right = args.right
left = args.left

# Find all matching files
if single:
  directory = "midis\single\{}".format(nps)
  file_names = glob.glob(os.path.join(directory, '*.txt'))
elif right:
  directory = "midis\right\{}".format(nps)
  file_names = glob.glob(os.path.join(directory, '*.txt'))
elif left:
  directory = "midis\left\{}".format(nps)
  file_names = glob.glob(os.path.join(directory, '*.txt'))
else:
  print("Bad flags, exiting")
  exit()


for i in range(len(file_names)):
  if i==0:
    train_data = np.array(np.loadtxt(file_names[i]))
  else:
    np.append(train_data, np.loadtxt(file_names[i]), axis=0)

print(train_data.shape)

# Hard coding in for debugging
# model = keras.Sequential([
#   keras.layers.Dense(nps*3, activation='relu'),
#   keras.layers.Dense(((nps-1)*3), activation='relu'),
#   keras.layers.Dense(3, activation='relu'),
#   keras.layers.Dense(((nps-1)*3), activation='relu'),
#   keras.layers.Dense((nps*3))
# ])
model = keras.Sequential([
  keras.layers.Dense(12, input_shape=(12,)),
  keras.layers.Dense(9, activation='relu'),
  keras.layers.Dense(6, activation='relu'),
  keras.layers.Dense(9, activation='relu'),
  keras.layers.Dense(12)
])

model.summary()

model.compile(optimizer='adam', loss=keras.losses.mean_squared_error, metrics=['accuracy'])
model.fit(train_data, train_data, epochs=1000)
test_loss, test_acc = model.evaluate(train_data, train_data, verbose=2)
print('\nTest accuracy:', test_acc)

if single:
  model.save("saved_models/single_{}".format(nps))
elif right:
  model.save("saved_models/right_{}".format(nps))
elif left:
  model.save("saved_models/left_{}".format(nps))