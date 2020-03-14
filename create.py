import tensorflow as tf
from tensorflow import keras

import argparse
import numpy as np
import mido

# ARG PARSING
parser = argparse.ArgumentParser()
parser.add_argument("nps", help="Number of notes per block", type=int)
parser.add_argument("-s", "--single", help="Use single track data", action="store_true")
args = parser.parse_args()

nps = args.nps
single = args.single

# Function to turn np arrays back into mido format
def to_mido(arr):
    # Note must have note, velocity, time
    assert(len(arr)==3)
    return mido.Message('note_on', note=arr[0], velocity=arr[1], time=arr[2])


# Load model
if single:
    model = keras.models.load_model("saved_models/single_{}".format(nps))
else:
    model = keras.models.load_model("saved_models/both_{}".format(nps))
model.summary()

# Get inital notes to seed the model
(rows, _) = np.loadtxt("midis/single/{}/op7_1.txt".format(nps)).shape
init = np.loadtxt("midis/single/{}/op10_e05.txt".format(nps), dtype=int, max_rows=1)

# Create a new midi file
mid = mido.MidiFile()
track = mido.MidiTrack()

# Add the first 'nps-1' notes from init to our track
for i in range(nps-1):
    track.append(to_mido(init[i*3:(i*3+3)]))

# Zero out the last note
init[-3:] = 0
init = np.asarray(init).reshape(1, 12)

# Predict and generate notes
for i in range(rows-nps):
    # Predict next note
    predicted_note = np.around(model.predict(init), decimals=0).astype(int)
    # Iterate through each value to make sure its within the MIDI spec range
    for j in range(len(predicted_note[0])):
        if j%3 == 0 or j%3 == 1:
            if predicted_note[0, j] < 0:
                predicted_note[0, j] = 0
            if predicted_note[0, j] > 127:
                predicted_note[0, j] = 127
        if j%3 == 2:
            if predicted_note[0, j] < 0:
                predicted_note[0, j] = 0
    # Add the predicted note to the track
    track.append(to_mido(predicted_note[0, -3:]))
    print(predicted_note[0, -3:])
    # Shift the numbers over and pad three 0s to the end
    init = np.roll(predicted_note, -3)
    init[0, -3:] = 0

mid.tracks.append(track)
print(mid)
mid.save("midis/gen/test.mid")