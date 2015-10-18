#!/usr/bin/python

import subprocess
import numpy
import cv2
import copy
import re

import star_trek_parse

import pick_voice as pv
import google_images as gi
import ffmpeg_add_audio as ffaa
import voice
from script import Dialog, StageDirection, ENTER, EXIT, BACKGROUND

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
    y_offset = y + fit_height / 6
    x_offset = x + (width - fit_width) / 2
    y0, y1 = y_offset, (y_offset+fit_height)
    x0, x1 = x_offset, (x_offset+fit_width)
    fit_mask = numpy.float32(fit_mask) / 255.0
    char_region = numpy.float32(character[y0:y1,x0:x1])
    inverse_fit_mask = fit_mask * -1 + 1.0
    mul = cv2.multiply(char_region, fit_mask)
    m1 = cv2.mean(mul)
    m2 = cv2.mean(fit_mask)
    avg = numpy.float32(map(lambda x, y: x/(y * 255.0) if y else 0.0, m1, m2))
    r = numpy.ones((fit_width,fit_height),numpy.float32)  * avg[0]
    g = numpy.ones((fit_width,fit_height),numpy.float32)  * avg[1]
    b = numpy.ones((fit_width,fit_height),numpy.float32)  * avg[2]
    rgb = cv2.merge((r,g,b))
    fit_image = cv2.multiply(numpy.float32(fit_image), rgb)
    fit_image = cv2.multiply(fit_image, inverse_fit_mask)
    character[y0:y1,x0:x1] = numpy.uint8(mul + fit_image)

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

def draw_scene(background, characters_fg, characters_bg, speaking, mouth, first_line):
    background = copy.copy(background)
    speaking_img = copy.copy(speaking.image)
    scale = 2
    if not speaking.loc:
        print "Error, could not find mouth location"
        x, y, w, h = 0, 0, 100, 100
    else:
        x, y, w, h = speaking.loc['mouth']
    draw_mouth(mouth, speaking_img, x-w/scale, y-w/scale, w*scale, h*scale)
    # place characters in background
    dx_bg = HORIZONTAL_RESOLUTION / (len(characters_bg) * 2 - 1)
    for i in range(len(characters_bg)):
        character = characters_bg[i]
        c_img = speaking_img if character == speaking else character.image
        background_space = int(0.4 * VERTICAL_RESOLUTION)
        draw_character(c_img, background, dx_bg * (i * 2), 0, dx_bg, background_space)
    # place characters in foreground
    dx_fg = HORIZONTAL_RESOLUTION / max(1, len(characters_fg))
    for i in range(len(characters_fg)):
        character = characters_fg[i]
        c_img = speaking_img if character == speaking else character.image
        background_space = int(0.4 * VERTICAL_RESOLUTION)
        draw_character(c_img, background, dx_fg * i, background_space, dx_fg, VERTICAL_RESOLUTION - background_space)
    return background

def create_video(script):
    pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)
    totalframes = 0
    audioManager = ffaa.OutputAudio()
    i = 0
    for character in script.characters:
        script.characters[character].voice = pv.pick_voice(script, character)
        i += 1

    for scene in script.scenes[:4]:
        characters_on_stage = list(scene.characters)
        characters_on_stage = sorted(characters_on_stage, key=lambda character: character.name)
        characters_in_background = list()

        setting_image = as_background_image(scene.setting.image)

        first_line = True
        for line in scene.directions:
            if isinstance(line, StageDirection):
                stage_direction = line
                for action, character in stage_direction.actions:
                    if action == EXIT:
                        if character in characters_on_stage:
                            characters_on_stage.remove(character)
                        if character in characters_in_background:
                            characters_in_background.remove(character)
                    elif action == ENTER:
                        if not character in characters_on_stage:
                            if character in characters_in_background:
                                characters_in_background.remove(character)
                            characters_on_stage.append(character)
                    elif action == BACKGROUND:
                        if not character in characters_in_background and not character in characters_on_stage:
                            characters_in_background.append(character)
                continue
            elif not isinstance(line, Dialog):
                raise Exception('Line is not dialog or stage direction')
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
                        frame = draw_scene(setting_image, characters_on_stage, characters_in_background, character, mouth, first_line)
                        # supertitles
                        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                        text_point = ((HORIZONTAL_RESOLUTION - text_size[0][0])/2, 50)
                        cv2.putText(frame, text, text_point, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
                        pipe.stdin.write(frame.tostring())
                        totalframes += 1
                    while (float(totalframes) / 24.0 - audioManager.curlen()) < .1:
                        frame = draw_scene(setting_image, characters_on_stage, characters_in_background, character, mouths[-1], first_line)
                        pipe.stdin.write(frame.tostring())
                        totalframes += 1
                    first_line = False
    pipe.stdin.close()
    pipe.wait()
    audioManager.combineWith('tmp/out.mp4', 'movie.mkv')

if __name__=="__main__":
    script = star_trek_parse.parse('the-defector.txt')
    create_video(script)
