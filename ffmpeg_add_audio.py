#!/usr/bin/python

import subprocess
import commands

# ffmpeg -y -i a.mp4 -itsoffset 00:00:30 sng.m4a -map 0:0 -map 1:0 -c:v copy -preset ultrafast -async 1 out.mp4

class OutputAudio:
    def __init__(self, temppath="tmp/audio.wav"):
        self.path = temppath
        command = "sox -n -r 22050 -c 1 %s trim 0.0 0.0" % self.path
        commands.getstatusoutput(command)

    def addAudio(self, audiopath, audiodelay, temppath="tmp/combined_audio.wav"):
        command = "sox -n -r 22050 -c 1 %s trim 0.0 %f" % (self.path + "pad.wav", audiodelay)
        commands.getstatusoutput(command)
        command = "sox %s %spad.wav %s %s" % \
                  (self.path, self.path, audiopath, temppath)
        commands.getstatusoutput(command)
        subprocess.Popen(['mv', temppath, self.path]).wait()

    def addSpeech(self, text, audiodelay, temppath="tmp/espeak_tmp.wav"):
        command = "echo \"%s\" | espeak --stdin -w %s" % (text, temppath)
        commands.getstatusoutput(command)
        self.addAudio(temppath, audiodelay)

    def combineWith(self, videopath, outputpath):
        command = 'yes | ffmpeg -i %s -i %s -strict -2 -vcodec copy %s' % \
                  (self.path, videopath, outputpath)
        commands.getstatusoutput(command)

if __name__=="__main__":
    aud = OutputAudio()
    aud.addSpeech("This cat has a mouth", 0)
    aud.addSpeech("What the fuck", 1)
    aud.addSpeech("Why would a cat have that kind of mouth", 1)
    aud.combineWith("out.mp4", "final.mkv")
