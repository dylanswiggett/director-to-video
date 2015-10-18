#!/usr/bin/python

# This will direct your movies
# They will be so good, you won't know what to do
# watch out hollywood

import star_trek_parse as parser
import google_images as gi


TESTFILE_PATH = "the-defector.txt"

def main():
  script = parser.parse(TESTFILE_PATH)
  print "Designing sets..."
  for setting in script.settings:
    print(setting)
    setting_image = gi.find_image(setting)
  for character in script.characters:
    print(character)
    character_data = gi.find_character(character)
   
if __name__=="__main__":
    main()    
