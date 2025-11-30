import util
import pygame
class Ground:
    def __init__(self,height:int,id:str):
        self.height = height
        self.renderer = util.getRenderer()
        self.id = id
        self.renderer.ResizeTexture(self.id,[None,height],True,True)
        self.texture = self.renderer.getTexture(self.id)
        self.texture_width = self.texture.get_width()
    def renderGround(self,player):
        offset = -(player.x%self.texture_width)
        screenx,screeny = util.getScreenDimensions()
        x = offset - self.texture_width if offset > 0 else offset
        while x < screenx:
            src = max(0, -x)
            dst = max(0, x)
            visible_width = min(self.texture_width - src, screenx - dst)
            cropped = self.texture.subsurface(pygame.Rect(src, 0, visible_width, self.height))
            self.renderer.screen.blit(cropped, (dst, screeny - self.height))
            x += self.texture_width

    def isTouchingGround(self,y):
        return y >= util.getScreenDimensions()[1]-self.height-50 #entity size+ 5px pad