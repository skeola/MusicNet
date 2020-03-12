import argparse
import numpy as np
import mido
from tempfile import TemporaryFile

# ARG PARSING
parser = argparse.ArgumentParser()
parser.add_argument("file_name", help="Midi file to load from")
parser.add_argument("nps", help="Number of notes per block", type=int)
parser.add_argument("-s", "--single", help="Whether to merge tracks into a single track", action="store_true")
args = parser.parse_args()

# Notes per block
nps = args.nps
# Flag to merge tracks or keep separate
single = args.single
# Midi file name
file_name = args.file_name

# PREPROCESSING
# We will remove all non-note messages and then turn
# the data into an array of size (# of msg x 3), where
# each message will consist of its note, velocity, and time
mid = mido.MidiFile("./midis/base/"+file_name, clip=True)

metas = []
controls = []

# Find meta tracks
for track in mid.tracks:
  if len(track) < 10:
    metas.append(track)

# Remove meta tracks
for track in metas:
  mid.tracks.remove(track)

# Remove non-note messages
for track in mid.tracks:
  # Find control msgs
  for msg in track:
    if msg.type != 'note_on':
      controls.append(msg)

  # Remove control msgs
  for msg in controls:
    track.remove(msg)

  # Reset controls for next track
  controls = []

# Turn tracks into np.arrays where each message is a row and
# each message is: [note, velocity, time]
train_blocks = []
for track in mid.tracks:
  for msg in track:
    train_blocks.append([msg.note, msg.velocity, msg.time])

# Turn list into an np.array
train_blocks = np.array(train_blocks)

# Turn the individual messages into blocks of length: 'nps'*3
# where each message consists of note, velocity, and time.
for track in mid.tracks:
  for i in range(nps-1, track.len()):
    if train_blocks == None:
      train_blocks = np.array(track)
    else:
      train_blocks.append()

# Save the array out for future use
outfile = TemporaryFile()
np.save(outfile, train_blocks)

# model = keras.Sequential([
#   keras.layers.Flatten(input_shape=(nps, 3)),
#   keras.layers.Dense(((nps-1)*3), activation='relu'),
#   keras.layers.Dense(3, activation='relu'),
#   keras.layers.Dense(((nps-1)*3), activation='relu'),
#   keras.layers.Dense((nps*3))
# ])

# model.compile(optimizer='adam', loss=tf.keras.losses.mean_squared_error, metrics=['accuracy'])
# model.fit(train_blocks, train_blocks, epochs=10)
# test_loss, test_acc = model.evaluate(train_blocks, train_blocks, verbose=2)
# print('\nTest accuracy:', test_acc)