import subprocess

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
    
 
generate_line(1, "Space... The final frontier. These are the voyages of the starship Enterprise. It's continuing mission, to explore strange new worlds. To seek out new life and new civilizations. To boldly go where no one has gone before.")
