import pygame
from renderer import Renderer
from animations import SpriteAnimation,TypingAnimation
from player import Player
import renderer_manager
pygame.init()# init shit
#define screen stuff
displayInfo = pygame.display.Info()
w,h = displayInfo.current_w//2, displayInfo.current_h//2 # window is half of screen size
screen = pygame.display.set_mode((w,h))
pygame.display.set_caption("Pygame") #title
#mainloop
clock = pygame.time.Clock()
renderer_manager.setRenderer(Renderer(screen,{},{"test":("Hello, World!","Arial",24,(0,0,0))}))
renderer = renderer_manager.getRenderer()
dt = None
sample = TypingAnimation("Hello world. Dolorem ipsum....", (100,100),"Arial",20,(0,0,0),4)
player = Player(None)
while 1:
    dt = clock.tick(60)/1000  # cap at 60 fps
    renderer.setBackground((255,255,255),None)
    renderer.render(["test"],[(50,50)])
    sample.doTypingAnimation()
    player.move()
    dt = pygame.time.Clock().tick(60)/1000 
    for event in pygame.event.get(): # basic quit on signal
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update() # update display