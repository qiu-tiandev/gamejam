import pygame
from renderer import Renderer
from animations import SpriteAnimation
from player import Player
import util
import console
import entities
from world import World, Sky, load_world_textures, unload_world_textures, get_world_data, get_world_count, WORLDS
from core_mechanics import InventoryManager, CraftingManager, BlockManager, CookerManager
from tutorial import TutorialManager
import psutil
import os
import sys
import random
pygame.init()
pygame.mixer.init()
displayInfo = pygame.display.Info()
w,h = displayInfo.current_w//2, displayInfo.current_h//2
util.SetScreenDimensions(w,h)
screen = pygame.display.set_mode((w,h), pygame.RESIZABLE | pygame.DOUBLEBUF)
pygame.display.set_caption("KCIT")
clock = pygame.time.Clock()
util.setRenderer(Renderer(screen, {"chest": "Chest.png", "ground": "ground_1.png", "sky1": "Sky1.png", "general_items": "general_items.png", "cooker_spritesheet": "cooker.png", "time_machine_block": "time_machine.png", "player_spritesheet": "player.png"}, {"crafting_title": ("Crafting", "arial", 24, (255, 255, 255))}))
renderer = util.getRenderer()

renderer.createImage("gui_spritesheet", "gui.png")
renderer.createImage("hotbar_spritesheet", "hotbar.png")
renderer.createImage("button_spritesheet", "button.png")
gui_sprite = SpriteAnimation("gui_spritesheet", (256, 177), 7)
gui_sprite.save_frames("gui")
hotbar_sprite = SpriteAnimation("hotbar_spritesheet", (24, 24), 14)
hotbar_sprite.save_frames("hotbar")
button_sprite = SpriteAnimation("button_spritesheet", (32, 32), 7)
button_sprite.save_frames("button")

renderer.cleanUp(["gui_spritesheet", "hotbar_spritesheet", "button_spritesheet"])

renderer.ResizeTexture("chest",[50,50],True,True)
renderer.createSolidTexture("placeholder-item", (0,0,255),(50,50),1000)

try:
    renderer.createImage("zombie_spritesheet", "zombie.png")
    zombie_sprite = SpriteAnimation("zombie_spritesheet", (16, 29), 2)
    zombie_sprite.save_frames("zombie")
    renderer.cleanUp(["zombie_spritesheet"])
except Exception as e:
    console.sendError(f"Failed to load zombie spritesheet. {e}", __file__)

cooker_sprite = SpriteAnimation("cooker_spritesheet", (24, 24), 2)
cooker_sprite.save_frames("block_cooker")  # Creates block_cooker_001 (idle) and block_cooker_002 (cooking)

renderer.cleanUp(["cooker_spritesheet"])

try:
    renderer.createImage("block_time_machine", "time_machine.png",(32,64))
except Exception as e:
    console.sendError(f"Failed to load time machine block texture. {e}", __file__)

try:
    renderer.createImage("brain_block", "Brain.png")
except Exception as e:
    console.sendError(f"Failed to load brain block texture. {e}", __file__)

try:
    renderer.createImage("beacon_block", "Beacon.png")
    renderer.createImage("antenna_block", "Antenna.png")
except Exception as e:
    console.sendError(f"Failed to load beacon block texture. {e}", __file__)

try:
    globe_size = int(min(w, h) * 0.15)
    spaceship_size = int(min(w, h) * 0.15)
    renderer.createImage("black_sky", "black_sky.png", (w, h))
    renderer.createImage("globe", "globe.png", (globe_size, globe_size))
    renderer.createImage("spaceship", "spaceship.png", (spaceship_size, spaceship_size))
except Exception as e:
    console.sendError(f"Failed to load intro sequence images. {e}", __file__)

def render_intro_sequence():
    global intro_active, intro_start_time, intro_zoom_triggered, intro_zoom_start_time, intro_message_shown, intro_message_start_time, intro_explosion_played
    
    if not intro_active:
        return
    
    current_w, current_h = pygame.display.get_surface().get_size()
    
    elapsed = pygame.time.get_ticks() - intro_start_time
    duration = 5000
    zoom_duration = 1500
    
    globe_size = int(min(current_w, current_h) * 0.15)
    spaceship_size = int(min(current_w, current_h) * 0.10)
    
    black_sky = renderer.getTexture("black_sky")
    if black_sky and (black_sky.get_width() != current_w or black_sky.get_height() != current_h):
        renderer.createImage("black_sky", "black_sky.png", (current_w, current_h))
    
    globe_tex = renderer.getTexture("globe")
    if globe_tex and (globe_tex.get_width() != globe_size or globe_tex.get_height() != globe_size):
        renderer.createImage("globe", "globe.png", (globe_size, globe_size))
    
    spaceship_tex = renderer.getTexture("spaceship")
    if spaceship_tex and (spaceship_tex.get_width() != spaceship_size or spaceship_tex.get_height() != spaceship_size):
        renderer.createImage("spaceship", "spaceship.png", (spaceship_size, spaceship_size))
    
    black_sky = renderer.getTexture("black_sky")
    if black_sky:
        renderer.render_surface(black_sky, (0, 0))
    
    globe_x = current_w * 0.8
    globe_y = current_h * 0.3
    
    start_x = current_w * 0.1
    end_x = globe_x - 80
    progress = min(1.0, elapsed / duration)
    
    if progress >= 0.6 and not intro_message_shown:
        intro_message_shown = True
        intro_message_start_time = pygame.time.get_ticks()
    
    # Calculate eased progress based on message timing
    if not intro_message_shown:
        # Slow constant speed until message appears (0% to 60%)
        eased_progress = progress * 0.3  # Move 30% of distance slowly
    else:
        # After message appears, wait 0.5s then dramatically accelerate
        time_since_message = pygame.time.get_ticks() - intro_message_start_time
        if time_since_message < 500:
            # Hold position for 0.5 seconds after message
            eased_progress = 0.6 * 0.3
        else:
            # Dramatic acceleration after 0.5s
            accel_progress = (progress - 0.6) / 0.4  # Remaining 40% of time
            eased_progress = 0.3 + 0.7 * (accel_progress ** 3)  # Cubic acceleration
    
    spaceship_x = start_x + (end_x - start_x) * eased_progress
    spaceship_y = current_h * 0.3
    
    globe = renderer.getTexture("globe")
    if globe:
        renderer.render_surface(globe, (int(globe_x), int(globe_y)))
    
    spaceship = renderer.getTexture("spaceship")
    if spaceship:
        renderer.render_surface(spaceship, (int(spaceship_x), int(spaceship_y)))
    
    if progress >= 0.95 and not intro_explosion_played:
        intro_explosion_played = True
        try:
            explosion_sound = pygame.mixer.Sound("assets/explosion.mp3")
            explosion_sound.play()
        except:
            console.sendInfo("Could not load explosion.mp3", __file__)
    
    if progress >= 1.0 and not intro_zoom_triggered:
        intro_zoom_triggered = True
        intro_zoom_start_time = pygame.time.get_ticks()
    
    if intro_zoom_triggered:
        zoom_elapsed = pygame.time.get_ticks() - intro_zoom_start_time
        zoom_progress = min(1.0, zoom_elapsed / zoom_duration)
        
        zoom_surface = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        zoom_alpha = int(255 * zoom_progress)
        zoom_surface.fill((0, 0, 0, zoom_alpha))
        renderer.render_surface(zoom_surface, (0, 0))
        
        if zoom_progress >= 1.0:
            intro_active = False
            intro_zoom_triggered = False
    
    if intro_message_shown:
        # Blinking effect - toggle every 400ms
        blink_interval = 400
        message_elapsed = pygame.time.get_ticks() - intro_message_start_time
        should_show = (message_elapsed // blink_interval) % 2 == 0
        
        if should_show:
            message = "Lost control. Entering the future"
            font = pygame.font.SysFont("Arial", 32)
            text_width = font.size(message)[0]
            renderer.createAndRenderText(
                "intro_message", message, "Arial", 32, (255, 0, 0),
                ((current_w - text_width) // 2, 50), cache=False, silence=True
            )
    
    # Keep the loop going with slight delay
    pygame.display.flip()
    pygame.time.wait(16)

def render_start_screen():
    current_w, current_h = pygame.display.get_surface().get_size()
    
    black_sky = renderer.getTexture("black_sky")
    if black_sky and (black_sky.get_width() != current_w or black_sky.get_height() != current_h):
        renderer.createImage("black_sky", "black_sky.png", (current_w, current_h))
    
    # Render black sky background
    if black_sky:
        renderer.render_surface(black_sky, (0, 0))
    
    # Render game title - centered horizontally, top third of screen
    title_text = "KCIT"
    title_font_size = 48
    title_font = pygame.font.SysFont("Arial", title_font_size)
    title_width = title_font.size(title_text)[0]
    title_x = (current_w - title_width) // 2
    title_y = current_h // 3
    
    renderer.createAndRenderText(
        "game_title", title_text, "Arial", title_font_size, (255, 255, 255),
        (title_x, title_y), cache=False, silence=True
    )
    
    # Render "Press anywhere to continue" - centered horizontally, bottom third of screen
    continue_text = "Press anywhere to continue"
    continue_font_size = 24
    continue_font = pygame.font.SysFont("Arial", continue_font_size)
    continue_width = continue_font.size(continue_text)[0]
    continue_x = (current_w - continue_width) // 2
    continue_y = current_h * 2 // 3
    
    renderer.createAndRenderText(
        "continue_text", continue_text, "Arial", continue_font_size, (200, 200, 200),
        (continue_x, continue_y), cache=False, silence=True
    )
    
    pygame.display.flip()
    pygame.time.wait(16)

current_world_index = 0
load_world_textures(renderer, current_world_index)

def create_world_entities(world_index):
    world_data = get_world_data(world_index)
    
    # Define recipes per world
    world_recipes = {
        0: {  # Void
            "Beacon": [("metal scrap", 3), ("plastic scrap", 2), ("liquid fuel", 1), ("mysterious powder", 1)],
            "Magical Purple Screw": [("Purple Fragment", 5)],
            "Purple Fragment": [("mysterious powder", 5), ("Ruby", 2)],
            "Ruby": [("metal scrap",5),("mysterious powder",2)],
            "time machine": [("Magical Purple Screw", 2), ("metal scrap", 5), ("Purple Fragment", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        },
        1: {  # Limbo
            "Calcium": [("bones", 5)],
            "Holy Book": [("mysterious powder", 1), ("string", 2), ("feather", 2), ("Ash",3)],
            "Magical Eternal Screw": [("Soul Fragment", 5)],
            "Soul Fragment": [("mysterious powder", 5), ("Calcium", 2)],
            "time machine": [("Magical Eternal Screw", 2), ("metal scrap", 5), ("Soul Fragment", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        },
        2: {  # Interstellar
            "Clock": [("plastic scrap", 2), ("metal scrap", 2), ("mysterious powder", 1), ("battery", 2)],
            "Magical Stellar Screw": [("Space Fragment", 5)],
            "Space Fragment": [("mysterious powder", 5), ("Chalk", 2)],
            "time machine": [("Magical Stellar Screw", 2), ("metal scrap", 5), ("Space Fragment", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        },
        3: {  # Planet-Z
            "Antenna": [("alloy", 2), ("metal scrap", 1)],
            "Bits": [("mysterious powder", 5), ("alloy", 2)],
            "Keyboard": [("plastic scrap", 2)],
            "Magical Code Screw": [("Bits", 5)],
            "time machine": [("Magical Code Screw", 2), ("metal scrap", 5), ("Bits", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        },
        4: {  # #AWRZ-P
            "Corrupted Fragment": [("mysterious powder", 5), ("Fluorite", 2)],
            "Fluorite": [("Calcium", 3), ("mysterious powder", 1)],
            "Magical Arbitrary Screw": [("Corrupted Fragment", 5)],
            "time machine": [("Magical Arbitrary Screw", 2), ("metal scrap", 5), ("Corrupted Fragment", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        },
        5: {  # Blackhole
            "Blackhole Fragment": [("mysterious powder", 5), ("Sapphire", 2)],
            "Magical Dark-matter Screw": [("Blackhole Fragment", 5)],
            "Mass": [("mysterious powder", 3)],
            "time machine": [("Magical Dark-matter Screw", 2), ("metal scrap", 5), ("Blackhole Fragment", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        },
        6: {  # Whitehole
            "Magical Anti-matter Screw": [("Whitehole Fragment", 5)],
            "Quartz": [("Chalk", 3), ("mysterious powder", 1)],
            "Whitehole Fragment": [("mysterious powder", 5), ("Quartz", 2)],
            "time machine": [("Magical Anti-matter Screw", 2), ("metal scrap", 5), ("Whitehole Fragment", 2), ("mysterious powder", 5), ("battery", 10), ("screwdriver", 1)]
        }
    }
    
    # Restricted items (fragments and screws) per world - these don't carry over
    restricted_items = {
        0: ["Magical Purple Screw", "Purple Fragment", "time machine"],
        1: ["Magical Eternal Screw", "Soul Fragment", "time machine"],
        2: ["Magical Stellar Screw", "Space Fragment", "time machine"],
        3: ["Magical Code Screw", "Bits", "time machine"],
        4: ["Magical Arbitrary Screw", "Corrupted Fragment", "time machine"],
        5: ["Magical Dark-matter Screw", "Blackhole Fragment", "time machine"],
        6: ["Magical Anti-matter Screw", "Whitehole Fragment", "time machine"]
    }
    
    # Build cumulative recipes, but exclude restricted items from previous worlds
    world_crafting_recipes = {}
    for w_idx in range(world_index + 1):
        for item, recipe in world_recipes[w_idx].items():
            if w_idx < world_index and item in restricted_items.get(w_idx, []):
                continue  # Skip restricted items from previous worlds
            world_crafting_recipes[item] = recipe
    
    # World-specific cooking recipes (smelting)
    world_cooking_recipes = {"recipes": {}}
    if world_index >= 1:  # Limbo
        world_cooking_recipes["recipes"].update({
            "Chalk": [(1, "Calcium", 1)],
            "Ash": [(1,"bones",1)]
        })
    if world_index >= 3:  # Planet-Z
        world_cooking_recipes["recipes"]["Sapphire"] = [(1, "Chalk", 1)]
    
    # World-specific chest loot tables
    world_loot_tables = {
        0: {  # Void
            "Beacon": {"min": 1, "max": 1, "rarity": "Rare"},
            "Purple Dust": {"min": 1, "max": 2, "rarity": "Common"},
            "Purple Fragment": {"min": 1, "max": 2, "rarity": "Rare"},
            "Ruby": {"min": 1, "max": 2, "rarity": "Uncommon"}
        },
        1: {  # Limbo
            "Ash": {"min": 1, "max": 3, "rarity": "Common"},
            "Calcium": {"min": 1, "max": 2, "rarity": "Uncommon"},
            "Half-eaten Brain": {"min": 1, "max": 1, "rarity": "Rare"},
            "Holy Book": {"min": 1, "max": 1, "rarity": "Rare"},
            "Pale Heart": {"min": 1, "max": 1, "rarity": "Uncommon"},
            "Soul Fragment": {"min": 1, "max": 2, "rarity": "Rare"}
        },
        2: {  # Interstellar
            "Chalk": {"min": 0, "max": 1, "rarity": "Uncommon"},
            "Clock": {"min": 1, "max": 1, "rarity": "Rare"},
            "Space Fragment": {"min": 1, "max": 2, "rarity": "Rare"}
        },
        3: {  # Planet-Z
            "Antenna": {"min": 1, "max": 1, "rarity": "Rare"},
            "Bits": {"min": 1, "max": 2, "rarity": "Rare"},
            "Keyboard": {"min": 1, "max": 1, "rarity": "Rare"}
        },
        4: {  # #AWRZ-P
            "Corrupted Fragment": {"min": 1, "max": 2, "rarity": "Rare"},
            "Fluorite": {"min": 1, "max": 1, "rarity": "Uncommon"}
        },
        5: {  # Blackhole
            "Blackhole Fragment": {"min": 1, "max": 1, "rarity": "Rare"},
            "Mass": {"min": 1, "max": 3, "rarity": "Uncommon"},
            "Sapphire": {"min": 1, "max": 1, "rarity": "Uncommon"}
        },
        6: {  # Whitehole
            "Quartz": {"min": 1, "max": 1, "rarity": "Uncommon"},
            "Whitehole Fragment": {"min": 1, "max": 1, "rarity": "Rare"}
        }
    }
    
    # Get the loot table for this world (start with general items)
    general_loot = {
        "alloy": {"min": 1, "max": 2, "rarity": "Rare"},
        "battery": {"min": 1, "max": 2, "rarity": "Uncommon"},
        "bones": {"min": 1, "max": 2, "rarity": "Uncommon"},
        "charcoal": {"min": 1, "max": 2, "rarity": "Uncommon"},
        "cooker": {"min": 1, "max": 1, "rarity": "Rare"},
        "dirt": {"min": 0, "max": 2, "rarity": "Common"},
        "feather": {"min": 0, "max": 2, "rarity": "Common"},
        "liquid fuel": {"min": 1, "max": 6, "rarity": "Uncommon"},
        "metal scrap": {"min": 1, "max": 3, "rarity": "Common"},
        "monster flesh": {"min": 1, "max": 3, "rarity": "Uncommon"},
        "mysterious meat": {"min": 1, "max": 2, "rarity": "Rare"},
        "mysterious powder": {"min": 1, "max": 5, "rarity": "Uncommon"},
        "plastic scrap": {"min": 1, "max": 2, "rarity": "Common"},
        "stone": {"min": 0, "max": 3, "rarity": "Common"},
        "string": {"min": 0, "max": 2, "rarity": "Common"},
        "wood chips": {"min": 1, "max": 4, "rarity": "Common"}
    }
    
    # Get world-specific loot and merge with general loot
    world_specific_loot = world_loot_tables.get(world_index, {})
    world_chest_loot = general_loot.copy()
    world_chest_loot.update(world_specific_loot)
    
    ground = entities.Ground(70, world_data["ground_id"])
    sky = Sky(world_data["sky_id"], ground.height)
    world = World(200, world_index=world_index, chestLoot=world_chest_loot, craftingRecipes=world_crafting_recipes, cookingRecipes=world_cooking_recipes)
    
    return ground, sky, world

def initialize_managers(world, ground, player, inventory):
    item_manager = entities.ItemEntityManager(player, inventory, ground)
    craft_manager = CraftingManager(world, inventory)
    block_manager = BlockManager(world, ground, inventory, player)
    player.block_manager = block_manager
    chest_manager = entities.ChestManager(player, ground, world, "chest", item_manager)
    monster_manager = entities.MonsterManager(player, ground, block_manager, itemManager=item_manager, world=world)
    cooker_manager = CookerManager(world, inventory, player, ground, block_manager)
    beacon_manager = entities.BeaconManager(player, ground, block_manager, monster_manager)
    
    return item_manager, craft_manager, block_manager, chest_manager, monster_manager, cooker_manager, beacon_manager

def do_fade_transition(fade_out=True, duration_ms=500):
    steps = 30
    step_duration = duration_ms // steps
    current_dims = util.getScreenDimensions()
    
    for i in range(steps + 1):
        alpha = int((i / steps) * 255) if fade_out else int((1 - i / steps) * 255)
        fade_surface = pygame.Surface(current_dims, pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, alpha))
        renderer.render_surface(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(step_duration)
        
        # Process events during fade to prevent freezing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def render_unlock_screen():
    if not unlocked_items:
        return
    
    screen_w, screen_h = w, h
    
    num_items = len(unlocked_items)
    item_size = 40
    item_spacing = 50
    gui_padding = 20
    
    total_items_width = num_items * item_spacing
    gui_width = max(200, total_items_width + gui_padding * 2)
    gui_height = 120
    
    gui_x = (screen_w - gui_width) // 2
    gui_y = 50
    
    gui_texture = renderer.getTexture(f"gui_{current_world.world_index + 1:03d}")
    if gui_texture:
        scaled_gui = pygame.transform.scale(gui_texture, (gui_width, gui_height))
        renderer.screen.blit(scaled_gui, (gui_x, gui_y))
    
    text_color = util.getContrastColor(current_world.themeColor)
    renderer.createAndRenderText(
        "unlock_title", "You Unlocked:", "Arial", 20, text_color,
        (gui_x + gui_width // 2 - 60, gui_y + 15), cache=False, silence=True
    )
    
    start_x = gui_x + gui_padding + (gui_width - gui_padding * 2 - total_items_width) // 2 + item_size // 2
    
    for i, item_id in enumerate(unlocked_items):
        icon_id = f"items_{item_id:03d}"
        icon_x = start_x + i * item_spacing
        icon_y = gui_y + gui_height // 2
        
        surf = renderer.ResizeTexture(icon_id, [item_size, item_size], False, save=False)
        if surf:
            renderer.render([surf], [(icon_x - item_size // 2, icon_y - item_size // 2)])

def render_death_screen():
    global death_respawn_button_rect
    
    # Get screen dimensions
    screen_w, screen_h = w, h
    
    # Draw semi-transparent overlay using direct surface rendering instead of texture
    overlay_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, death_screen_fade_alpha))
    renderer.render_surface(overlay_surface, (0, 0))
    
    # Calculate GUI dimensions
    gui_width = 400
    gui_height = 250
    gui_x = (screen_w - gui_width) // 2
    gui_y = (screen_h - gui_height) // 2
    
    # Render GUI background
    gui_texture = renderer.getTexture(f"gui_{current_world.world_index + 1:03d}")
    if gui_texture:
        scaled_gui = pygame.transform.scale(gui_texture, (gui_width, gui_height))
        renderer.screen.blit(scaled_gui, (gui_x, gui_y))
    
    # Render "You died" text
    text_color = util.getContrastColor(current_world.themeColor)
    renderer.createAndRenderText(
        "death_title", "You died", "Arial", 28, text_color,
        (gui_x + gui_width // 2 - 60, gui_y + 20), cache=False, silence=True
    )
    
    # Render the long text - split into two lines and center properly
    death_text1 = "Womp womp, but lucky you,"
    death_text2 = "you will respawn in the"
    death_text3 = "same time period as you passed"
    
    font_small = pygame.font.SysFont("Arial", 14)
    text1_width = font_small.size(death_text1)[0]
    text2_width = font_small.size(death_text2)[0]
    text3_width = font_small.size(death_text3)[0]
    
    # Center each line within the GUI
    renderer.createAndRenderText(
        "death_text1", death_text1, "Arial", 14, text_color,
        (gui_x + (gui_width - text1_width) // 2, gui_y + 70), cache=False, silence=True
    )
    renderer.createAndRenderText(
        "death_text2", death_text2, "Arial", 14, text_color,
        (gui_x + (gui_width - text2_width) // 2, gui_y + 90), cache=False, silence=True
    )
    renderer.createAndRenderText(
        "death_text3", death_text3, "Arial", 14, text_color,
        (gui_x + (gui_width - text3_width) // 2, gui_y + 110), cache=False, silence=True
    )
    
    # Render Respawn button
    button_width = 100
    button_height = 30
    button_x = gui_x + (gui_width - button_width) // 2
    button_y = gui_y + gui_height - 50
    death_respawn_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Get button sprite
    button_sprite_id = f"button_{current_world.world_index + 1:03d}"
    button_tex = renderer.getTexture(button_sprite_id)
    if button_tex:
        scaled_button = pygame.transform.scale(button_tex, (button_width, button_height))
        renderer.screen.blit(scaled_button, (button_x, button_y))
    
    # Render "Respawn" text on button
    font = pygame.font.SysFont("arial", 16)
    text_width = font.size("Respawn")[0]
    text_x = button_x + (button_width - text_width) // 2
    text_y = button_y + (button_height - 16) // 2
    renderer.createAndRenderText(
        "respawn_button_text", "Respawn", "Arial", 16, text_color,
        (text_x, text_y), cache=False, silence=True
    )

def render_win_screen():
    
    # Get screen dimensions
    screen_w, screen_h = w, h
    
    # Draw plain black background
    black_surface = pygame.Surface((screen_w, screen_h))
    black_surface.fill((0, 0, 0))
    renderer.render_surface(black_surface, (0, 0))
    
    # Render "Congrats! you win" text centered
    win_text = "Congrats! you win"
    text_color = (255, 255, 255)
    font = pygame.font.SysFont("Arial", 48)
    text_width = font.size(win_text)[0]
    renderer.createAndRenderText(
        "win_title", win_text, "Arial", 48, text_color,
        (screen_w // 2 - text_width // 2, screen_h // 2 - 24), cache=False, silence=True
    )

# Initialize first world (Void)
ground, sky, current_world = create_world_entities(current_world_index)
player = Player(current_world, ground)
inventory = InventoryManager("hotbar1", current_world)

# Initialize managers
itemManager, craftManager, blockManager, chestManager, monsterManager, cookerManager, beaconManager = initialize_managers(
    current_world, ground, player, inventory
)

console.sendInfo("Loading item spritesheets...", __file__)
item_offset = 22
general_sprite = SpriteAnimation("general_items", (32, 32), 21)
general_sprite.save_frames("items", start=1)
world_item_configs = [
    ("void_items.png", 5),
    ("limbo_items.png", 7),
    ("interstella_items.png", 4),
    ("planet_z_items.png", 4),
    ("awrz_p_items.png", 3),
    ("blackhole_items.png", 4),
    ("whitehole_items.png", 3),
]
for n,i in world_item_configs:
    renderer.createImage(n.split(".")[0], n)
    sprite = SpriteAnimation(n.split(".")[0], (32, 32), i)
    sprite.save_frames("items", start=item_offset)
    item_offset += i
console.sendInfo("Initialization complete.", __file__)
proc = psutil.Process(os.getpid())

inventory.addItem(util.getItemID("laser gun"), 1)
inventory.addItem(util.getItemID("cooked monster flesh"), 4)
inventory.addItem(util.getItemID("battery"), 3)
inventory.addItem(util.getItemID("liquid fuel"), 3)
is_focused = True
is_paused = False
time_machine_used = False
grace_period_active = False
grace_period_end_time = 0
GRACE_PERIOD_DURATION = 2000

damage_tint_alpha = 0
damage_tint_max_alpha = 60
damage_tint_duration = 300
damage_tint_start_time = 0
last_health = player.health

unlock_screen_active = False
unlock_screen_start_time = 0
unlock_screen_duration = 5000
unlocked_items = []

death_screen_active = False
death_screen_fade_alpha = 0
death_respawn_button_rect = None

win_screen_active = False
win_screen_fade_alpha = 0

antenna_boost_active = False
antenna_toggle_cooldown = 0

intro_active = True
start_screen_active = True
intro_start_time = 0
try:
    pygame.mixer.music.load("assets/start.mp3")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except:
    console.sendInfo("Could not load start.mp3", __file__)
intro_zoom_triggered = False
intro_zoom_start_time = 0
intro_message_shown = False
intro_explosion_played = False

# Define items unlocked per world
WORLD_UNLOCKS = {
    0: [],  # Void - no unlocks (starting world)
    1: [27, 28, 29, 30, 31, 32, 33],  # Limbo unlocks Void items
    2: [34, 35, 36, 37],  # Interstella unlocks Limbo items
    3: [38, 39, 40, 41],  # Planet-Z unlocks Interstella items
    4: [42, 43, 44],  # #AWRZ-P unlocks Planet-Z items
    5: [45, 46, 47, 48],  # Blackhole unlocks #AWRZ-P items
    6: [49, 50, 51],  # Whitehole unlocks Blackhole items
    7: []  # Completion unlocks Whitehole items
}

# Initialize tutorial
tutorialManager = TutorialManager(renderer, current_world, craftManager, player, chestManager, cookerManager, inventory)

# Run intro sequence before main game loop
while intro_active:
    if start_screen_active:
        render_start_screen()
    else:
        render_intro_sequence()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_screen_active:
                # Transition from start screen to spaceship animation
                start_screen_active = False
                pygame.mixer.music.stop()
                intro_start_time = pygame.time.get_ticks()
            else:
                # Skip intro on any input during spaceship animation
                intro_active = False

while not time_machine_used:
    if not is_focused: # prevent fps drops when not in focus 
        pygame.time.wait(100)
        util.SetDeltaTime()  # Still update delta time to prevent accumulation
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.ACTIVEEVENT:
                if event.gain == 1:  
                    is_focused = True
        continue
    
    util.SetDeltaTime()
    if antenna_toggle_cooldown > 0:
        antenna_toggle_cooldown -= util.getDeltaTime()
    current_w, current_h = pygame.display.get_surface().get_size()
    if current_w != w or current_h != h:
        w, h = current_w, current_h
        util.SetScreenDimensions(w, h)
        craftManager.screen_w = w
        craftManager.screen_h = h
        renderer.createSolidTexture(craftManager.overlay_id, (0, 0, 0, 180), (w, h), 4, cache=True)
        sky = Sky(current_world.sky_id, ground.height)
        player.y = h - ground.height - 50
        inventory.updateSlotSize()
        chestManager.updateGroundY()
        itemManager.updateGroundY()
        monsterManager.updateGroundY()
        itemManager.spawnRandomItems()
    
    # Check if grace period has ended
    if grace_period_active and pygame.time.get_ticks() >= grace_period_end_time:
        grace_period_active = False
        player.last_food_time = pygame.time.get_ticks() // 1000  # Reset hunger timer after grace period
    
    if not is_paused:  # Only update game logic when not paused
        renderer.setBackground((255,255,255),None)
        sky.render(player.x)
        text_color = util.getContrastColor(current_world.themeColor)
        
        # display current world
        world_text = f"World: {current_world.world_name}"
        renderer.createAndRenderText("world_display", world_text, "Arial", 14, text_color, (w//2 - 60, 5), cache=False, silence=True)
        
        ground.renderGround(player)
        
        # Only update game elements if tutorial is not active
        if not tutorialManager.is_active and not death_screen_active:
            chestManager.generateAndRenderChest()
            itemManager.pickUpItems()
        
        itemManager.RenderItemEntities()
        
        # Only update player lasers if tutorial is not active
        if not tutorialManager.is_active and not death_screen_active:
            player.updateLasers(util.getDeltaTime(), is_paused)
        
        # Update and render beacons (only if tutorial is not active)
        if not tutorialManager.is_active and not death_screen_active:
            beaconManager.update(util.getDeltaTime(), is_paused)
        
        # Check laser-monster collisions (only if not in grace period and not paused and not in tutorial)
        if not grace_period_active and not is_paused and not tutorialManager.is_active and not death_screen_active:
            lasers_hit = monsterManager.checkLaserCollision(player.active_lasers)
            for idx in reversed(lasers_hit):
                player.active_lasers.pop(idx)
            # Check beacon laser collisions
            beaconManager.check_laser_collisions()
        
        inventory.updateDirection(pygame.key.get_pressed())
        
        # Only allow player movement if tutorial is not active
        if not tutorialManager.is_active and not death_screen_active:
            player.move(is_paused)
        else:
            # Still update animation but don't move
            player._update_animation()
        
        player.renderLasers()
        beaconManager.render_lasers()  # Render beacon lasers after player lasers
        
        # Render world elements in order: blocks, monsters, player
        blockManager.render_blocks()
        monsterManager.renderMonsters()  # Monsters before player
        player.render()  # Player after monsters
        
        # Render UI elements: inventory, held item, health bars
        inventory.renderInventory()
        # Render held item description only when not in tutorial
        if not tutorialManager.is_active:
            inventory.renderHeldItem(player)
        
        renderer.createAndRenderText("OBJECTIVE", "Objective: Get time machine to progress", "Arial", 16, text_color, (10, 0), cache=False, silence=True)
    
    # Update health/hunger ALWAYS (not just when not paused) so pause tracking works (not in tutorial)
    if not grace_period_active and not tutorialManager.is_active and not death_screen_active:
        player.update_health(is_paused)
        player.update_hunger(is_paused)
    
    # Check for player death
    if player.health <= 0 and not death_screen_active:
        death_screen_active = True
        death_screen_fade_alpha = 0
    
    # Detect damage and trigger damage tint
    if player.health < last_health:
        damage_tint_alpha = damage_tint_max_alpha
        damage_tint_start_time = pygame.time.get_ticks()
    last_health = player.health
    
    # Update damage tint alpha smoothly
    if damage_tint_alpha > 0:
        elapsed = pygame.time.get_ticks() - damage_tint_start_time
        progress = min(1.0, elapsed / damage_tint_duration)
        damage_tint_alpha = int(damage_tint_max_alpha * (1.0 - progress))
    
    # Render damage tint vignette (red edges)
    if damage_tint_alpha > 0:
        # Create uniform red tint that extends to screen edges
        vignette_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Fill entire screen with red tint
        vignette_surface.fill((255, 0, 0, damage_tint_alpha))
        
        renderer.render_surface(vignette_surface, (0, 0))
    
    # Render health/hunger bars ALWAYS (except when tutorial is showing them)
    if not (tutorialManager.is_active and tutorialManager.current_paragraph == 7):
        player.render_healthbar()
        player.render_hunger_bar()
    itemManager.spawnRandomItems()
    # Render GUI elements last
    cookerManager.render()
    craftManager.render()
    
    # Update and render tutorial (renders on top of everything)
    tutorialManager.update()
    tutorialManager.render()
    
    # Render unlock screen (shows unlocked items after world progression)
    if unlock_screen_active:
        elapsed = pygame.time.get_ticks() - unlock_screen_start_time
        if elapsed < unlock_screen_duration:
            render_unlock_screen()
        else:
            unlock_screen_active = False
            unlocked_items = []
    
    # Render death screen
    if death_screen_active:
        death_screen_fade_alpha = min(255, death_screen_fade_alpha + 5)
        render_death_screen()
    
    # Reset health and hunger after tutorial ends
    if tutorialManager.is_active == False and not grace_period_active:
        # Check if tutorial just ended by seeing if it was active in previous frame
        if not hasattr(tutorialManager, '_was_active'):
            tutorialManager._was_active = True
        if tutorialManager._was_active and tutorialManager.is_active == False:
            player.health = 100
            player.hunger_timer = player.max_hunger_time
            player.last_food_time = pygame.time.get_ticks() / 1000
            tutorialManager._was_active = False
    keys = pygame.key.get_pressed()
    # Antenna toggle is now handled in the S key event handler when near antenna
    # R key is handled in KEYDOWN events for keyboard/clock/holy book
    
    # Keybind guide system - determine which guide to show (priority order)
    keybind_guide = None
    
    # Check if near a chest
    for chest_x in chestManager.chests.values():
        if player.x + 60 > chest_x and player.x < chest_x + 60:
            keybind_guide = "Press S to loot chest"
            break
    
    # Check if near a time machine (priority over cooker)
    if keybind_guide is None:
        nearby_time_machine = blockManager.get_nearby_time_machine()
        if nearby_time_machine:
            if nearby_time_machine.get("state") == "broken":
                # Check if player has screwdriver
                screwdriver_id = util.getItemID("screwdriver")
                if screwdriver_id >= 0 and inventory.items.get(screwdriver_id, 0) > 0:
                    keybind_guide = "Press R to fix time machine"
            elif nearby_time_machine.get("state") == "fixed":
                keybind_guide = "Press S to use time machine"
    
    # Check if near a cooker (only if no chest or time machine guide)
    if keybind_guide is None:
        nearby_cooker = cookerManager.get_nearby_cooker()
        if nearby_cooker:
            keybind_guide = "Press S to use cooker"
    
    # Check if near antenna (lowest priority)
    if keybind_guide is None:
        if blockManager.get_nearby_antenna(player.x, player.y):
            status = "deactivate" if antenna_boost_active else "activate"
            keybind_guide = f"Press S to {status} antenna boost"
    
    # Check if holding placeable block
    if keybind_guide is None:
        items_list = list(inventory.items.items())
        if items_list and inventory.currentSlot - 1 < len(items_list):
            selected_item_id, amount = items_list[inventory.currentSlot - 1]
            if amount > 0:
                item_name = util.getItemName(selected_item_id)
                if item_name.lower() in current_world.placeableBlocks:
                    keybind_guide = "Press W to place block"
                elif item_name in current_world.eatables:
                    keybind_guide = "Press R to eat food"
                elif item_name == "laser gun":
                    # Check if player has battery or liquid fuel to refill
                    battery_id = util.getItemID("battery")
                    fuel_id = util.getItemID("liquid fuel")
                    has_battery = battery_id != -1 and inventory.items.get(battery_id, 0) > 0
                    has_fuel = fuel_id != -1 and inventory.items.get(fuel_id, 0) > 0
                    if player.lasergun_energy < 100 and (has_battery or has_fuel):
                        # Show what items can be used
                        usable_items = []
                        if has_battery:
                            usable_items.append("Battery")
                        if has_fuel:
                            usable_items.append("Liquid Fuel")
                        fuel_str = "/".join(usable_items)
                        keybind_guide = f"Press R to refill ({fuel_str})"
                elif item_name == "Clock":
                    keybind_guide = "Press R to extend hunger time"
                elif item_name == "Keyboard":
                    keybind_guide = "Press R for +15% damage boost"
                elif item_name == "Holy Book":
                    keybind_guide = "Press R to increase max health"
                elif item_name == "Holy Book":
                    keybind_guide = "Press R to increase max health"
    
    # Check if holding an item and display description
    item_description = None
    items_list = list(inventory.items.items())
    if items_list and inventory.currentSlot - 1 < len(items_list):
        selected_item_id, amount = items_list[inventory.currentSlot - 1]
        item_name = util.getItemName(selected_item_id)
        if amount > 0:
            item_description = util.getItemDescription(item_name)
    
    # Render item description and adjust keybind guide position if needed
    description_y = 20
    guide_y = 35
    if item_description and not tutorialManager.is_active:
        text_color = util.getContrastColor(current_world.themeColor)
        renderer.createAndRenderText("item_description", item_description, "Arial", 18, text_color, (w // 2 - len(item_description) * 4, description_y), cache=False, silence=True)
        guide_y = 55  # Move keybind guide down if description is shown
        
        # Re-render keybind guide at new position if it exists
    if keybind_guide and not tutorialManager.is_active:
        renderer.createAndRenderText("keybind_guide", keybind_guide, "Arial", 18, text_color, (w // 2 - len(keybind_guide) * 4, guide_y), cache=False, silence=True)
    
    # Only update monster logic if not in grace period and not in tutorial
    if not grace_period_active and not tutorialManager.is_active and not death_screen_active:
        monsterManager.update(is_focused, is_paused)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.ACTIVEEVENT:
            if event.gain == 0:  # Window lost focus
                is_focused = False
            elif event.gain == 1:  # Window regained focus
                is_focused = True
        if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Get mouse position once for all checks
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Tutorial click handling (highest priority)
                    if tutorialManager.is_active:
                        tutorialManager.handle_click()
                    elif craftManager.is_open:
                        # Check if clicking craft button
                        if hasattr(craftManager, 'craft_button_rect') and craftManager.craft_button_rect.collidepoint(mouse_pos):
                            craftManager.craft_selected()
                        elif craftManager.hovered_slot >= 0:
                            craftManager.on_click(craftManager.hovered_slot)
                    elif cookerManager.is_open and cookerManager.hovered_slot >= 0:
                        cookerManager.on_click(cookerManager.hovered_slot)
                    elif death_screen_active and death_respawn_button_rect and death_respawn_button_rect.collidepoint(mouse_pos):
                        # Play click sound
                        try:
                            click_sound = pygame.mixer.Sound("assets/click.mp3")
                            click_sound.set_volume(0.5)
                            click_sound.play()
                        except:
                            pass
                        
                        # Respawn player
                        player.health = player.max_health
                        player.last_food_time = pygame.time.get_ticks() // 1000  # Reset hunger timer
                        
                        # Clear inventory but retain essentials
                        laser_gun_id = util.getItemID("laser gun")
                        cooked_flesh_id = util.getItemID("cooked monster flesh")
                        # Clear inventory but retain specific items
                        laser_gun_id = util.getItemID("laser gun")
                        cooked_flesh_id = util.getItemID("cooked monster flesh")
                        battery_id = util.getItemID("battery")
                        
                        # Keep only the specified items
                        kept_items = {}
                        if laser_gun_id >= 0 and inventory.items.get(laser_gun_id, 0) > 0:
                            kept_items[laser_gun_id] = 1  # Keep 1 laser gun
                        if cooked_flesh_id >= 0:
                            kept_items[cooked_flesh_id] = 5  # Give 5 cooked monster flesh
                        if battery_id >= 0:
                            kept_items[battery_id] = 3  # Give 3 batteries
                        
                        # Clear and restore inventory
                        inventory.items.clear()
                        inventory.items.update(kept_items)
                        
                        monsterManager.monsters = []  # Reset monsters
                        chestManager.chests = {}  # Reset chests
                        death_screen_active = False
                        death_screen_fade_alpha = 0
                        death_respawn_button_rect = None
                    elif not tutorialManager.is_active and not death_screen_active:
                        num_shots = 2 if antenna_boost_active else 1
                        player.shootLaser(pygame.mouse.get_pos(), inventory, num_shots)
        if event.type == pygame.KEYDOWN: #sum keys for input (exclude a and d for player movement)
            # Disable all key inputs during tutorial
            if tutorialManager.is_active:
                continue
            # Disable all key inputs during death screen
            if death_screen_active:
                continue
            
            if pygame.K_1 <= event.key <= pygame.K_9:
                inventory.setCurrentSlot(event.key - pygame.K_0)
            elif event.key == pygame.K_0:
                inventory.setCurrentSlot(10)
            elif event.key == pygame.K_q:
                inventory.dropCurrent(itemManager, player, 1)
            elif event.key == pygame.K_e:
                craftManager.toggle()
            elif event.key == pygame.K_ESCAPE:
                # If any GUI is open, close them
                if craftManager.is_open or cookerManager.is_open:
                    if craftManager.is_open:
                        craftManager.toggle()
                    if cookerManager.is_open:
                        cookerManager.toggle()
                else:
                    # Toggle pause when no GUIs are open
                    is_paused = not is_paused
            elif event.key == pygame.K_r:
                # Check if holding a clock, holy book, or keyboard first (highest priority)
                items_list = list(inventory.items.items())
                if items_list and inventory.currentSlot - 1 < len(items_list):
                    selected_item_id, amount = items_list[inventory.currentSlot - 1]
                    item_name = util.getItemName(selected_item_id)
                    if item_name == "Clock" and amount > 0:
                        player.use_clock(inventory)
                    elif item_name == "Holy Book" and amount > 0:
                        player.use_holy_book(inventory)
                    elif item_name == "Keyboard" and amount > 0:
                        # Give player stackable 15% damage boost when using keyboard
                        player.damage_boost += 15
                        inventory.removeItem(selected_item_id, 1)
                    elif item_name in current_world.eatables and amount > 0:
                        # Food eating
                        player.eat_food(inventory)
                    else:
                        # Check if near a broken time machine with screwdriver
                        nearby_time_machine = blockManager.get_nearby_time_machine()
                        if nearby_time_machine and nearby_time_machine.get("state") == "broken":
                            blockManager.fix_time_machine(nearby_time_machine)
                        else:
                            player.refillLaserEnergy(inventory)
                else:
                    # Check if near a broken time machine with screwdriver
                    nearby_time_machine = blockManager.get_nearby_time_machine()
                    if nearby_time_machine and nearby_time_machine.get("state") == "broken":
                        blockManager.fix_time_machine(nearby_time_machine)
                    else:
                        player.refillLaserEnergy(inventory)
            elif event.key == pygame.K_s:
                # Check if near antenna first (toggle antenna boost)
                if blockManager.get_nearby_antenna(player.x, player.y):
                    antenna_boost_active = not antenna_boost_active
                    status = "ON" if antenna_boost_active else "OFF"
                # Check if near a fixed time machine (time travel!)
                else:
                    nearby_time_machine = blockManager.get_nearby_time_machine()
                    if nearby_time_machine and nearby_time_machine.get("state") == "fixed":
                        # Check if this is the last world (Whitehole)
                        if current_world_index >= get_world_count() - 1:
                            # Player completed all worlds - break out of the game loop
                            time_machine_used = True
                        else:
                            # Time travel to next world!
                            # Fade out
                            do_fade_transition(fade_out=True, duration_ms=500)
                            
                            # Unload previous world textures to free memory
                            unload_world_textures(renderer, current_world_index)
                            
                            # Advance to next world
                            current_world_index += 1
                            
                            # Load new world textures
                            load_world_textures(renderer, current_world_index)
                            
# Clear player inventory except all food items and laser gun
                        food_items = [
                            util.getItemID("cooked monster flesh"),
                            util.getItemID("cooked mysterious meat"),
                            util.getItemID("mysterious meat"),  # Raw food
                            util.getItemID("monster flesh")     # Raw food
                        ]
                        laser_gun_id = util.getItemID("laser gun")
                        kept_items = {}
                        for item_id, count in inventory.items.items():
                            if item_id in food_items or item_id == laser_gun_id:
                                kept_items[item_id] = count
                        inventory.items.clear()
                        inventory.items.update(kept_items)
                        
                        # Give starting items for new world
                        inventory.addItem(util.getItemID("laser gun"), 1)
                        
                        # Give bonus items
                        inventory.addItem(util.getItemID("cooked monster flesh"), 3)
                        inventory.addItem(util.getItemID("liquid fuel"), 4)
                            
                        # Create new world entities
                        ground, sky, current_world = create_world_entities(current_world_index)
                            
                        # Reset player for new world
                        player.world = current_world
                        player.ground = ground
                        player.x = 0
                        player.y = h - ground.height - 50
                        player.health = 100
                        player.hunger_timer = player.max_hunger_time
                        player.active_lasers.clear()
                        player.lasergun_energy = 100
                        
                        # Reinitialize managers with new world
                        itemManager, craftManager, blockManager, chestManager, monsterManager, cookerManager, beaconManager = initialize_managers(
                            current_world, ground, player, inventory
                        )
                        
                        # Update inventory's world reference
                        inventory.world = current_world
                        inventory.updateWorld(current_world)
                        craftManager.updateWorld(current_world)
                        cookerManager.updateWorld(current_world)
                        
                        # Start grace period
                        grace_period_active = True
                        grace_period_end_time = pygame.time.get_ticks() + GRACE_PERIOD_DURATION
                        
                        # Fade in
                        do_fade_transition(fade_out=False, duration_ms=500)
                        
                        # Show unlock screen for new world items
                        unlocked_items = WORLD_UNLOCKS.get(current_world_index, [])
                        if unlocked_items:
                            unlock_screen_active = True
                            unlock_screen_start_time = pygame.time.get_ticks()
                        
                        console.sendInfo(f"Time traveled to {current_world.world_name}!", __file__)
                    else:
                        # Chest looting has priority over cooker GUI
                        chest_looted = False
                        for n, chest_x in list(chestManager.chests.items()):
                            if player.x + 60 > chest_x and player.x < chest_x + 60 and player.y + 60 > chestManager.groundy and player.y < chestManager.groundy + 60:
                                for name, loot_data in chestManager.loot.items():
                                    rarity = loot_data["rarity"]
                                    drop_chance = chestManager.drop_chances.get(rarity, 1.0)
                                    if random.random() < drop_chance:
                                        item_id = util.getItemID(name)
                                        mn = loot_data["min"]
                                        mx = loot_data["max"]
                                        amt = random.randint(mn, mx)
                                        drop_x = chest_x + random.randint(-20, 20)
                                        itemManager.addItemEntities(item_id, amt, (drop_x, chestManager.groundy))
                                del chestManager.chests[n]
                                chest_looted = True
                                break
                        if not chest_looted:
                            nearby_cooker = cookerManager.get_nearby_cooker()
                            if nearby_cooker:
                                cookerManager.toggle()
            elif event.key == pygame.K_w:
                # Place block in the direction the player is facing
                blockManager.place_block(player.x, inventory.lastDir)
    
    
    # Render pause screen if paused
    if is_paused:
        # Darken the screen
        pause_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 200))  # real alpha
        renderer.render_surface(pause_overlay, (0, 0))
        
        # Render "Game Paused" text in center
        pause_text = "Game Paused"
        text_color = (255, 255, 255)
        text_x = w // 2 - len(pause_text) * 12 
        text_y = h // 2 - 20
        renderer.createAndRenderText("game_paused_text", pause_text, "Arial", 48, text_color, (text_x, text_y), cache=False, silence=True)
    
    pygame.display.flip()

# Show win screen after completing all worlds
while 1:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            util.getRenderer().cleanUp("all")
            pygame.quit()
            sys.exit()
    render_win_screen()
    pygame.display.flip()

# Wait a bit then exit
pygame.time.wait(3000)  # Show for 3 seconds
pygame.quit()
sys.exit()