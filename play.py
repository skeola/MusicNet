import pygame
import os
import sys
from mido import MidiFile

# FUNCTION DEFS
# Takes file name and then plays the midi file
def play_music(music_file):
  clock = pygame.time.Clock()
  try:
    pygame.mixer.music.load(music_file)
    print("Music file is loaded")
  except pygame.error:
      print("File not found")
      return
  pygame.mixer.music.play()
  while pygame.mixer.music.get_busy():
      clock.tick(30)

# ARG PARSING
if len(sys.argv) == 1:
  print("Need audio file to play")
else:
  if sys.argv[1] == None:
    print("Need file name")
    exit()
  else:
    file_name = sys.argv[1]

# PLAY TRACK
pygame.mixer.init(44100, -16, 2, 1024)

pygame.mixer.music.set_volume(0.8)

try:
  play_music("./midis/"+file_name)
except KeyboardInterrupt:
  pygame.mixer.music.fadeout(1000)
  pygame.mixer.music.stop()
  raise SystemExit