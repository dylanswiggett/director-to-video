#!/usr/bin/env bash

VOICE=$1
PITCH=$2
VOLUME=$3
TEXT=$4

espeak -s 140 -v mb-$VOICE -q -p $PITCH --pho --phonout=tmp/tmp.pho "$TEXT"
mbrola -v $VOLUME /usr/share/mbrola/$VOICE/$VOICE tmp/tmp.pho tmp/tmp.wav 

cat tmp/tmp.pho
