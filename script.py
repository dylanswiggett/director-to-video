#!/usr/bin/python

from difflib import SequenceMatcher

# Stage directions:
ENTER = 0
EXIT = 1
BACKGROUND = 2

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class Dialog:
    def __init__(self, character, text):
        self.character = character
        self.text = text

class StageDirection:
    def __init__(self, text, character=None):
        self.text = text
        self.character = character
        self.actions = []

    def addAction(self, action, obj):
        self.actions.append((action, obj))

class Character:
    def __init__(self, name):
        self.name = name
        self.image = None
        self.loc = None
        self.voice = 0

    def setImage(self, image):
        self.image = image

class Setting:
    def __init__(self, name):
        self.name = name
        self.image = None

class Scene:
    def __init__(self, description):
        self.description = description
        self.directions = []
        self.characters = set()
        self.setting = None

    def addDirection(self, direction):
        self.directions.append(direction)

        if isinstance(direction, Dialog):
            self.characters.add(direction.character)

    def setSetting(self, setting):
        self.setting = setting

class Script:
    def __init__(self):
        self.scenes = []
        self.characters = dict()
        self.settings = dict()

    def addScene(self, scene):
        self.scenes.append(scene)

    def addSetting(self, name):
        if name in self.settings:
            return False
        self.settings[name] = Setting(name)
        return True

    def getSetting(self, name):
        sims = [(similar(name,n),self.settings[n]) for n in self.settings]
        return max(sims)[1]

    def addCharacter(self, name):
        char = Character(name)
        names = name.split("/")
        for subname in names:
            self.characters[subname] = char

    def getCharacter(self, name):
        sims = [(similar(name,n),self.characters[n]) for n in self.characters]
        return max(sims)[1]
