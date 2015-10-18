import subprocess

# Voices:
#  0: British Male
#  1: 
#
#

voices = [("en1", "50", "2")]

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
    
 
generate_line(0, "Data says I am incapable of any feeling")
