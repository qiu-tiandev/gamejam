import console
import os
import pygame
import math
class Renderer:
    def __init__(self, Imagetextures: dict, TextTextures:dict[str, tuple[str]]): #enforce pre-rendering of textures
        self.font = pygame.font.SysFont('Arial', 25)
        self.Imagetextures = {}
        self.TextTextures = {}
        self.background = None
        for p,i in Imagetextures.items():
            if os.path.exists(f"assets/{i}"):
                self.Imagetextures[p] = pygame.image.load(f"assets/{i}").convert_alpha()
            else:
                console.sendError(f"Texture file assets/{i} not found.", __file__)
        for p,i in TextTextures.items(): # (text, font_size, Color)
            texture = self.font.render(i[0],True,i[2])
            self.TextTextures[p] = texture
        console.sendInfo(f"Renderer initialized with {len(self.Imagetextures)} image textures and {len(self.TextTextures)} text textures.", __file__)
    def render(self, screen, objects: list[str],coordinates:list[tuple[int,int]]):
        for obj,(x,y) in zip(objects,coordinates):
            if getattr(obj, "visible") == True: continue
            texture = self.Imagetextures.get(obj.texture_id)
            if not texture:
                texture = self.TextTextures.get(obj.texture_id)
            if texture:
                screen.blit(texture, (x, y))
            else:
                console.sendError(f"Texture ID {obj.texture_id} not found in textures dictionary.", __file__)
    def createText(self, id:str, text:str, font_size:int, color:tuple[int,int,int],cache:bool=True):
        if self.Imagetextures.get(id) or self.TextTextures.get(id):
            console.sendWarning(f"Texture ID {id} already exists and will be overwritten.", __file__)
        font = pygame.font.SysFont('Arial', font_size)
        texture = font.render(text, True, color)
        if cache:
            self.TextTextures[id] = texture
        return texture
    def createImage(self, id:str, filepath:str,size:tuple[int,int],cache:bool=True):
        if self.Imagetextures.get(id) or self.TextTextures.get(id):
            console.sendWarning(f"Texture ID {id} already exists and will be overwritten.", __file__)
        if os.path.exists(filepath):
            texture= pygame.transform.scale(pygame.image.load(filepath).convert_alpha(), size)
            if cache:
                self.Imagetextures[id] = texture
            return texture
        else:
            console.sendError(f"Image file {filepath} not found.", __file__)
    def createAndRenderText(self, screen,id:str, text:str, font_size:int, color:tuple[int,int,int], coordinates:tuple[int,int],cache:bool=False):
        texture = self.createText(id, text, font_size, color, cache)
        screen.blit(texture, coordinates)
    def createAndRenderImage(self,screen,id:str, filepath:str, coordinates:tuple[int,int],cache:bool=False):
        texture = self.createImage(id,filepath, cache)
        screen.blit(texture, coordinates)
    def createSolidTexture(self, id:str, color:tuple[int,int,int], size:tuple[int,int],numPoints:int,cache:bool=True):
        if numPoints <=2:
            console.sendWarning(f"Creating solid texture with {numPoints} points may not render correctly.", __file__)
        texture = pygame.Surface(size)
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
    def createAndRenderSolidTexture(self,id:str, screen, color:tuple[int,int,int], size:tuple[int,int], coordinates:tuple[int,int],numPoints:int,cache:bool=False):
        texture = self.createSolidTexture(id, color, size, numPoints, cache)
        screen.blit(texture, coordinates)
    def setBackground(self, screen, color=None, image_path=None):
        if not color and not image_path:
            console.sendWarning("No background color or image path provided. Background will not be loaded", __file__)
            return
        if not self.background or (color != background and image_path != self.background):
            if image_path and os.path.exists(image_path):
                self.background = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), screen.get_size())
            background = pygame.Surface(screen.get_size())
            background = background.convert() 
            self.background= background.fill(color)
        screen.blit(self.background, (0, 0))
    def setVisibility(self, id, visible:bool):
        setattr(id, "visible", visible)
 