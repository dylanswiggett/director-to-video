#!/usr/bin/env bash

VOICE=$1
PITCH=$2
VOLUME=$3
TEXT=$4

echo "$TEXT"
espeak -s 140 -v mb-$VOICE -q -p $PITCH --pho --phonout=tmp/tmp.pho "$TEXT"
espeak -s 140 -v mb-$VOICE -p $PITCH -w tmp/tmp.wav "$TEXT"
# mbrola -v $VOLUME /usr/share/mbrola/$VOICE/$VOICE tmp/tmp.pho tmp/tmp.wav 

cat tmp/tmp.pho
