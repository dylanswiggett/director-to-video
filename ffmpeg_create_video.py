#!/usr/bin/python

import subprocess
import numpy
import cv2
import copy

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

def draw_character(char, scene, x, y, width, height):
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
	fit_height, fit_width = fit_image.shape[0:2]
	y_offset = y + (height - fit_height)
	x_offset = x + (width - fit_width) / 2
	scene[y_offset:(y_offset+fit_height), x_offset:(x_offset+fit_width)] = fit_image

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

def draw_scene(background, characters, speaking, mouth):
        print speaking.name + " is speaking"
        background = copy.copy(background)
        speaking_img = copy.copy(speaking.image)
        if not speaking.loc:
          print "Error, could not find mouth location"
          x, y, w, h = 0, 0, 100, 100
        else:
          x, y, w, h = speaking.loc['mouth'] 
        draw_character(mouth, speaking_img, x, y, w, h)
        nchars = len(characters) + 2
        dx = HORIZONTAL_RESOLUTION/nchars
        i = 0
        for character in characters:
            c_img = speaking_img if character == speaking else character.image
            draw_character(c_img, background, dx * i, 0, dx - 10, VERTICAL_RESOLUTION)
            i += 1
        return background

def create_video(script):
	pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)
	scene = script.scenes[10]
        audioManager = ffaa.OutputAudio()
        setting_image = as_background_image(scene.setting.image)
        nchars = len(scene.characters) + 2
        dx = HORIZONTAL_RESOLUTION/nchars
        i = 0
        totalframes = 0
        for character in scene.characters:
            character.voice = i % 4 
            i += 1
        for line in scene.directions:
            startframes = totalframes
            if not isinstance(line, Dialog):
                    continue
            text, character = line.text, line.character
            mouths = voice.generate_line(character.voice, text)
            for mouth in mouths:
                frame = draw_scene(setting_image, scene.characters, character, mouth)
                pipe.stdin.write(frame.tostring())
                totalframes += 1
            for i in range(0,5):
                    frame = draw_scene(setting_image, scene.characters, character, mouths[-1])
                    pipe.stdin.write(frame.tostring())
                    totalframes += 1
            off = float(startframes) / 24.0 - audioManager.curlen()
            if off < 0: off = 0
            audioManager.addAudio('tmp/tmp.wav', off)
	pipe.stdin.close()
        pipe.wait()
        audioManager.combineWith('tmp/out.mp4', 'movie.mkv')

if __name__=="__main__":
	script = star_trek_parse.parse('the-defector.txt')
	create_video(script)
