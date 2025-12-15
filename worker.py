import pygame
from renderer import Renderer
from animations import SpriteAnimation,TypingAnimation
from player import Player
import util
import console
import entities
from world import World
from core_mechanics import InventoryManager
import psutil
import os
pygame.init()# init shit
#define screen stuff
displayInfo = pygame.display.Info()
w,h = displayInfo.current_w//2, displayInfo.current_h//2 # window is half of screen size
util.SetScreenDimensions(w,h)
screen = pygame.display.set_mode((w,h))
pygame.display.set_caption("Pygame") #title
#mainloop
clock = pygame.time.Clock()
util.setRenderer(Renderer(screen,{"chest":"Chest.png","ground":"ground_1.png","hotbar1":"Hotbar_1.png","sky1":"Sky1.png","general_items":"general_items.png"},{}))
renderer = util.getRenderer() 
renderer.ResizeTexture("chest",[50,50],True,True)
sample = TypingAnimation("Hello world. Dolorem ipsum....", (100,100),"Arial",20,(0,0,0),4)
renderer.createSolidTexture("placeholder-item", (0,0,255),(50,50),1000)
sample_ground = entities.Ground(70,"ground")
from world import Sky
sky = Sky("sky1",sample_ground.height)
sample_world = World(200)
player = Player(sample_world,sample_ground)
inventory = InventoryManager("hotbar1")# Example: inventory.addItem(1, 5)
itemManager = entities.ItemEntityManager(player, inventory, sample_ground)
from animations import SpriteAnimation
SpriteAnimation("general_items", (32,32), 9999).save_frames("items")
chestManager = entities.ChestManager(player,sample_ground,sample_world,"chest",itemManager)
while 1:
    util.SetDeltaTime()
    renderer.setBackground((255,255,255),None)
    sky.render(player.x)
    renderer.createAndRenderText("POSTEMP",str(player.x),"Arial",15,(0,0,0),(0,0),silence=True)
    sample_ground.renderGround(player)
    sample.doTypingAnimation()
    chestManager.generateAndRenderChest()
    itemManager.pickUpItems()
    itemManager.RenderItemEntities()
    proc = psutil.Process(os.getpid())
    mem_mb = proc.memory_info().rss / (1024 * 1024)
    renderer.createAndRenderText("MEMUSAGE", f"Memory: {mem_mb} MB", "Arial", 12, (255,255,255), (10, 0), cache=False, silence=True)
    inventory.renderInventory()
    player.move()
    for event in pygame.event.get(): # basic quit on signal
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN: #sum keys for input (exclude a and d for player movement)
            if pygame.K_1 <= event.key <= pygame.K_9:
                inventory.setCurrentSlot(event.key - pygame.K_0)
            elif event.key == pygame.K_0:
                inventory.setCurrentSlot(10)
            elif event.key == pygame.K_q:
                inventory.dropCurrent(itemManager, player, 1)
    pygame.display.update() # update display