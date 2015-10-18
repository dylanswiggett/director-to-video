#!/usr/bin/python

class Dialog:
    def __init__(self, character, text, modifier):
        self.character = character
        self.text = text
        self.modifier = modifier

class StageDirection:
    def __init__(self, text):
        self.text = text

class Character:
    def __init__(self, name):
        self.name = name

    def setImage(self, image):
        self.image = image

class Setting:
    def __init__(self, name):
        self.name = name

class Scene:
    def __init__(self, description):
        self.description = description
        self.directions = []
        self.characters = set()
        self.setting = None

    def addDirection(self, direction):
        self.directions.append(direction)

        if type(direction) is Dialog:
            self.characters.add(direction.character)

class Script:
    def __init__(self):
        self.scenes = []
        self.characters = dict()
        
    def addScene(self, scene):
        self.scenes.append(scene)

    def addCharacter(self, name):
        self.characters[name] = Character(name)

    def getCharacter(self, name):
        return self.characters[name]
