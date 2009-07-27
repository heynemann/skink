#!/usr/bin/env python
# -*- coding:utf-8 -*-

from os.path import abspath
import time

import pygame
from pygame.locals import *

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard

class SoundPlugin (Plugin):
    section = "SoundPlugin" 
    config_keys = ("audiofile", "duration")
    
    def __init__(self, configuration=None):
        super(SoundPlugin, self).__init__(configuration)

        self.audiofile = self.configuration.get('audiofile', None)
        if self.enabled and not self.audiofile:
            raise ValueError("If you enable the sound plugin you must specify the audio file.")

        self.duration = int(self.configuration.get('duration', 10))

        pygame.init()

    def on_build_failed(self, project, build):
        sound = self.load_broken_build_sound()
        sound.play()
        time.sleep(self.duration)
        sound.stop()
 
    def load_broken_build_sound(self):
        class NoneSound:
            def play(self): pass
 
        if not pygame.mixer:
            return NoneSound()
 
        fullname = abspath(self.audiofile)

        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error, message:
            print "Cannot load sound:", fullname
            raise SystemExit, message
        return sound

