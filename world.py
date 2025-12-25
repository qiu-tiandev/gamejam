import util
import pygame

WORLDS = [
    {"name": "Void", "theme_color": (129, 99, 180), "ground_id": "ground_void", "sky_id": "sky_void"},
    {"name": "Limbo", "theme_color": (184, 184, 184), "ground_id": "ground_limbo", "sky_id": "sky_limbo"},
    {"name": "Interstella", "theme_color": (255, 196, 209), "ground_id": "ground_interstella", "sky_id": "sky_interstella"},
    {"name": "Planet-Z", "theme_color": (115, 240, 198), "ground_id": "ground_planet_z", "sky_id": "sky_planet_z"},
    {"name": "#AWRZ-P", "theme_color": (0, 212, 89), "ground_id": "ground_awrz_p", "sky_id": "sky_awrz_p"},
    {"name": "Blackhole", "theme_color": (36, 2, 0), "ground_id": "ground_blackhole", "sky_id": "sky_blackhole"},
    {"name": "Whitehole", "theme_color": (255, 255, 255), "ground_id": "ground_whitehole", "sky_id": "sky_whitehole"},
]

def get_world_names():
    return [w["name"] for w in WORLDS]

def get_world_count():
    return len(WORLDS)

def get_world_data(index):
    return WORLDS[index % len(WORLDS)]

def load_world_textures(renderer, world_index):
    world = get_world_data(world_index)
    
    renderer.createImage(world["ground_id"], f"ground_{world_index + 1}.png")
    renderer.createImage(world["sky_id"], f"Sky{world_index + 1}.png")

def unload_world_textures(renderer, world_index):
    if world_index < 0:
        return
    world = get_world_data(world_index)
    
    if world["ground_id"] in renderer.Imagetextures:
        del renderer.Imagetextures[world["ground_id"]]
    if world["sky_id"] in renderer.Imagetextures:
        del renderer.Imagetextures[world["sky_id"]]

class World:
    def __init__(self, gravity, world_index: int = 0, chestLoot: dict = None, themeColor:tuple[int,int,int]=None, craftingRecipes: dict = None, placeableBlocks:list = None, cookingRecipes: dict = None):
        self.gravity = gravity
        self.world_index = world_index
        self.world_data = get_world_data(world_index)
        self.world_name = self.world_data["name"]
        
        self.themeColor = themeColor if themeColor is not None else self.world_data["theme_color"]
        
        self.ground_id = self.world_data["ground_id"]
        self.sky_id = self.world_data["sky_id"]
        world_key = self.world_name.lower().replace("-", "_").replace("#", "")
        self.items_id = f"items_{world_key}"
        
        if chestLoot is None:
            self.chestLoot = {}
        else:
            self.chestLoot = chestLoot
        self.craftingRecipes = {
                "battery": [("metal scrap", 2), ("liquid fuel", 1)],
                "cooker": [("stone", 5), ("string", 2),("wood chips", 3)],
                "screwdriver": [("metal scrap", 3), ("plastic scrap", 2)],
                "liquid fuel": [("charcoal", 2), ("metal scrap", 2)],
                "feather": [("string", 3)]
            }
        if craftingRecipes is not None:
            self.craftingRecipes.update(craftingRecipes)
        
        self.placeableBlocks = ["time machine", "cooker", "half-eaten brain", "beacon", "antenna"]
        if placeableBlocks is not None:
            self.placeableBlocks.extend(placeableBlocks)
        
        self.blockAssets = {
            "time machine": "time_machine.png",
            "cooker": "cooker_spritesheet",
            "half-eaten brain": "Brain.png",
            "beacon": "Beacon.png",
            "antenna": "Antenna.png",
        }
        
        self.blockProperties = {
            "time machine": {"height": 2, "states": ["default"], "solid": False},
            "cooker": {"height": 1, "states": ["idle", "cooking"], "solid": True},
            "half-eaten brain": {"height": 0.75, "states": ["active"], "solid": True},
            "beacon": {"height": 1, "states": ["active"], "solid": True},
            "antenna": {"height": 1, "states": ["active"], "solid": True},
        }
        
        self.cookingRecipes = {
            "fuels": ["charcoal","liquid fuel", "wood chips"],
            "recipes": {
                "charcoal": [(1, "wood chips", 1)],
                "cooked monster flesh": [(1, "monster flesh", 1)],
                "cooked mysterious meat": [(1, "mysterious meat", 1)]
            }
        }
        if cookingRecipes is not None:
            for i in cookingRecipes["recipes"]:
                if i in self.cookingRecipes["recipes"]:
                    self.cookingRecipes["recipes"][i].extend(cookingRecipes["recipes"][i])
                else:
                    self.cookingRecipes["recipes"][i] = cookingRecipes["recipes"][i]
        
        self.eatables = [
            "cooked monster flesh",
            "cooked mysterious meat",
        ]
    
    def getChestLoot(self):
        return self.chestLoot

class Sky:
    def __init__(self, id:str, groundh):
        self.id = id 
        self.renderer = util.getRenderer()
        self.groundh = groundh
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        original = self.renderer.getTexture(self.id)
        original_w, original_h = original.get_size()
        target_h = h - groundh
        scale_factor = target_h / original_h
        scaled_w = int(original_w * scale_factor)
        scaled_texture = pygame.transform.scale(original, (scaled_w, target_h))
        self.renderer.Imagetextures[self.id + "_scaled"] = scaled_texture
        self.scaled_id = self.id + "_scaled"
        self.scaled_w = scaled_w
        self.screen_w = w
        self._scaled_tex = scaled_texture
    def render(self, player_x):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.__init__(self.id, self.groundh)
        scroll_speed = 0.3
        offset_x = int(player_x * scroll_speed) % self.scaled_w
        if self.scaled_w > self.screen_w:
            crop_w = min(self.screen_w, self.scaled_w - offset_x)
            crop_rect = pygame.Rect(offset_x, 0, crop_w, self._scaled_tex.get_height())
            cropped = self._scaled_tex.subsurface(crop_rect)
            self.renderer.render_surface(cropped, (0, 0))
            if crop_w < self.screen_w:
                remaining = self.screen_w - crop_w
                wrap_rect = pygame.Rect(0, 0, remaining, crop_rect.height)
                wrapped = self._scaled_tex.subsurface(wrap_rect)
                self.renderer.render_surface(wrapped, (crop_w, 0))
        else:
            self.renderer.render([self.scaled_id], [(0, 0)])