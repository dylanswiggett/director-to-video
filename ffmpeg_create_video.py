import subprocess
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

cat_image = cv2.imread('tmp/cat.jpg')
cat_open_image = copy.copy(cat_image)
#cat2_image = cv2.imread('tmp/cat2.jpg')

cv2.rectangle(cat_open_image, (400, 200), (500, 300), (0, 0, 0), thickness=-1)

pipe = subprocess.Popen(ffmpeg_create_video_command, stdin=subprocess.PIPE)

for i in range(10):
	for j in range(12):
		pipe.stdin.write(cat_image.tostring())
	for j in range(12):
		pipe.stdin.write(cat_open_image.tostring())

pipe.stdin.close()
