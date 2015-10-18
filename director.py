#!/usr/bin/python

# This will direct your movies
# They will be so good, you won't know what to do
# watch out hollywood

import star_trek_parse as parser
import google_images as gi
import ffmpeg_create_video as ffcv
import cv2

TESTFILE_PATH = "clues.txt"

def main():
  script = parser.parse(TESTFILE_PATH)
  scene = script.scenes[12]
  scene.setting.image = cv2.cvtColor(gi.find_image(scene.setting.name), cv2.COLOR_BGR2RGB)
  print "Casting..."
  for character in scene.characters:
    print(character.name)
    character_data = gi.find_character(character.name)
    loc, image = character_data
    print loc
    character.loc = loc
    character.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  ffcv.create_video(script)
if __name__=="__main__":
    main()    
