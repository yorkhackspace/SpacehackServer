#!/usr/bin/env python
"""Play a game"""

import pygame
import os

for filename in os.listdir("."):

        print filename
        if not filename[-4:] == ".mp3":
                continue
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)
