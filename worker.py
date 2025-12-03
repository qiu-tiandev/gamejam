import pygame
from renderer import Renderer
from animations import SpriteAnimation,TypingAnimation
from player import Player
import util
import console
import util
import entities
from world import World
pygame.init()# init shit
#define screen stuff
displayInfo = pygame.display.Info()
w,h = displayInfo.current_w//2, displayInfo.current_h//2 # window is half of screen size
util.SetScreenDimensions(w,h)
screen = pygame.display.set_mode((w,h))
pygame.display.set_caption("Pygame") #title
#mainloop
clock = pygame.time.Clock()
util.setRenderer(Renderer(screen,{"ground":"Stone Texture.jpg"},{}))
renderer = util.getRenderer() 
sample = TypingAnimation("Hello world. Dolorem ipsum....", (100,100),"Arial",20,(0,0,0),4)
renderer.createSolidTexture("chest",(0,255,0),(50,50),4)
renderer.createSolidTexture("placeholder-item", (0,0,255),(50,50),1000)
sample_ground = entities.Ground(40,"ground")
sample_world = World(200,{})
player = Player(sample_world,sample_ground)
chestManager = entities.ChestManager(player,sample_ground,sample_world,"chest")
while 1:
    util.SetDeltaTime()
    renderer.setBackground((255,255,255),None)
    renderer.createAndRenderText("POSTEMP",str(player.x),"Arial",15,(0,0,0),(0,0),silence=True)
    sample_ground.renderGround(player)
    sample.doTypingAnimation()
    chestManager.generateAndRenderChest()
    player.move()  
    for event in pygame.event.get(): # basic quit on signal
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update() # update display