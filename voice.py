#!/usr/bin/python

import subprocess
import phonemes as ph
import ffmpeg_create_video as v
import ffmpeg_add_audio as a

# Voices:
#  0: British Male
#  1: 
#
#

voices = [
  ("en1", "50", "2"),
  ("us1", "50", "1"),
  ("us2", "50", "2"),
  ("us3", "50", "2")
]

def generate_mouths(voice_num, line, fps=24, scale=1.0):
  phones = generate_line(voice_num, line)

  framelen = 1000.0 / fps # ms
  
  totaloffset = 0
  curframeend = 0

  mouths = []

  for phone in phones:
    p, dur = phone
    print p
    dur *= scale
    if p in ph.phonemes:
      face = ph.phonemes[p]
    else:
      face = ph.REST
      print "Unknown phoneme", p

    while totaloffset + dur >= curframeend:
      mouths.append(face)
      off = curframeend - totaloffset
      totaloffset += off
      curframeend += framelen
      dur -= off
    totaloffset += dur
  return mouths

# Given a voice number and a line of dialog, returns an array of tuples phoneme, length (ms)
def generate_line(voice_num, line):
  voice, pitch, volume = voices[voice_num]
  phonemes = subprocess.check_output(["./voice.sh", voice, pitch, volume, line])
  
  lines = phonemes.split("\n")
  phones = []
  for i in range(len(lines)):
    phon = lines[i].split("\t")
    if len(phon) < 2:
      continue
    p, time = phon[0], phon[1]
    phones.append((p, int(time)))
  return phones
    
if __name__ == "__main__":
  text = "Data says I am incapable of any feeling. I do not think that that is a correct statement, but the matter will require further analysis. Now I am simply talking for a long time, because I do not care if I experience emotion. I am rather more interested in whether or not my lips sync properly with my audio, since I do try to act human if possible."
  au = a.OutputAudio()
  au.addAudio("tmp/tmp.wav", 0)

#  scale = au.curlen() / 
  mouths = generate_mouths(0, text)
#  scale = au.curlen() / (len(mouths) / 24.0)
#  if abs(scale - 1.0) > .001: # Error correct
#    mouths = generate_mouths(0, text, scale=scale)

  mouth_images = dict()
  for mouth in mouths:
    if not mouth in mouth_images:
      path = "mouths/" + mouth
      print path
      mouth_images[mouth] = v.load_image(path)
  pipe = subprocess.Popen(v.ffmpeg_create_video_command, stdin = subprocess.PIPE)
  for m in mouths:
    img = mouth_images[m]
    pipe.stdin.write(v.as_background_image(img).tostring())
  pipe.stdin.close()

  au.combineWith("out.mp4", "final.mkv")
