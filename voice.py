import subprocess

# Voices:
#  0: British Male
#  1: 
#
#

consonants = [
  'p', 'b',
  't', 'd',
  'tS', # CHurch
  'dZ', # juDGe
  'k', 'g',
  'f', 'v',
  'T', # THin
  'D', # THis
  's', 'z',
  'S', # SHop
  'Z', # pleaSure
  'h',

  'm', 'n',
  'N', # siNG
  'l', 'r',
  'j', #Yes
  'w',
  'C', #German ich
  'x', #German ch
  'l^', #Italian GLi
  'n^', #Spanish n~
]

vowels = [
  '@', #alphA
  '3', #bettER
  '3:', #nURse
  '@L', #simpLE
  '@2', #the
  '@5', #to
  'a',
  'aa',
  'a#',
  'A:',
  'A@',
  'E',
  'e@',
  'I',
  'I2',
  'i',
  'i:',
  'i@',
  '0',
  'V',
  'u:',
  'U',
  'U@',
  'O:',
  'O@',
  'o@',
  'aI',
  'eI',
  'OI',
  'aU',
  'oU',
  'aI@',
  'aU@'
]

voices = [("en1", "50", "2")]

def generate_line(voice_num, line):
  voice, pitch, volume = voices[voice_num]
  phonemes = subprocess.check_output(["./voice.sh", voice, pitch, volume, line])
  
  lines = phonemes.split("\n")
  for i in range(len(lines)):
    phon = lines[i].split("\t")
    if len(phon) < 2:
      continue
    p, time = phon[0], phon[1]
    is_vowel = p in vowels
    print(p, time, is_vowel)
 
generate_line(0, "Data says I am incapable of any feeling")
