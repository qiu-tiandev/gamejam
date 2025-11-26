import pygame
from renderer import Renderer
import util


class Player():
    def __init__(self):
        self.renderer = util.getRenderer()
        self.renderer.createSolidTexture("Player", (0,0,0), (50,50), 1000, True)
        self.x = 10
        self.y = 10
        self.speed = 2
        self.multiplier = 50
        self.directions = {pygame.K_w: (0,-1),pygame.K_a: (-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0)}

    def detectinput(self):
        keys = pygame.key.get_pressed()
        if keys:
            dt = util.getDeltaTime()
            for key, direction in self.directions.items():
                if keys[key]: 
                    self.x += direction[0] * self.speed * dt * self.multiplier
                    self.y += direction[1] * self.speed * dt * self.multiplier


    def move(self):
        self.detectinput()
        self.renderer.render(["Player"], [(self.x, self.y)])

    def update(self):
        self.detectinput()
        
