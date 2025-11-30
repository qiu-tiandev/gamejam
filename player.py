import pygame
from renderer import Renderer
import util
import console

class Player():
    def __init__(self,world,ground):
        self.renderer = util.getRenderer()
        self.renderer.createSolidTexture("Player", (0,0,0), (50,50), 1000, True)
        self.ground = ground 
        self.x = 10
        self.y = self.ground.height-50
        self.dt = None
        self.speed = 2
        self.multiplier = 50
        self.directions = {pygame.K_a: (-1,0),pygame.K_d:(1,0)}
        self.gravity = world.gravity
        self.jump_duration = 0.6
        self.peak_jump_duration = 0.1
        self.jumping = False
        self.jumping_start = None 
        self.jump_power = 4
    def detectinput(self):
        keys = pygame.key.get_pressed()
        self.dt = util.getDeltaTime()
        if keys:
            for key, direction in self.directions.items():
                if keys[key]: 
                    self.x += direction[0] * self.speed * self.dt * self.multiplier
                    self.y += direction[1] * self.speed * self.dt * self.multiplier
            if keys[pygame.K_SPACE]:
                if not self.jumping and self.ground.isTouchingGround(self.y):
                    self.jumping = True
                    self.jumping_start = pygame.time.get_ticks()
    def move(self):
        self.detectinput()
        if self.jumping:
            elapsed = pygame.time.get_ticks() - self.jumping_start
            if elapsed >= (self.jump_duration+self.peak_jump_duration) *1000:
                self.jumping = False
                self.jumping_start = None
            if elapsed < self.jump_duration*1000:
                self.y -=self.jump_power*self.dt*self.multiplier
        if not self.ground.isTouchingGround(self.y)and not self.jumping:
            self.y += self.gravity * self.dt
        elif not self.jumping:
            self.y = util.getScreenDimensions()[1]-self.ground.height - 50
        self.renderer.render(["Player"], [(util.getScreenDimensions()[0]//2-25, self.y)])

    def update(self):
        self.detectinput()
        
