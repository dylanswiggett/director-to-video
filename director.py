#!/usr/bin/python

# This will direct your movies
# They will be so good, you won't know what to do
# watch out hollywood

import star_trek_parse as parser
import google_images as gi
import ffmpeg_create_video as ffcv

TESTFILE_PATH = "the-defector.txt"

def main():
  script = parser.parse(TESTFILE_PATH)
  scene = script.scenes[0]
  scene.setting.image = gi.find_image(setting)
  print "Casting..."
  for character in scene.characters:
    print(character)
    character_data = gi.find_character(character.name)
    character.loc, character.name = character_data
  ffcv.create_video(script)
if __name__=="__main__":
    main()    
