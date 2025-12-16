import pygame
renderer = None
clock = pygame.time.Clock()
dt = None
w =0 
h = 0
itemID = {
    # --- General items (alphabetical) ---
    "battery": 0,
    "bones": 1,
    "charcoal": 2,
    "cooked monster flesh": 3,
    "cooker": 4,
    "dirt": 5,
    "feather": 6,
    "laser gun": 7,
    "liquid fuel": 8,
    "metal scrap": 9,
    "monster flesh": 10,
    "mysterious powder": 11,
    "plastic scrap": 12,
    "screw driver": 13,
    "stone": 14,
    "string": 15,
    "time machine": 16,
    "wood chips": 17,

    # --- Void ---
    "Purple Dust": 18,
    "Purple Fragment": 19,
    "Magical Purple Screw": 20,
    "Beacon": 21,
    "Ruby": 22,

    # --- Limbo ---
    "Ash": 23,
    "Soul Fragment": 24,
    "Magical Eternal Screw": 25,
    "Pale Heart": 26,
    "Half-eaten Brain": 27,
    "Holy Book": 28,
    "Calcium": 29,

    # --- Interstellar ---
    "Space Fragment": 30,
    "Magical Stellar Screw": 31,
    "Clock": 32,
    "Chalk": 33,

    # --- Planet-Z ---
    "Bits": 34,
    "Magical Code Screw": 35,
    "Keyboard": 36,
    "Antenna": 37,
    "Alloy": 38,

    # --- #AWRZ-P ---
    "Corrupted Fragment": 39,
    "Magical Arbitrary Screw": 40,
    "Fluorite": 41,

    # --- Blackhole ---
    "Blackhole Fragment": 42,
    "Magical Dark-matter Screw": 43,
    "Mass": 44,
    "Sapphire": 45,

    # --- Whitehole ---
    "Whitehole Fragment": 46,
    "Magical Anti-matter Screw": 47,
    "Quartz": 48,
}
itemID_reversed = {v:k for k,v in itemID.items()}

def setRenderer(Newrenderer):
    global renderer
    renderer = Newrenderer
def getRenderer():
    return renderer
def SetDeltaTime():
    global dt
    dt = clock.tick(120)/1000
def getDeltaTime():
    return dt
def SetScreenDimensions(nw,nh):
    global w,h
    w,h = nw,nh
def getScreenDimensions():
    return w,h
def getItemID(name:str):
    return itemID.get(name,-1)
def getItemName(id:int):
    return itemID_reversed.get(id,"unknown item")
sampleChestLoot = {
    "bones": (1, 3),
    "metal scrap": (2, 5),
    "string": (1, 2),
    "stone": (3, 6),
}