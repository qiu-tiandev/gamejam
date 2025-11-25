import console
import os
import pygame
import math
class Renderer:
    def __init__(self,screen, Imagetextures: dict, TextTextures:dict[str, tuple[str,str,int,str]]): #enforce pre-rendering of textures
        self.screen = screen
        self.Imagetextures = {}
        self.TextTextures = {}
        self.visibility = {}
        self.fonts = {}
        self.background = None
        self.background_path = None
        for p,i in Imagetextures.items():
            if os.path.exists(f"assets/{i}"):
                self.Imagetextures[p] = pygame.image.load(f"assets/{i}").convert_alpha()
            else:
                console.sendError(f"Texture file assets/{i} not found.", __file__)
        for p,i in TextTextures.items(): # (text,font, font_size, Color)
            texture = self.getFont(i[1],i[2]).render(i[0],True,i[3])
            self.TextTextures[p] = texture
        console.sendInfo(f"Renderer initialized with {len(self.Imagetextures)} image textures and {len(self.TextTextures)} text textures.", __file__)
    def getFont(self,font,font_size:int):
        return self.fonts.get((font,font_size),pygame.font.SysFont(font,font_size))
    def render(self, objects: list[str],coordinates:list[tuple[int,int]]):
        for obj,(x,y) in zip(objects,coordinates):
            if not self.visibility.get(obj,True): continue
            texture = self.Imagetextures.get(obj) or self.TextTextures.get(obj)
            if not texture:
                texture = self.TextTextures.get(obj)
            if texture:
                self.screen.blit(texture, (x, y))
            else:
                console.sendError(f"Texture ID {obj.texture_id} not found in textures dictionary.", __file__)
    def createText(self, id:str, text:str,font:str, font_size:int, color:tuple[int,int,int],cache:bool=True):
        if self.Imagetextures.get(id) or self.TextTextures.get(id):
            console.sendWarning(f"Texture ID {id} already exists and will be overwritten.", __file__)
        font = self.getFont(font, font_size)
        texture = font.render(text, True, color)
        if cache:
            self.TextTextures[id] = texture
        return texture
    def createImage(self, id:str, filepath:str,size:tuple[int,int],cache:bool=True):
        if self.Imagetextures.get(id) or self.TextTextures.get(id):
            console.sendWarning(f"Texture ID {id} already exists and will be overwritten.", __file__)
        if os.path.exists(filepath):
            texture = pygame.image.load(filepath).convert_alpha()
            if size:
                texture= pygame.transform.scale(texture, size)
            if cache:
                self.Imagetextures[id] = texture
            return texture
        else:
            console.sendError(f"Image file {filepath} not found.", __file__)
    def createAndRenderText(self,id:str, text:str,font:str, font_size:int, color:tuple[int,int,int], coordinates:tuple[int,int],cache:bool=False):
        texture = self.createText(id, text,font, font_size, color, cache)
        self.screen.blit(texture, coordinates)
    def createAndRenderImage(self,id:str, filepath:str,size:tuple[int,int], coordinates:tuple[int,int],cache:bool=False):
        texture = self.createImage(id,filepath,size, cache)
        self.screen.blit(texture, coordinates)
    def createSolidTexture(self, id:str, color:tuple[int,int,int], size:tuple[int,int],numPoints:int,cache:bool=True):
        if numPoints <=2:
            console.sendWarning(f"Creating solid texture with {numPoints} points may not render correctly.", __file__)
        texture = pygame.Surface(size,pygame.SRCALPHA)
        w,h = size
        radius = min(w,h)//2
        points = []
        for i in range(numPoints):
            angle = (2 * math.pi / numPoints) * i - math.pi / 2
            x = w//2 + int(math.cos(angle) * radius)
            y = h//2 + int(math.sin(angle) * radius)
            points.append((x, y))
        pygame.draw.polygon(texture, color, points)
        if cache:
            self.Imagetextures[id] = texture
        return texture
    def createAndRenderSolidTexture(self,id:str, color:tuple[int,int,int], size:tuple[int,int], coordinates:tuple[int,int],numPoints:int,cache:bool=False):
        texture = self.createSolidTexture(id, color, size, numPoints, cache)
        self.screen.blit(texture, coordinates)
    def setBackground(self, color=None, image_path=None):
        if not color and not image_path:
            console.sendWarning("No background color or image path provided. Background will not be loaded.", __file__)
            return
        if not self.background or (self.background_path not in [image_path, color]):
            if image_path:
                if not os.path.exists(image_path):
                    return console.sendError(f"Background image file {image_path} not found.", __file__)
                self.background = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), self.screen.get_size())
                self.background_path = image_path
            else:
                background = pygame.Surface(self.screen.get_size())
                background.fill(color)
                self.background = background
                self.background_path = color
        self.screen.blit(self.background, (0, 0))
    def getTexture(self,id:str):
        return self.Imagetextures.get(id) or self.TextTextures.get(id)
    def setVisibility(self, id:str, visible:bool):
        self.visibility[id] = visible 
 