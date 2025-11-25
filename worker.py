import pygame
from renderer import Renderer
pygame.init()# init shit
#define screen stuff
displayInfo = pygame.display.Info()
w,h = displayInfo.current_w//2, displayInfo.current_h//2 # window is half of screen size
screen = pygame.display.set_mode((w,h))
pygame.display.set_caption("Pygame") #title
#mainloop
clock = pygame.time.Clock()
renderer = Renderer({},{"test":("Hello, World!","Arial",24,(0,0,0))})
while 1:
    renderer.setBackground(screen,(255,255,255),None)
    renderer.render(screen,["test"],[(50,50)])
    dt = pygame.time.Clock().tick(60)/1000 
    for event in pygame.event.get(): # basic quit on signal
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update() # update display