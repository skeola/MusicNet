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

if single:
  inputs = np.loadtxt("midis/single/{}/inputs.txt".format(nps))
  labels = np.loadtxt("midis/single/{}/labels.txt".format(nps))

print("Input dimensions: ", inputs.shape)
print("Label dimensions: ", labels.shape)


model = keras.Sequential([
  keras.layers.Dense(nps*3, input_dim=nps*3),
  keras.layers.Dense((nps-1)*3, activation='relu'),
  keras.layers.Dense((nps-1)*2, activation='relu'),
  keras.layers.Dense(3)
])

model.summary()

model.compile(optimizer='adam', loss=keras.losses.mean_squared_error, metrics=['accuracy'])
model.fit(inputs, labels, epochs=100, shuffle=True)
test_loss, test_acc = model.evaluate(inputs, labels, verbose=2)
print('\nTest accuracy:', test_acc)

if single:
  model.save("saved_models/single_{}".format(nps))
elif right:
  model.save("saved_models/right_{}".format(nps))
elif left:
  model.save("saved_models/left_{}".format(nps))