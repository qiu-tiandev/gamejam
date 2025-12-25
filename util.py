import pygame
renderer = None
clock = pygame.time.Clock()
dt = None
w =0 
h = 0
itemID = {
    # --- General items (alphabetical) ---
    "alloy": 1,
    "battery": 2,
    "bones": 3,
    "charcoal": 4,
    "cooked monster flesh": 5,
    "cooked mysterious meat": 6,
    "cooker": 7,
    "dirt": 8,
    "feather": 9,
    "laser gun": 10,
    "liquid fuel": 11,
    "metal scrap": 12,
    "monster flesh": 13,
    "mysterious meat": 14,
    "mysterious powder": 15,
    "plastic scrap": 16,
    "screwdriver": 17,
    "stone": 18,
    "string": 19,
    "time machine": 20,
    "wood chips": 21,

    # --- Void (alphabetical) ---
    "Beacon": 22,
    "Magical Purple Screw": 23,
    "Purple Dust": 24,
    "Purple Fragment": 25,
    "Ruby": 26,

    # --- Limbo (alphabetical) ---
    "Ash": 27,
    "Calcium": 28,
    "Half-eaten Brain": 29,
    "Holy Book": 30,
    "Magical Eternal Screw": 31,
    "Pale Heart": 32,
    "Soul Fragment": 33,

    # --- Interstellar (alphabetical) ---
    "Chalk": 34,
    "Clock": 35,
    "Magical Stellar Screw": 36,
    "Space Fragment": 37,

    # --- Planet-Z (alphabetical) ---
    "Antenna": 38,
    "Bits": 39,
    "Keyboard": 40,
    "Magical Code Screw": 41,

    # --- #AWRZ-P (alphabetical) ---
    "Corrupted Fragment": 42,
    "Fluorite": 43,
    "Magical Arbitrary Screw": 44,

    # --- Blackhole (alphabetical) ---
    "Blackhole Fragment": 45,
    "Magical Dark-matter Screw": 46,
    "Mass": 47,
    "Sapphire": 48,

    # --- Whitehole (alphabetical) ---
    "Magical Anti-matter Screw": 49,
    "Quartz": 50,
    "Whitehole Fragment": 51,
}
itemID_reversed = {v:k for k,v in itemID.items()}

def setRenderer(Newrenderer):
    global renderer
    renderer = Newrenderer
def getRenderer():
    return renderer
def SetDeltaTime():
    global dt
    dt = clock.tick(9999999)/1000
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

def getItemDescription(name:str):
    return itemDescriptions.get(name, "")

# Item descriptions
itemDescriptions = {
    # --- General items ---
    "alloy": "A refined metal alloy",
    "battery": "Electrical energy source for time travelling, refilling gun",
    "bones": "Skeletal remains",
    "charcoal": "Main fuel source for cooking food",
    "cooked monster flesh": "Nutritious cooked meat",
    "cooked mysterious meat": "Cooked mysterious meat, safe to eat",
    "cooker": "Cooks raw food",
    "dirt": "Common soil",
    "feather": "Lightweight plumage",
    "laser gun": "Shoots concentrated beams of energy, dealing damage to enemies",
    "liquid fuel": "Combustible liquid energy source, subfuel for refilling gun",
    "metal scrap": "Broken metal pieces. Essential for crafting",
    "monster flesh": "Raw meat from monsters (Cannot eat)",
    "mysterious meat": "Raw mysterious meat (Cannot eat)",
    "mysterious powder": "Unknown magical substance",
    "plastic scrap": "Broken plastic pieces. Useful for crafting",
    "screwdriver": "Tool for fixing broken machinery",
    "stone": "Hard rock. Useful for crafting",
    "string": "Flexible cord, useful for crafting",
    "time machine": "Enables travel to other worlds",
    "wood chips": "Fragments of wood. Subfuel for cooking",

    # --- Void ---
    "Beacon": "Guides lost souls through darkness",
    "Magical Purple Screw": "Mystical component from the Void, essential for time travel",
    "Purple Dust": "Shimmering dust of the Void",
    "Purple Fragment": "Crystallized Void matter, useful for crafting",
    "Ruby": "A precious red gemstone",

    # --- Limbo ---
    "Ash": "Remains of forgotten things",
    "Calcium": "Mineral from ancient bones",
    "Half-eaten Brain": "Ewww...Attracts undead creatures",
    "Holy Book": "Contains sacred knowledge, increases max health",
    "Magical Eternal Screw": "Eternal component from Limbo, essential for time travel",
    "Pale Heart": "Heart of a lost soul",
    "Soul Fragment": "Essence of a departed spirit",

    # --- Interstellar ---
    "Chalk": "Writing tool from the stars",
    "Clock": "Time is key. Extends your survival time by 10%",
    "Magical Stellar Screw": "Cosmic component, essential for time tra  vel",
    "Space Fragment": "Matter from outer space",

    # --- Planet-Z ---
    "Antenna": "Allows you to shoot double lasers",
    "Bits": "Digital information fragments, useful for crafting",
    "Keyboard": "Increases attack",
    "Magical Code Screw": "Algorithmic component, essential for time travel",

    # --- #AWRZ-P ---
    "Corrupted Fragment": "Twisted matterm, useful for crafting",
    "Fluorite": "Fluorescent mineral",
    "Magical Arbitrary Screw": "Chaotic component, essential for time travel",

    # --- Blackhole ---
    "Blackhole Fragment": "Matter compressed infinitely, useful for crafting",
    "Magical Dark-matter Screw": "Component of hidden matter, essential for time travel",
    "Mass": "Pure gravitational force, useful for crafting",
    "Sapphire": "A precious blue gemstone",

    # --- Whitehole ---
    "Magical Anti-matter Screw": "Component of creation, essential for time travel",
    "Quartz": "Clear crystalline mineral",
    "Whitehole Fragment": "Matter bursting with energy, useful for crafting",
}

def getContrastColor(themeColor):
    r, g, b = themeColor[:3]
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    # Return white for dark backgrounds, black for light backgrounds
    return (255, 255, 255) if luminance < 0.5 else (0, 0, 0)