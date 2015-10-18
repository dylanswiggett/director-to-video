#!/usr/bin/python

import subprocess
import commands
import re

# ffmpeg -y -i a.mp4 -itsoffset 00:00:30 sng.m4a -map 0:0 -map 1:0 -c:v copy -preset ultrafast -async 1 out.mp4

class OutputAudio:
    def __init__(self, temppath="tmp/audio.wav"):
        self.path = temppath
        command = "sox -n -r 22050 -c 1 %s trim 0.0 0.0" % self.path
        commands.getstatusoutput(command)

    def addAudio(self, audiopath, audiodelay, temppath="tmp/combined_audio.wav"):
        command = "sox -c 1 %s tmp/out.wav rate 22050" % audiopath
        commands.getstatusoutput(command)
        command = "sox -n -r 22050 -c 1 %s trim 0.0 %f" % (self.path + "pad.wav", audiodelay)
        commands.getstatusoutput(command)
        command = "sox %s %spad.wav %s %s" % \
                  (self.path, self.path, "tmp/out.wav", temppath)

        for line in commands.getstatusoutput(command):
            print line
        subprocess.Popen(['mv', temppath, self.path]).wait()

    def addSpeech(self, text, audiodelay, voice=("en1","50","2"), temppath="tmp/espeak_tmp.wav"):
        command = "echo \"%s\" | espeak -s 140 -v mb-%s -q -p %s --stdin -w %s" % \
                  (text, voice[0], voice[1], temppath)
        commands.getstatusoutput(command)
        self.addAudio(temppath, audiodelay)

    def combineWith(self, videopath, outputpath):
        command = 'yes | ffmpeg -i %s -i %s -strict -2 -vcodec copy %s' % \
                  (self.path, videopath, outputpath)
        commands.getstatusoutput(command)

    def curlen(self):
        command = 'soxi %s' % self.path
        for line in commands.getstatusoutput(command)[1:]:
            if "Duration" in line:
                res = re.search(r'(\d+):(\d+):(\d+).(\d+)', line)
                h,m,s,cs = res.group(1), res.group(2), res.group(3), res.group(4)
                return int(h) * 3600.0 + int(m) * 60.0 + int(s) + int(cs) * .01
        return 0


if __name__=="__main__":
    aud = OutputAudio()
    aud.addSpeech("This cat has a mouth", 0)
    aud.addSpeech("What the fuck", 1)
    aud.addSpeech("Why would a cat have that kind of mouth", 1)
    aud.combineWith("out.mp4", "final.mkv")
