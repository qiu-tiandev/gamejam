import pygame
from renderer import Renderer
from renderer_manager import getRenderer


class Player():
    def __init__(self, dt):
        self.renderer = getRenderer()
        self.renderer.createSolidTexture("Player", (0,0,0), (50,50), 1000000, True)
        self.dt = dt
        self.x = 10
        self.y = 10

    def detectinput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y += -1
        if keys[pygame.K_a]:
            self.x += -1
        if keys[pygame.K_s]:
            self.y += 1
        if keys[pygame.K_d]:
            self.x += 1

    def move(self):
        self.detectinput()
        self.renderer.render(["Player"], [(self.x, self.y)])

    def update(self):
        self.detectinput()
        
