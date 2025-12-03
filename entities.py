import util
import pygame
import random
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
        return y >= util.getScreenDimensions()[1]-self.height-50 #entity size
def isOnScreen(x,playerx):
    screenx = util.getScreenDimensions()[0]
    pos_on_screen = x - playerx + (screenx)//2
    if -100 <= pos_on_screen <= screenx + 100: # 100px allowance
        return pos_on_screen
class ItemEntityManager:
    def __init__(self,player,inventory,ground):
        self.player = player
        self.items:list[tuple[int,int,tuple[int,int]]] = []
        self.inventoryManager = inventory
        self.ground = ground
    def addItemEntities(self,id:int,amount:int,pos:tuple[int,int]):
        self.items.append((id,amount,pos))
    def pickUpItems(self):
        New = []
        for i in self.items:
            if self.player.x + 30 > i[2][0] and self.player.x < i[2][0] +30 and self.player.y+30 > self.groundy and self.player.y < self.groundy + 30:
                pass # ADD INVENTORY SHIT
                continue
            New.append(i)
        self.items = New
    def RenderItemEntities(self):
        if not self.items:
            return
        toRender = []
        for i in self.items:
            itemX,itemY = i[2]
            pos = isOnScreen(itemX,self.player.x)
            if pos:
                toRender.append((itemX,itemY))
class ChestManager:
    def __init__(self,player,ground,world,id:str):
        self.id = id
        self.renderer= util.getRenderer()
        self.player = player
        self.groundy = util.getScreenDimensions()[1]-ground.height-50
        self.spawnChance = 1/2500
        self.cooldown = 240
        self.chests = {}  #id: chestpos
        self.lastChestPos = None
        self.minDist = 500
        self.screenx,_ = util.getScreenDimensions()
        self.loot =  world.chestLoot # (item name, loot)
        self.currentId = 1
    def lootChest(self):
        playerx = self.player.x
        playery = self.player.y
        if pygame.key.get_pressed()[pygame.K_s]:
            for n,i in self.chests.items():
                if playerx + 60 > i and playerx < i +60 and playery+60 > self.groundy and playery < self.groundy + 60:  #10px distance allowance
                    del self.chests[n]
                    break
    def generateAndRenderChest(self):
        self.lootChest()
        if self.cooldown > 0:
            self.cooldown -=1
        if random.random() > self.spawnChance and (not self.lastChestPos or abs(self.player.x-(self.lastChestPos))> self.minDist) and self.cooldown ==0:
            chestPos = self.player.x + random.randint(self.screenx//2+50,self.screenx//2+300)
            self.chests[self.currentId] = chestPos
            self.currentId+=1
            self.lastChestPos = chestPos
            self.cooldown = 120
        render_pos = []
        for i in self.chests.values():
            pos_on_screen = isOnScreen(i,self.player.x)
            if pos_on_screen:
                render_pos.append((pos_on_screen,self.groundy))
        if render_pos:self.renderer.render([self.id]*len(render_pos),render_pos)
