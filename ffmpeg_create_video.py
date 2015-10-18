#!/usr/bin/python

import subprocess
import numpy
import cv2
import copy

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
	'-vcodec', 'mpeg4',
	'%s.mp4' % VIDEO_FILENAME
	]

def draw_image(src, dst, x, y, width, height):
	dst[y:(y+height), x:(x+width)] = cv2.resize(src, (width, height))

cat_closed_image = cv2.imread('characters/cat.jpg')
cat_open_image = copy.copy(cat_closed_image)

mouth_closed_image = cv2.imread('mouths/Rest.jpg')
draw_image(mouth_closed_image, cat_closed_image, 350, 250, 100, 100);
mouth_open_image = cv2.imread('mouths/O.jpg')
draw_image(mouth_open_image, cat_open_image, 350, 250, 100, 100);

#cv2.rectangle(cat_open_image, (400, 200), (500, 300), (0, 0, 0), thickness=-1)

pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)

for i in range(10):
	for j in range(12):
		pipe.stdin.write(cat_closed_image.tostring())
	for j in range(12):
		pipe.stdin.write(cat_open_image.tostring())

pipe.stdin.close()
