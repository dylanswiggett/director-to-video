#!/usr/bin/python

import subprocess
import numpy
import cv2
import copy
import re

import star_trek_parse

import google_images as gi
import ffmpeg_add_audio as ffaa
import voice
from script import Dialog

ASPECT_RATIO = 16.0 / 9.0
VERTICAL_RESOLUTION = 720
HORIZONTAL_RESOLUTION = int(VERTICAL_RESOLUTION * ASPECT_RATIO)

FRAME_RATE = 24

VIDEO_FILENAME = 'tmp/out'

ffmpeg_create_video_command = ['ffmpeg',
        '-y', # overwrite file if it exists
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', '%dx%d' % (HORIZONTAL_RESOLUTION, VERTICAL_RESOLUTION),
        '-pix_fmt', 'rgb24',
        '-r', '%d' % FRAME_RATE,
        '-i', '-',
        '-an',
        '-b:v', '4M',
        '-vcodec', 'mpeg4',
        '%s.mp4' % VIDEO_FILENAME
        ]

def load_image(filename):
    return cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)

def draw_image(src, dst, x, y, width=0, height=0):
    if width == 0:
        height, width = src.shape[0:2]
        dst[y:(y+height), x:(x+width)] = src
    else:
        dst[y:(y+height), x:(x+width)] = cv2.resize(src, (width, height))

def fit_character(char, width, height):
    char_height, char_width = char.shape[0:2]
    char_ratio = float(char_width) / float(char_height)
    fit_ratio = float(width) / float(height)
    fit_image = None
    if char_ratio > fit_ratio:
        fit_image = cv2.resize(char, (width, int(width / char_ratio)))
    elif char_ratio < fit_ratio:
        fit_image = cv2.resize(char, (int(height * char_ratio), height))
    else:
        fit_image = cv2.resize(char, (width, height))
    return fit_image

def draw_character(char, scene, x, y, width, height):
    fit_image = fit_character(char, width, height)
    fit_height, fit_width = fit_image.shape[0:2]
    y_offset = y + (height - fit_height)
    x_offset = x + (width - fit_width) / 2
    scene[y_offset:(y_offset+fit_height), x_offset:(x_offset+fit_width)] = fit_image

def draw_mouth(mouth, character, x, y, width, height):
    fit_image = fit_character(mouth[0], width, height)
    fit_mask = fit_character(mouth[1], width, height)
    fit_height, fit_width = fit_image.shape[0:2]
    y_offset = y + (height - fit_height)
    x_offset = x + (width - fit_width) / 2
    character[y_offset:(y_offset+fit_height), x_offset:(x_offset+fit_width)] = cv2.bitwise_and(character[y_offset:(y_offset+fit_height), x_offset:(x_offset+fit_width)], fit_mask) + cv2.bitwise_and(fit_image, cv2.bitwise_not(fit_mask))

def fit_dimensions(img, fit_width, fit_height):
    image_height, image_width = img.shape[0:2]
    image_ratio = float(image_width) / float(image_height)
    fit_ratio = float(fit_width) / float(fit_height)
    fit_image = None
    if image_ratio > fit_ratio:
        fit_image = cv2.resize(img, (int(fit_height * image_ratio), fit_height))
    elif image_ratio < fit_ratio:
        fit_image = cv2.resize(img, (fit_width, int(fit_width / image_ratio)))
    else:
        fit_image = cv2.resize(img, (fit_width, fit_height))
    height, width = fit_image.shape[0:2]
    y_offset = (height - fit_height) / 2
    x_offset = (width - fit_width) / 2
    return fit_image[y_offset:y_offset+fit_height, x_offset:x_offset+fit_width]

def as_background_image(image):
    return fit_dimensions(image, HORIZONTAL_RESOLUTION, VERTICAL_RESOLUTION)

def draw_scene(background, characters, speaking, mouth, first_line):
    background = copy.copy(background)
    speaking_img = copy.copy(speaking.image)
    if not speaking.loc:
        print "Error, could not find mouth location"
        x, y, w, h = 0, 0, 100, 100
    else:
        x, y, w, h = speaking.loc['mouth']
        scale = 2
    draw_mouth(mouth, speaking_img, x-w/scale, y-w/scale, w*scale, h*scale)
    character_list = list(characters)
    speaking_index = character_list.index(speaking)
    n_characters = len(character_list)
    dx = HORIZONTAL_RESOLUTION / n_characters
    if (first_line and n_characters > 1) or (n_characters == 2):
        for i in range(n_characters):
            character = character_list[i]
            c_img = speaking_img if i == speaking_index else character.image
            background_space = int(0.4 * VERTICAL_RESOLUTION)
            draw_character(c_img, background, dx * i, background_space, dx - 20, VERTICAL_RESOLUTION - background_space)
    else:
        speaking_x = 0
        if n_characters == 1 or speaking_index < (n_characters / 2):
            speaking_x = int(0.2 * HORIZONTAL_RESOLUTION)
        else:
            speaking_x = int(0.8 * HORIZONTAL_RESOLUTION)
        speaking_width = int(0.38 * HORIZONTAL_RESOLUTION)
        fit_image = fit_character(speaking_img, speaking_width, VERTICAL_RESOLUTION)
        fit_height, fit_width = fit_image.shape[0:2]
        y_offset = VERTICAL_RESOLUTION - fit_height
        x_offset = speaking_x - fit_width / 2
        background[y_offset:(y_offset+fit_height), x_offset:(x_offset+fit_width)] = fit_image
    return background

def create_video(script):
    pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)
    totalframes = 0
    audioManager = ffaa.OutputAudio()
    i = 0
    for character in script.characters:
        script.characters[character].voice = i % 4
        i += 1

    for scene in script.scenes[:10]:
        setting_image = as_background_image(scene.setting.image)
        nchars = len(scene.characters) + 2
        dx = HORIZONTAL_RESOLUTION/nchars

        first_line = True
        for line in scene.directions:
            if not isinstance(line, Dialog):
                continue
            text_full, character = line.text, line.character
            for text in re.split(r"[.,!:;?]+", text_full):
                if len(text) > 0:
                    # Begin hax to make voices line up
                    off = float(totalframes) / 24.0 - audioManager.curlen()
                    off -= .1
                    if off < 0:
                        off = 0
                        print "THIS SHOULD ACTUALLY NEVER HAPPEN."
                    voice.generate_line(character.voice, text)
                    starttime = audioManager.curlen() + off
                    audioManager.addAudio('tmp/tmp.wav', off)
                    length = audioManager.curlen() - starttime
                    mouths = voice.generate_line(character.voice, text, length=length)
                    # End hax

                    for mouth in mouths:
                        frame = draw_scene(setting_image, scene.characters, character, mouth, first_line)
                        cv2.putText(frame, text, (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0))
                        pipe.stdin.write(frame.tostring())
                        totalframes += 1
                    while (float(totalframes) / 24.0 - audioManager.curlen()) < .1:
                        frame = draw_scene(setting_image, scene.characters, character, mouths[-1], first_line)
                        pipe.stdin.write(frame.tostring())
                        totalframes += 1
                    first_line = False
    pipe.stdin.close()
    pipe.wait()
    audioManager.combineWith('tmp/out.mp4', 'movie.mkv')

if __name__=="__main__":
    script = star_trek_parse.parse('the-defector.txt')
    create_video(script)
