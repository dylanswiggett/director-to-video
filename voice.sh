#!/usr/bin/env bash

VOICE=$1
PITCH=$2
VOLUME=$3
TEXT=$4

espeak --punct="~" -s 140 -v mb-$VOICE -q -p $PITCH --pho --phonout=tmp/tmp.pho "$TEXT"
espeak --punct="~" -s 140 -v mb-$VOICE -p $PITCH -w tmp/tmp.wav "$TEXT"

cat tmp/tmp.pho
