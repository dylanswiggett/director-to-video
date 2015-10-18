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

# returns information about image
def detect_face(img):
    faces = face_classifier.detectMultiScale(img)
    mouths = mouth_classifier.detectMultiScale(img, 1.1, 2)
    if len(faces) != 1:
        return False
    f = faces[0]
    y1 = f[1] + f[3]/2
    y2 = f[1] + f[3]
    x1 = f[0]
    x2 = f[0] + f[2]
    the_mouth = None
    the_mouth_size = 0
    for m in mouths:
        if m[0] + 15 < x1 or m[0] + m[2] > x2 + 15:
            continue
        if m[1] + 15 < y1 or m[1] + m[3] > y2 + 15:
            continue
        if the_mouth_size < m[2]:
            the_mouth = m
            the_mouth_size = m[2]
    if the_mouth == None:
        return False
    return {
      'face': f,
      'mouth': the_mouth
    }
