import argparse
import numpy as np
import mido

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
mid = mido.MidiFile("./midis/base/"+file_name+'.mid', clip=True)

# Merge into a single track if flag is set
if single:
  single_track = mido.merge_tracks(mid.tracks)
  new_mid = mido.MidiFile()
  new_mid.tracks.append(single_track)
  mid = new_mid

# Init variables
metas = []
controls = []
names = []

# Find meta tracks
for track in mid.tracks:
  if len(track) < 10:
    metas.append(track)

# Remove meta tracks
for track in metas:
  mid.tracks.remove(track)

# Remove non-note messages
for track in mid.tracks:
  names.append(track.name)
  # Find control msgs
  for msg in track:
    if msg.type != 'note_on':
      controls.append(msg)

  # Remove control msgs
  for msg in controls:
    track.remove(msg)
    
  # Reset controls for next track
  controls = []

# Remove any empty tracks
i = 0
for track in mid.tracks:
  if len(track) == 0:
    mid.tracks.remove(track)
    del names[i]
  i += 1

print("names before editing: ", names)
# Names need manual changing here to make it easier to parse
# and reload data later
if single:
  names = ['single']
else:
  for i in range(len(names)):
    if 'right' in names[i] or 'Right' in names[i]:
      names[i] = 'right'
    elif 'left' in names[i] or 'Left' in names[i]:
      names[i] = 'left'
    else:
      print(names[i])

print("edited names: ", names)

# Turn tracks into np.arrays where each message is a row and
# each message is: [note, velocity, time]
# Then insert them into a dictionary with track name as the key
train_notes = {}
i = 0
for track in mid.tracks:
  track_notes = []
  for msg in track:
    track_notes.append([msg.note, msg.velocity, msg.time])
  train_notes[names[i]] = np.array(track_notes)
  i += 1

# DEBUG SECTION
# print("train_notes:\n", train_notes)
for key, notes in train_notes.items():
  print("{} has {} msgs".format(key,len(notes)))

# Turn the individual messages into blocks of length: 'nps'*3
# where each message consists of note, velocity, and time.
train_blocks = {}
for key, notes in train_notes.items():
  track_blocks = []

  # Create an empty block and add 'nps' items to it
  for index in range(len(notes)-nps+1):
    track_block = []
    for num in range(nps):
      track_block.append(notes[index+num])
    
    track_blocks.append(np.ndarray.flatten(np.array(track_block)))

  train_blocks[key] = np.array(track_blocks)

print("train_blocks:\n", train_blocks)

# DEBUG - this printout should have 'nps-1' less items
for key, notes in train_blocks.items():
  print("{} has {} msgs".format(key,len(notes)))

# Save the array out for future use
if single:
  np.savetxt("midis/single/{}/{}.txt".format(nps, file_name),train_blocks['single'])
else:
  np.savetxt("midis/left/{}/{}.txt".format(nps, file_name), train_blocks['left'])
  np.savetxt("midis/right/{}/{}.txt".format(nps, file_name), train_blocks['right'])