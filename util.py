import pygame
renderer = None
clock = pygame.time.Clock()
dt = None
w =0 
h = 0
def setRenderer(Newrenderer):
    global renderer
    renderer = Newrenderer
def getRenderer():
    return renderer
def SetDeltaTime():
    global dt
    dt = clock.tick(60)/1000
def getDeltaTime():
    return dt
def SetScreenDimensions(nw,nh):
    global w,h
    w,h = nw,nh
def getScreenDimensions():
    return w,h