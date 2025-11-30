import pygame
import util
import console
class SpriteAnimation:
    def __init__(self, spriteid:str, spriteSize:tuple[int,int],numSprites:int, position:tuple[int,int]):
        self.renderer = util.getRenderer()
        self.spritesheet = self.renderer.getTexture(spriteid)
        self.position = position
        self.spriteid = spriteid
        self.numSpriteW = self.spritesheet.get_width() // spriteSize[0]
        self.numSpriteH = self.spritesheet.get_height() // spriteSize[1]
        if not self.spritesheet:
            console.sendError(f"Sprite ID {self.spriteid} not found for animation.", __file__)
            return
        self.InternalCache = []
        for HorizontalFrames in range(self.numSpriteW):
            for VerticalFrames in range(self.numSpriteH):
                rect = pygame.Rect(HorizontalFrames * spriteSize[0], VerticalFrames * spriteSize[1], spriteSize[0], spriteSize[1])
                self.InternalCache.append(self.spritesheet.subsurface(rect))
    def doSpriteAnimation(self,frame:int):
        self.renderer.render(self.InternalCache[frame-1], [self.position])
class TypingAnimation: # WARNING NOT DONE
    def __init__(self, text:str, position:tuple[int,int], font:str, font_size:int, color:tuple[int,int,int], speed:float):
        self.renderer = util.getRenderer()
        self.text = text
        self.position = position
        self.font = font
        self.font_size = font_size
        self.color = color
        self.SecondsPerChar = 1/(5*speed)
        self.current_index = 0
        self.startTime= None
        self.currentText = ""
        self.renderer.createText("TEMPTYPINGANIMATION","",self.font,self.font_size,self.color,True)
    def doTypingAnimation(self):
        if self.startTime is None:
            self.startTime = pygame.time.get_ticks()
        elapsed = pygame.time.get_ticks() - self.startTime
        if elapsed >= (self.SecondsPerChar * 1000):
            if self.current_index == len(self.text)-1:
                return True
            self.current_index += 1
            self.renderer.createAndRenderText("TEMPTYPINGANIMATION",self.text[:self.current_index], self.font, self.font_size, self.color, self.position, True,True)
            self.startTime = pygame.time.get_ticks()
        else:
            self.renderer.render(["TEMPTYPINGANIMATION"],[self.position])