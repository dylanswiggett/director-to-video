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

VIDEO_FILENAME = 'out'

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

def draw_image(src, dst, x, y, width, height):
	dst[y:(y+height), x:(x+width)] = cv2.resize(src, (width, height))

def as_background_image(img):
	height, width = img.shape[0:2]
	ratio = float(width) / float(height)
	background_image = None
	if ratio > ASPECT_RATIO:
		background_image = cv2.resize(img, (int(VERTICAL_RESOLUTION * ratio), VERTICAL_RESOLUTION))
	elif ratio < ASPECT_RATIO:
		background_image = cv2.resize(img, (HORIZONTAL_RESOLUTION, int(HORIZONTAL_RESOLUTION / ratio)))
	else:
		background_image = cv2.resize(img, (HORIZONTAL_RESOLUTION, VERTICAL_RESOLUTION))
	return background_image[0:VERTICAL_RESOLUTION, 0:HORIZONTAL_RESOLUTION]

def create_video(script):
        setting_images[setting] = as_background_image(cv2.cvtColor(gi.find_image(setting), cv2.COLOR_BGR2RGB))
	pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)
	for scene in script.scenes:
		setting_image = setting_images[scene.setting.name]
		for character in scene.characters:
                           
                for j in range(24):
			pipe.stdin.write(setting_image.tostring())
	pipe.stdin.close()

if __name__=="__main__":
	script = star_trek_parse.parse('the-defector.txt')
	create_video(script)

"""
cat_closed_image = as_background_image(load_image('characters/cat.jpg'))
#cat_closed_image = cv2.imread('characters/cat.jpg')
cat_open_image = copy.copy(cat_closed_image)

mouth_closed_image = load_image('mouths/Rest.jpg')
draw_image(mouth_closed_image, cat_closed_image, 350, 250, 100, 100);
mouth_open_image = load_image('mouths/O.jpg')
draw_image(mouth_open_image, cat_open_image, 350, 250, 100, 100);

#cv2.rectangle(cat_open_image, (400, 200), (500, 300), (0, 0, 0), thickness=-1)

pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)

for i in range(5):
	for j in range(12):
		pipe.stdin.write(cat_closed_image.tostring())
	for j in range(12):
		pipe.stdin.write(cat_open_image.tostring())

pipe.stdin.close()
"""
