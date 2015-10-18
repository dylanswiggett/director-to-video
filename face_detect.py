#!/usr/bin/env python2

"""
OpenCV example. Show webcam image and detect face.
"""

import cv2

FACESET = "haar/lbpcascade_frontalface.xml"
MOUTHSET = "haar/Mouth.xml"
EYESET = "haar/parojos.xml"

def draw_rects(classifier, frame):
    rects = classifier.detectMultiScale(frame)
    for r in rects:
        x, y, w, h = r
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255))

face_classifier = cv2.CascadeClassifier(FACESET)
mouth_classifier = cv2.CascadeClassifier(MOUTHSET)
eye_classifier = cv2.CascadeClassifier(EYESET)

def has_face(img):
    return len(face_classifier.detectMultiScale(img)) > 0

DOWNSCALE = 1
# returns information about image
def detect_face(img):

    minisize = (img.shape[1]/DOWNSCALE,img.shape[0]/DOWNSCALE)
    miniframe = cv2.resize(img, minisize)
    faces = face_classifier.detectMultiScale(miniframe)
    mouths = mouth_classifier.detectMultiScale(miniframe)
    if len(faces) != 1:
        return False
    f = [v*DOWNSCALE for v in faces[0]]
    y1 = f[1] + f[3]/2
    y2 = f[1] + f[3]
    x1 = f[0]
    x2 = f[0] + f[2]
    the_mouth = None
    the_mouth_size = 0
    for m in mouths:
        m = [v*DOWNSCALE for v in m]
        if m[0] < x1 or m[0] + m[2] > x2:
            continue
        if m[1] < y1 or m[1] + m[3] > y2:
            continue
        if the_mouth_size < m[1]:
            the_mouth = m
            the_mouth_size = m[1]
    if the_mouth == None:
        return False
    return {
      'face': [v*DOWNSCALE for v in f],
      'mouth': [v*DOWNSCALE for v in the_mouth]
    }
