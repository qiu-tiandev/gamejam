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
        self._cached_dims = (0, 0)
        self._screenx = 0
        self._screeny = 0
        self._updateDims()
    def _updateDims(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self._screenx = w
        self._screeny = h
    def renderGround(self,player):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self._updateDims()
        offset = -(player.x % self.texture_width)
        screenx = self._screenx
        screeny = self._screeny
        x = offset - self.texture_width if offset > 0 else offset
        while x < screenx:
            src = max(0, -x)
            dst = max(0, x)
            visible_width = min(self.texture_width - src, screenx - dst)
            cropped = self.texture.subsurface(pygame.Rect(src, 0, visible_width, self.height))
            self.renderer.render_surface(cropped, (dst, screeny - self.height))
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
        self.items:list[dict] = []
        self.inventoryManager = inventory
        self.ground = ground
        self.renderer = util.getRenderer()
        self._cached_dims = (0, 0)
        self._scale_factor = 1.0
        self.groundy = 0
        self.updateGroundY()
    def updateGroundY(self):
        w, h = util.getScreenDimensions()
        old_groundy = self.groundy
        self._cached_dims = (w, h)
        self.groundy = h - self.ground.height - 32
        self._scale_factor = max(0.5, h / 720)
        if old_groundy != 0 and old_groundy != self.groundy:
            for item in self.items:
                item["pos"] = (item["pos"][0], self.groundy)
    def addItemEntities(self,id:int,amount:int,pos:tuple[int,int]):
        now = pygame.time.get_ticks()
        count = min(amount, 10)
        base_x, _ = pos
        for i in range(count):
            ox = random.randint(-40, 40)
            self.items.append({"id": id, "amount": 1, "pos": (base_x + ox, self.groundy), "spawn": now})
        remaining = amount - count
        if remaining > 0:
            self.items.append({"id": id, "amount": remaining, "pos": (base_x, self.groundy), "spawn": now})
    def pickUpItems(self):
        New = []
        now = pygame.time.get_ticks()
        for i in self.items:
            itemX,itemY = i["pos"]
            if now - i["spawn"] < 2000:
                New.append(i)
                continue
            if self.player.x + 30 > itemX and self.player.x < itemX + 30 and self.player.y+30 > self.groundy and self.player.y < self.groundy + 30:
                self.inventoryManager.addItem(i["id"], i["amount"])
                continue
            New.append(i)
        self.items = New
    def RenderItemEntities(self):
        if not self.items:
            return
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.updateGroundY()
        render_ids = []
        render_pos = []
        scale_factor = self._scale_factor
        player_x = self.player.x
        for i in self.items:
            itemX, itemY = i["pos"]
            pos = isOnScreen(itemX, player_x)
            if pos is not None:
                tex_id = f"items_{i['id']:03d}"
                if self.renderer.getTexture(tex_id) is None:
                    tex_id = "placeholder-item"
                render_ids.append(tex_id)
                render_pos.append((int(pos), int(itemY)))
        if render_ids:
            self.renderer.render(render_ids, render_pos)
class ChestManager:
    def __init__(self,player,ground,world,id:str,itemManager:ItemEntityManager):
        self.id = id
        self.renderer= util.getRenderer()
        self.player = player
        self.ground = ground
        self.spawnChance = 1/2500
        self.cooldown = 240
        self.chests = {0:200}  #id: chestpos| starter chest will gen x=200
        self.lastChestPos = None
        self.minDist = 500
        self.loot =  world.chestLoot # (item name -> (min,max))
        self.currentId = 1
        self.itemManager = itemManager
        self._cached_dims = (0, 0)
        self.groundy = 0
        self.screenx = 0
        self.updateGroundY()
    def updateGroundY(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self.groundy = h - self.ground.height - 50
        self.screenx = w
    def lootChest(self):
        playerx = self.player.x
        playery = self.player.y
        if pygame.key.get_pressed()[pygame.K_s]:
            for n,i in self.chests.items():
                if playerx + 60 > i and playerx < i +60 and playery+60 > self.groundy and playery < self.groundy + 60:  #10px distance allowance
                    for name,(mn,mx) in self.loot.items():
                        item_id = util.getItemID(name)
                        amt = random.randint(mn,mx)
                        drop_x = i + random.randint(-20,20)
                        self.itemManager.addItemEntities(item_id, amt, (drop_x, self.groundy))
                    del self.chests[n]
                    break
    def generateAndRenderChest(self):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.updateGroundY()
        self.lootChest()
        if self.cooldown > 0:
            self.cooldown -=1
        if random.random() < self.spawnChance and self.cooldown == 0:
            if not self.lastChestPos or abs(self.player.x - self.lastChestPos) > self.minDist:
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
