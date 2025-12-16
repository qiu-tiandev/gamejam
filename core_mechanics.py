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
        self._cached_dims = (0, 0)
        self._x_offset = 0
        self._y_offset = 0
        self.slotSize = 24
        self._icon_size = 20
        self._icon_cache = {}
        self._icon_id_cache = {}
        self._amt_cache = {}
        self._recalcLayout()
    def _recalcLayout(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self._x_offset = int(w * 0.01)
        self._y_offset = int(h * 0.06)
        self.slotSize = max(24, int(h * 0.07))
        self._icon_size = self.slotSize - 4
        self._icon_cache.clear()
        self._icon_id_cache.clear()
        self._amt_cache.clear()
    def updateSlotSize(self):
        self._recalcLayout()
    def updateDirection(self, keys_pressed):
        if keys_pressed.get(util.pygame.K_a, False):
            self.lastDir = -1
        elif keys_pressed.get(util.pygame.K_d, False):
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
        if dims != self._cached_dims:
            self._recalcLayout()
        items_list = list(self.items.items())
        slot_size = self.slotSize
        icon_size = self._icon_size
        x_off = self._x_offset
        y_off = self._y_offset
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
                surf = self._icon_cache.get(key)
                if surf is None:
                    base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=True)
                    if surf:
                        self._icon_cache[key] = surf
                if surf:
                    self.renderer.render([surf], [(x_off + 2, pos_y + 2)])
                text_pos = (x_off + slot_size + 8, pos_y + slot_size // 4)
                amt_key = (item_id, amount)
                tex_id = self._amt_cache.get(amt_key)
                if tex_id is None:
                    tex_id = f"inv_amt_{item_id}_{amount}"
                    self.renderer.createText(tex_id, str(amount), "arial", 18, (255,255,255), True)
                    self._amt_cache[amt_key] = tex_id
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
            amt = min(amount, have)
            if amt <= 0:
                return
            offset = 30 * self.lastDir
            itemManager.addItemEntities(item_id, amt, (player.x + offset, util.getScreenDimensions()[1] - self.slotSize))
            self.removeItem(item_id, amt)
    def setCurrentSlot(self, slot):
        if 1 <= slot <= self.num_slots:
            self.currentSlot = slot
        
 
class CraftingManager:
    def __init__(self):
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
        self._cached_dims = (0, 0)
        self._gui_scaled = None
        self._gui_x = 0
        self._gui_y = 0
        self._list_x = 0
        self._list_y = 0
        self._item_spacing = 0
        self._recalcLayout()
    def _recalcLayout(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self.screen_w = w
        self.screen_h = h
        gui_texture = self.renderer.getTexture(self.gui_base)
        if gui_texture:
            gui_w = int(w * 0.6)
            gui_h = int(h * 0.7)
            self._gui_scaled = pygame.transform.scale(gui_texture, (gui_w, gui_h))
            self._gui_x = (w - gui_w) // 2
            self._gui_y = (h - gui_h) // 2
            self._list_x = self._gui_x + int(gui_w * 0.05)
            self._list_y = self._gui_y + int(gui_h * 0.05)
            self._item_spacing = int(gui_h * 0.12)
    def toggle(self):
        self.is_open = not self.is_open
    def render(self):
        if not self.is_open:
            return
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self._recalcLayout()
        self.renderer.render([self.overlay_id], [(0, 0)])
        if self._gui_scaled:
            self.renderer.screen.blit(self._gui_scaled, (self._gui_x, self._gui_y))
            for idx, item_name in enumerate(self.craftables):
                slot_pos = (self._list_x, self._list_y + idx * self._item_spacing)
                self.hotbarSprite.doSpriteAnimation(1, slot_pos)


