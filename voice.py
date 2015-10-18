#!/usr/bin/python

import subprocess
import phonemes as ph
import ffmpeg_create_video as v
import ffmpeg_add_audio as a
import pipes

# Voices:
#  0: British Male
#  1:
#
#

voices = [
  ("en1", "50", "2"),
  ("us1", "50", "1"),
  ("us2", "50", "1"),
  ("us3", "50", "2")
]

mouth_images = dict()

def generate_mouths(voice_num, phones, fps=24, scale=1.0):
    framelen = 1000.0 / fps # ms

    totaloffset = 0
    curframeend = 0

    mouths = []

    for phone in phones:
        p, dur = phone
        dur *= scale
        if p in ph.phonemes:
            face = ph.phonemes[p]
        else:
            face = ph.REST
            print "Unknown phoneme", p

        while totaloffset + dur >= curframeend:
            mouths.append(face)
            curframeend += framelen
        totaloffset += dur

    return mouths

# Given a voice number and a line of dialog, returns an array of tuples phoneme, length (ms)
def generate_line(voice_num, line, scale=1.0):
    voice, pitch, volume = voices[voice_num]
    phonemes = subprocess.check_output(["./voice.sh", voice, pitch, volume, pipes.quote(line)])

    lines = phonemes.split("\n")
    phones = []
    for i in range(len(lines)):
        phon = lines[i].split("\t")
        if len(phon) < 2:
            continue
        p, time = phon[0], phon[1]
        phones.append((p, int(time)))

    mouths = generate_mouths(voice_num, phones, scale=scale)
    mouth_img_list = []
    for mouth in mouths:
        if not mouth in mouth_images:
            path = "mouths/" + mouth
            mask_path = "mouths/mask_" + mouth
            mouth_images[mouth] = (v.load_image(path), v.load_image(mask_path))
        mouth_img_list.append(mouth_images[mouth])
    if len(mouth_img_list) == 0:
        mouth_img_list.append(mouth_images["Rest.jpg"])
    return mouth_img_list

if __name__ == "__main__":
#  text = "Data says I am incapable of any feeling. I do not think that that is a correct statement, but the matter will require further analysis. Now I am simply talking for a long time, because I do not care if I experience emotion. I am rather more interested in whether or not my lips sync properly with my audio, since I do try to act human if possible."

    text = "Space, the final frontier. These are the voyages of the starship enterprise. Its ongoing mission: to explore strange new worlds. To seek out new life, and new civilizations. To boldly go where no one has gone before. Dooooo dooooo.... doooo, dooo dooo dooo doooooooooooooooooooo... dooooo, dooooo.... dooooo, dooo doooo doooo dooooooooooo..... dooooo doooooooo, dooooo dooooooo, dooo dooo dooo dooo doooooooo..... dooooooo..... dooo doooo, doooooooooo....... dooo, dooo, dooo, dooooooooooooooooooooooooooooooo"
    au = a.OutputAudio()
    mouth_images = generate_line(0, text)
    au.addAudio("tmp/tmp.wav", 0)

    pipe = subprocess.Popen(v.ffmpeg_create_video_command, stdin = subprocess.PIPE)
    for m in mouth_images:
        pipe.stdin.write(v.as_background_image(m).tostring())
    pipe.stdin.close()

    au.combineWith("tmp/out.mp4", "final.mkv")
