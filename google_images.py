import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError

import numpy as np
import cv2
import face_detect as fd
import time

def find_image(query):
    """Download full size images from Google image search.
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    query = query.replace('/', ' ')
    path = 'tmp/scenes'
    BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
               'v=1.0&q=' + query + '+star+trek&start=%d&userip=69.91.178.167&safe=active&imgtype=face&imgsz=medium'

    BASE_PATH = path

    if os.path.exists(BASE_PATH + '/' + query + '.jpg'):
        print "Reusing cached image..."
        return cv2.imread(BASE_PATH + '/' + query + '.jpg')
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

    start = 0 # Google's start query string parameter for pagination.
    while True:
        r = requests.get(BASE_URL % start)
        time.sleep(1)
        for image_info in json.loads(r.text)['responseData']['results']:
            url = image_info['unescapedUrl']
            try:
                image_r = requests.get(url)
            except ConnectionError, e:
                print 'could not download %s' % url
                continue

            # Remove file-system path characters from name.
            title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')

            file = open(os.path.join(BASE_PATH, '%s.jpg') % query, 'w')
            try:
                arr = np.asarray(bytearray(image_r.content), dtype=np.uint8)
                img = cv2.imdecode(arr,-1) # 'load it as it is'
                if fd.has_face(img):
                    continue
                # save a copy of the image
                Image.open(StringIO(image_r.content)).save(file)
                return img
            except IOError, e:
                # Throw away some gifs...blegh.
                print 'could not save %s' % url
                continue
            finally:
                file.close()
        start += 4


character_lookup_keywords = ['character', 'star+trek']
def find_character(query):
    """Download full size images from Google image search.
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    query = query.replace('/', ' ')
    path = 'tmp/characters'
    BASE_PATH = path
    keywords_i = 0

    if os.path.exists(BASE_PATH + '/' + query + '.jpg'):
        print "Reusing cached image..."
        img = cv2.imread(BASE_PATH + '/' + query + '.jpg')
        results = False
        tries = 0
        while not results and tries < 20:
            print "Trying to find face again"
            results = fd.detect_face(img)
            if float(img.shape[1]) / float(img.shape[0]) > 1.5:
                print "Need to crop %s" % query
                fx, fy, fw, fh = results['face']
                img = img[max(0, fy-10):min(fy+fh+10, img.shape[0]), max(0, fx-10):min(fx+fw+10, img.shape[1])]
                results = fd.detect_face(img)
                if not results:
                  continue 

            tries += 1
        return (results, img)
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

    start = 0 # Google's start query string parameter for pagination.
    while True:
        if start > 3:
            keywords_i += 1
            start = 0
        keyword = ""
        character_name = ""
        if keywords_i < len(character_lookup_keywords):
            keyword = character_lookup_keywords[keywords_i]
            character_name = query
        elif (keywords_i < 2 * len(character_lookup_keywords)) and query.lower().endswith('s'):
            keyword = character_lookup_keywords[keywords_i - len(character_lookup_keywords)]
            character_name = query[:-1]
        else:
            character_name = 'FACE'
        print "Searching for " + character_name + " " + keyword + " " + str(start)
        BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
                 'v=1.0&q=' + character_name + '+' + keyword + '&start=%d'
        r = requests.get(BASE_URL % start)
        for image_info in json.loads(r.text)['responseData']['results']:
            url = image_info['unescapedUrl']
            try:
                image_r = requests.get(url)
            except ConnectionError, e:
                print 'could not download %s' % url
                continue

            # Remove file-system path characters from name.
            title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')

            file = open(os.path.join(BASE_PATH, '%s.jpg') % query, 'w')
            try:
                Image.open(StringIO(image_r.content)).save(file)
                file.close()
                img = cv2.imread(BASE_PATH + '/' + query + '.jpg')
                # save a copy of the image
                results = fd.detect_face(img)
                if not results:
                    continue
                if float(img.shape[1]) / float(img.shape[0]) > 1.5:
                    print "Need to crop %s" % query
                    fx, fy, fw, fh = results['face']
                    img = img[max(0, fy-10):min(fy+fh+10, img.shape[0]), max(0, fx-10):min(fx+fw+10, img.shape[1])]
                    results = fd.detect_face(img)
                    if not results:
                        continue 
                return (results, img)
            except:
                # Throw away some gifs...blegh.
                print 'could not save %s' % url
                continue
            finally:
                file.close()
        start += 4

# Example use
# find_character('data')
# find_image('the bridge')
