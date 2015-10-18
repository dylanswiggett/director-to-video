#!/usr/bin/python

import subprocess
import numpy
import cv2
import copy

import star_trek_parse

import google_images as gi

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

def create_video(script):
	pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)
	scene = script.scenes[0]
        setting_image = as_background_image(scene.setting.image)
        nchars = len(scene.characters) + 2
        dx = HORIZONTAL_RESOLUTION/nchars
        i = 0
        for character in scene.characters:
                char_img = fit_dimensions(character.image, dx-10, VERTICAL_RESOLUTION)
                print(type(char_img))
                draw_image(char_img, setting_image, dx*i, 0)
                i += 1
                
        for j in range(24):
                pipe.stdin.write(setting_image.tostring())
	pipe.stdin.close()

if __name__=="__main__":
	script = star_trek_parse.parse('the-defector.txt')
	create_video(script)
