import util
from animations import SpriteAnimation
import pygame
class InventoryManager:
    def __init__(self,id):
        self.items:dict[int,int] = {} # itemID:amount
        self.renderer = util.getRenderer()
        self.currentSlot = 1
        self.num_slots = 10
        self.spriteAnimation = SpriteAnimation(id,(24,24),2)
        self.lastDir = 1
        self.cached_dims = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.slotSize = 24
        self.icon_size = 20
        self.icon_cache = {}
        self.icon_id_cache = {}
        self.amt_cache = {}
        self.recalcLayout()
    def recalcLayout(self):
        w, h = util.getScreenDimensions()
        self.cached_dims = (w, h)
        self.x_offset = int(w * 0.01)
        self.y_offset = int(h * 0.06)
        self.slotSize = max(24, int(h * 0.07))
        self.icon_size = self.slotSize - 4
        self.icon_cache.clear()
        self.icon_id_cache.clear()
        self.amt_cache.clear()
        if hasattr(self, 'held_cache'):
            self.held_cache.clear()
    def updateSlotSize(self):
        self.recalcLayout()
    def updateDirection(self, keys_pressed):
        if keys_pressed[util.pygame.K_a]:
            self.lastDir = -1
        elif keys_pressed[util.pygame.K_d]:
            self.lastDir = 1
    def addItem(self,id:int,amount:int):
        if id in self.items:
            self.items[id] += amount
        else:
            self.items[id] = amount
    def removeItem(self,id:int,amount:int):
        if id in self.items:
            self.items[id] -= amount
            if self.items[id] <= 0:
                self.items[id] = 0
    def renderInventory(self):
        dims = util.getScreenDimensions()
        if dims != self.cached_dims:
            self.recalcLayout()
        items_list = list(self.items.items())
        slot_size = self.slotSize
        icon_size = self.icon_size
        x_off = self.x_offset
        y_off = self.y_offset
        for idx in range(1, self.num_slots + 1):
            pos_y = y_off + (idx - 1) * slot_size
            frame = 1 if idx == self.currentSlot else 0
            self.spriteAnimation.doSpriteAnimation(frame, (x_off, pos_y), (slot_size, slot_size))
            if idx <= len(items_list):
                item_id, amount = items_list[idx - 1]
                if amount <= 0:
                     continue
                icon_id = f"items_{item_id:03d}"
                key = (item_id, icon_size)
                surf = self.icon_cache.get(key)
                if surf is None:
                    base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=True)
                    if surf:
                        self.icon_cache[key] = surf
                if surf:
                    self.renderer.render([surf], [(x_off + 2, pos_y + 2)])
                text_pos = (x_off + slot_size + 8, pos_y + slot_size // 4)
                amt_key = (item_id, amount)
                tex_id = self.amt_cache.get(amt_key)
                if tex_id is None:
                    tex_id = f"inv_amt_{item_id}_{amount}"
                    self.renderer.createText(tex_id, str(amount), "arial", 18, (255,255,255), True)
                    self.amt_cache[amt_key] = tex_id
                self.renderer.render([tex_id], [text_pos])
        if items_list and 1 <= self.currentSlot <= len(items_list):
            sel_id, sel_amt = items_list[self.currentSlot - 1]
            if sel_amt > 0:
                name = util.getItemName(sel_id)
                self.renderer.createAndRenderText(
                    "inv_selected_name", name, "arial", 20, (0,0,0), (10, 10), cache=False, silence=True
                )
    def dropCurrent(self, itemManager, player, amount: int = 1):
        items_list = list(self.items.items())
        if self.currentSlot - 1 < len(items_list):
            item_id, have = items_list[self.currentSlot - 1]
            if item_id == util.getItemID("laser gun"):
                return
            amt = min(amount, have)
            if amt <= 0:
                return
            offset = 30 * self.lastDir
            itemManager.addItemEntities(item_id, amt, (player.x + offset, util.getScreenDimensions()[1] - self.slotSize))
            self.removeItem(item_id, amt)
    def setCurrentSlot(self, slot):
        if 1 <= slot <= self.num_slots:
            self.currentSlot = slot
    
    def renderHeldItem(self, player):
        items_list = list(self.items.items())
        if not items_list or self.currentSlot - 1 >= len(items_list):
            return
        item_id, amount = items_list[self.currentSlot - 1]
        if amount <= 0:
            return
        icon_id = f"items_{item_id:03d}"
        held_size = max(24, int(self.slotSize * 0.8))
        cache_key = (item_id, held_size, self.lastDir)
        if not hasattr(self, 'held_cache'):
            self.held_cache = {}
        surf = self.held_cache.get(cache_key)
        if surf is None:
            base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
            base_surf = self.renderer.ResizeTexture(base_id, [held_size, held_size], False, save=False)
            if base_surf:
                if self.lastDir == -1:
                    surf = pygame.transform.flip(base_surf, True, False)
                else:
                    surf = base_surf
                self.held_cache[cache_key] = surf
        if surf:
            if self.lastDir == -1:
                item_x = util.getScreenDimensions()[0]//2-25 - held_size//2 - 5
            else:
                item_x = util.getScreenDimensions()[0]//2+25 - held_size//2 + 5 #5px is offset (so items doesnt look so squished)
            item_y = player.y
            self.renderer.render([surf], [(item_x, item_y)])
        if item_id == util.getItemID("laser gun") and amount > 0:
            w, h = util.getScreenDimensions()
            energy_text = f"Energy: {player.lasergun_energy}%"
            self.renderer.createAndRenderText(
                "lasergun_energy", energy_text, "arial", 18, (0, 255, 0) if player.lasergun_energy > 30 else (255, 0, 0),
                (w // 2 - 50, 30), cache=False, silence=True
            )
        
 
class CraftingManager:
    def __init__(self,world):
        self.world = world
        self.renderer = util.getRenderer()
        self.is_open = False
        self.overlay_id = "craft_overlay"
        w, h = util.getScreenDimensions()
        self.renderer.createSolidTexture(self.overlay_id, (0, 0, 0, 180), (w, h), 4)
        self.gui_base = "guibase1"
        self.hotbarSprite = SpriteAnimation("hotbar1", (24, 24), 2)
        self.screen_w = w
        self.screen_h = h
        self.craftables = ["crafted_item_1", "crafted_item_2", "crafted_item_3", "crafted_item_4", "crafted_item_5"]
        self.cached_dims = (0, 0)
        self.gui_scaled = None
        self.gui_x = 0
        self.gui_y = 0
        self.list_x = 0
        self.list_y = 0
        self.item_spacing = 0
        self.slot_size = 24
        self.gui_w = 0
        self.gui_h = 0
        self.recalcLayout()
    def recalcLayout(self):
        w, h = util.getScreenDimensions()
        self.cached_dims = (w, h)
        self.screen_w = w
        self.screen_h = h
        gui_texture = self.renderer.getTexture(self.gui_base)
        if gui_texture:
            gui_w = int(w * 0.6)
            gui_h = int(h * 0.7)
            self.gui_w = gui_w
            self.gui_h = gui_h
            self.gui_scaled = pygame.transform.scale(gui_texture, (gui_w, gui_h))
            self.gui_x = (w - gui_w) // 2
            self.gui_y = (h - gui_h) // 2
            # Center craft boxes in left third with responsive sizing
            self.slot_size = max(24, int(min(gui_w, gui_h) * 0.08))
            left_third_center_x = self.gui_x + (gui_w // 3) // 2
            self.list_x = left_third_center_x - self.slot_size // 2
            self.list_y = self.gui_y + int(gui_h * 0.15)
            self.item_spacing = int(self.slot_size * 1.6)
    def toggle(self):
        self.is_open = not self.is_open
    def render(self):
        if not self.is_open:
            return
        dims = util.getScreenDimensions()
        if dims != self.cached_dims:
            self.recalcLayout()
        self.renderer.render([self.overlay_id], [(0, 0)])
        if self.gui_scaled:
            self.renderer.screen.blit(self.gui_scaled, (self.gui_x, self.gui_y))
            line_x = self.gui_x + self.gui_w // 3
            pygame.draw.line(self.renderer.screen, self.world.themeColor, 
                           (line_x, round(self.gui_y*1.4)), (line_x, self.gui_y + self.gui_h), 4)
            
            title_x = self.gui_x + self.gui_w // 2 - 40
            title_y = round(self.gui_y*1.3) + int(self.gui_h * 0.03)
            self.renderer.render(["crafting_title"], [(title_x, title_y)])
            
            for idx, item_name in enumerate(self.craftables):
                slot_pos = (self.list_x, self.list_y + idx * self.item_spacing)
                self.hotbarSprite.doSpriteAnimation(1, slot_pos, (self.slot_size, self.slot_size))


