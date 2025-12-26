import util
from animations import SpriteAnimation
import pygame
class InventoryManager:
    def __init__(self, id, world=None):
        self.items:dict[int,int] = {}
        self.renderer = util.getRenderer()
        self.world = world
        self.currentSlot = 1
        self.num_slots = 10
        if world:
            self.hotbar_unselected_id = f"hotbar_{(world.world_index * 2) + 1:03d}"
            self.hotbar_selected_id = f"hotbar_{(world.world_index * 2) + 2:03d}"
        else:
            self.hotbar_unselected_id = "hotbar_001"
            self.hotbar_selected_id = "hotbar_002"
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
    def updateWorld(self, world):
        self.world = world
        if world:
            self.hotbar_unselected_id = f"hotbar_{(world.world_index * 2) + 1:03d}"
            self.hotbar_selected_id = f"hotbar_{(world.world_index * 2) + 2:03d}"
        else:
            self.hotbar_unselected_id = "hotbar_001"
            self.hotbar_selected_id = "hotbar_002"
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
    def canAddItem(self, id: int) -> bool:
        return id in self.items or len(self.items) < self.num_slots
    
    def addItem(self, id: int, amount: int) -> bool:
        if self.canAddItem(id):
            if id in self.items:
                self.items[id] += amount
            else:
                self.items[id] = amount
            return True
        return False
    
    def removeItem(self, id: int, amount: int):
        if id in self.items:
            self.items[id] -= amount
            if self.items[id] <= 0:
                del self.items[id]
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
            hotbar_id = self.hotbar_selected_id if idx == self.currentSlot else self.hotbar_unselected_id
            hotbar_tex = self.renderer.getTexture(hotbar_id)
            if hotbar_tex:
                scaled_hotbar = pygame.transform.scale(hotbar_tex, (slot_size, slot_size))
                self.renderer.screen.blit(scaled_hotbar, (x_off, pos_y))
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
                text_color = util.getContrastColor(self.world.themeColor) if self.world else (255, 255, 255)
                tex_id = f"inv_amt_slot_{idx}"
                self.renderer.createText(tex_id, str(amount), "arial", 18, text_color, True, silence=True)
                self.renderer.render([tex_id], [text_pos])
        if items_list and 1 <= self.currentSlot <= len(items_list):
            sel_id, sel_amt = items_list[self.currentSlot - 1]
            if sel_amt > 0:
                name = util.getItemName(sel_id)
                text_color = util.getContrastColor(self.world.themeColor) if self.world else (0, 0, 0)
                w, h = util.getScreenDimensions()
                self.renderer.createAndRenderText(
                    "inv_selected_name", name, "arial", 26, text_color, (w // 2 - len(name) * 6.7, 70), cache=False, silence=True
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
                item_x = util.getScreenDimensions()[0]//2-10 - held_size//2 - 5
            else:
                item_x = util.getScreenDimensions()[0]//2+10 - held_size//2 +5 #5px is offset (so items doesnt look so squished)
            item_y = player.y
            self.renderer.render([surf], [(item_x, item_y)])
        if item_id == util.getItemID("laser gun") and amount > 0:
            w, h = util.getScreenDimensions()
            energy_text = f"Energy: {player.lasergun_energy}%"
            self.renderer.createAndRenderText(
                "lasergun_energy", energy_text, "arial", 18, (0, 255, 0) if player.lasergun_energy > 30 else (255, 0, 0),
                (w // 2 - 60, 35), cache=False, silence=True
            )
        
 
class CraftingManager:
    def __init__(self,world, inventory):
        self.world = world
        self.inventory = inventory
        self.renderer = util.getRenderer()
        self.is_open = False
        self.overlay_id = "craft_overlay"
        w, h = util.getScreenDimensions()
        self.renderer.createSolidTexture(self.overlay_id, (0, 0, 0, 180), (w, h), 4)
        self.world = world
        # GUI sprite is gui_{world_index+1:03d}
        self.gui_base = f"gui_{world.world_index + 1:03d}"
        # Hotbar sprites: hotbar_{(world_index*2)+1:03d} (unselected) and hotbar_{(world_index*2)+2:03d} (selected)
        self.hotbar_unselected_id = f"hotbar_{(world.world_index * 2) + 1:03d}"
        self.hotbar_selected_id = f"hotbar_{(world.world_index * 2) + 2:03d}"
        # Button sprites: button_{world_index+1:03d} (normal) - hover effect implemented via brightness
        self.button_normal_id = f"button_{world.world_index + 1:03d}"
        self.screen_w = w
        self.screen_h = h
        self.craftables = list(world.craftingRecipes.keys())
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
        self.icon_cache = {}
        self.hovered_slot = -1
        self.selected_recipe = -1
        self.recalcLayout()
    def updateWorld(self, world):
        self.world = world
        self.gui_base = f"gui_{world.world_index + 1:03d}"
        self.hotbar_unselected_id = f"hotbar_{(world.world_index * 2) + 1:03d}"
        self.hotbar_selected_id = f"hotbar_{(world.world_index * 2) + 2:03d}"
        self.button_normal_id = f"button_{world.world_index + 1:03d}"
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
            self.slot_size = max(24, int(min(gui_w, gui_h) * 0.08))
            left_third_center_x = self.gui_x + (gui_w // 3) // 2
            self.list_x = left_third_center_x - self.slot_size // 2
            self.list_y = self.gui_y + int(gui_h * 0.15)
            self.item_spacing = int(self.slot_size * 1.6)
            self.icon_cache.clear()
    def toggle(self):
        self.is_open = not self.is_open
        if not self.is_open:
            self.selected_recipe = -1
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def can_craft(self, recipe_materials):
        for material_name, required_amount in recipe_materials:
            material_id = util.getItemID(material_name)
            current_amount = self.inventory.items.get(material_id, 0)
            if current_amount < required_amount:
                return False
        return True
    
    def on_click(self, idx):
        if idx >= 0 and idx < len(self.craftables):
            self.selected_recipe = idx
            try:
                click_sound = pygame.mixer.Sound("assets/click.mp3")
                click_sound.set_volume(0.5)
                click_sound.play()
            except:
                pass
    
    def craft_selected(self):
        if self.selected_recipe < 0 or self.selected_recipe >= len(self.craftables):
            return False
        
        recipe_name = self.craftables[self.selected_recipe]
        recipe_materials = self.world.craftingRecipes[recipe_name]
        
        if not self.can_craft(recipe_materials):
            return False
        
        crafted_item_id = util.getItemID(recipe_name)
        if not self.inventory.canAddItem(crafted_item_id):
            return False
        
        for material_name, required_amount in recipe_materials:
            material_id = util.getItemID(material_name)
            self.inventory.removeItem(material_id, required_amount)
        
        self.inventory.addItem(crafted_item_id, 1)
        
        return True
    
    def render(self):
        if not self.is_open:
            return
        dims = util.getScreenDimensions()
        if dims != self.cached_dims:
            self.recalcLayout()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered_slot = -1
        cursor_changed = False
        
        self.renderer.render([self.overlay_id], [(0, 0)])
        if self.gui_scaled:
            self.renderer.screen.blit(self.gui_scaled, (self.gui_x, self.gui_y))
            line_x = self.gui_x + self.gui_w // 3
            pygame.draw.line(self.renderer.screen, self.world.themeColor, 
                           (line_x, round(self.gui_y*1.4)), (line_x, self.gui_y + self.gui_h), 4)
            
            title_x = round((self.gui_x + self.gui_w // 2)*1.09)
            title_y = round(self.gui_y*1.3) + int(self.gui_h * 0.02)
            self.renderer.render(["crafting_title"], [(title_x, title_y)])
            
            icon_size = self.slot_size - 4
            max_per_column = 7
            num_items = len(self.craftables)
            num_columns = (num_items + max_per_column - 1) // max_per_column  # Ceiling division
            
            for idx, item_name in enumerate(self.craftables):
                column = idx // max_per_column
                row = idx % max_per_column
                slot_pos = (self.list_x + column * (self.slot_size + 10), self.list_y + row * self.item_spacing)
                
                hotbar_tex = self.renderer.getTexture(self.hotbar_unselected_id)
                if hotbar_tex:
                    scaled_hotbar = pygame.transform.scale(hotbar_tex, (self.slot_size, self.slot_size))
                    self.renderer.screen.blit(scaled_hotbar, slot_pos)
                
                recipe_materials = self.world.craftingRecipes[item_name]
                can_craft = self.can_craft(recipe_materials)
                outline_color = (0, 255, 0) if can_craft else (255, 0, 0)
                
                pygame.draw.rect(self.renderer.screen, outline_color, 
                               (slot_pos[0], slot_pos[1], self.slot_size, self.slot_size), 2)
                
                item_id = util.getItemID(item_name)
                icon_id = f"items_{item_id:03d}"
                cache_key = (item_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(slot_pos[0] + 2, slot_pos[1] + 2)])
                
                if (slot_pos[0] <= mouse_x <= slot_pos[0] + self.slot_size and
                    slot_pos[1] <= mouse_y <= slot_pos[1] + self.slot_size):
                    self.hovered_slot = idx
                    if can_craft:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        cursor_changed = True
            
            if not cursor_changed:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            if self.selected_recipe >= 0 and self.selected_recipe < len(self.craftables):
                self.render_recipe_details(self.selected_recipe)
    
    def render_recipe_details(self, recipe_idx):
        recipe_name = self.craftables[recipe_idx]
        recipe_materials = self.world.craftingRecipes[recipe_name]
        
        w, h = util.getScreenDimensions()
        base_icon_size = max(24, int(min(w, h) * 0.11))
        num_ingredients = len(recipe_materials)
        
        if num_ingredients > 3:
            icon_size = max(16, int(base_icon_size * 0.6))
        else:
            icon_size = base_icon_size
        
        item_spacing = int(icon_size * 2)
        text_offset_y = icon_size + 5
        right_section_start = self.gui_x + (self.gui_w) // 4 + 10
        right_section_end = self.gui_x + self.gui_w
        right_section_width = right_section_end - right_section_start
        
        total_width = num_ingredients * item_spacing - (item_spacing - icon_size)
        
        use_two_rows = total_width > right_section_width
        if use_two_rows:
            items_per_row = max(1, (num_ingredients + 1) // 2)
            row_width = items_per_row * item_spacing - (item_spacing - icon_size)
            start_x = right_section_start + (right_section_width - row_width) // 2
            rows = 2
        else:
            start_x = right_section_start + (right_section_width - total_width) // 2
            items_per_row = num_ingredients
            rows = 1
        
        right_section_y = self.gui_y + int(self.gui_h * 0.15)
        row_spacing = icon_size + text_offset_y + icon_size // 2 + 10  # Space between rows
        
        for row in range(rows):
            row_start_idx = row * items_per_row
            row_end_idx = min((row + 1) * items_per_row, num_ingredients)
            row_ingredients = recipe_materials[row_start_idx:row_end_idx]
            
            if use_two_rows:
                row_width = len(row_ingredients) * item_spacing - (item_spacing - icon_size)
                start_x = right_section_start + (right_section_width - row_width) // 2
            
            for ingredient_idx, (material_name, required_amount) in enumerate(row_ingredients):
                material_id = util.getItemID(material_name)
                current_amount = self.inventory.items.get(material_id, 0)
                has_enough = current_amount >= required_amount
                text_color = (0, 255, 0) if has_enough else (255, 0, 0)
                
                x_pos = start_x + ingredient_idx * item_spacing
                y_pos = right_section_y + row * row_spacing
                
                icon_id = f"items_{material_id:03d}"
                cache_key = (material_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(x_pos, y_pos)])
                
                font_size = icon_size // 3
                font = pygame.font.SysFont("arial", font_size)
                name_width = font.size(material_name)[0]
                name_x = x_pos + (icon_size - name_width) // 2
                self.renderer.createAndRenderText(
                    f"recipe_ingredient_{row}_{ingredient_idx}", material_name, "arial", font_size, text_color,
                    (name_x, y_pos + text_offset_y), cache=False, silence=True
                )
                amnt_vs_req = f"{current_amount}/{required_amount}"
                text_width = font.size(amnt_vs_req)[0]
                text_x = x_pos + (icon_size - text_width) // 2
                
                self.renderer.createAndRenderText(
                    f"recipe_ingredient_amt_{row}_{ingredient_idx}", amnt_vs_req, "arial", font_size, text_color,
                    (text_x, y_pos + text_offset_y + icon_size // 2), cache=False, silence=True
                )
        
        recipe_description = util.getItemDescription(recipe_name)
        if recipe_description:
            if util.getScreenDimensions()[1] < 800:
                description_y = right_section_y+ item_spacing
            else:
                description_y = right_section_y + item_spacing + 20
            text_color = util.getContrastColor(self.world.themeColor)
            description_font_size = max(10, int(min(w, h) * 0.03))
            temp_font = pygame.font.SysFont("Arial", description_font_size)
            text_width = temp_font.size(recipe_description)[0]
            description_x = right_section_start + (right_section_width - text_width) // 2
            self.renderer.createAndRenderText(
                f"recipe_description_{recipe_name}", recipe_description, "Arial", description_font_size, text_color,
                (description_x, description_y), cache=False, silence=True
            )
        
        result_item_id = util.getItemID(recipe_name)
        result_icon_id = f"items_{result_item_id:03d}"
        result_icon_size = max(32, int(min(w, h) * 0.11))
        result_cache_key = (result_item_id, result_icon_size)
        
        result_x = self.gui_x//10+self.gui_w - result_icon_size
        result_y = self.gui_y//5 + self.gui_h - result_icon_size - 50
        
        result_surf = self.icon_cache.get(result_cache_key)
        if result_surf is None:
            result_base_id = result_icon_id if self.renderer.getTexture(result_icon_id) else "placeholder-item"
            result_surf = self.renderer.ResizeTexture(result_base_id, [result_icon_size, result_icon_size], False, save=False)
            if result_surf:
                self.icon_cache[result_cache_key] = result_surf
        
        # Render craft button below result
        button_width = 100
        button_height = 30
        button_x = result_x - (button_width - result_icon_size) // 2
        button_y = result_y + result_icon_size*1.9 +5
        self.craft_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovering = self.craft_button_rect.collidepoint(mouse_x, mouse_y)
        can_craft = self.can_craft(recipe_materials)
        
        # Choose button sprite and effects based on state
        if not can_craft:
            button_sprite_id = self.button_normal_id  # Normal state, will be tinted gray
            tint_disabled = True
            brightness_boost = 0
        elif is_hovering:
            button_sprite_id = self.button_normal_id  # Normal state with brightness boost for hover
            tint_disabled = False
            brightness_boost = 50  # Make it brighter on hover
        else:
            button_sprite_id = self.button_normal_id  # Normal state
            tint_disabled = False
            brightness_boost = 0
        
        # Render button sprite
        button_tex = self.renderer.getTexture(button_sprite_id)
        if button_tex:
            scaled_button = pygame.transform.scale(button_tex, (button_width, button_height))
            if tint_disabled:
                # Apply gray tint for disabled state
                gray_surface = pygame.Surface(scaled_button.get_size(), pygame.SRCALPHA)
                gray_surface.fill((100, 100, 100, 150))
                scaled_button.blit(gray_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif brightness_boost > 0:
                # Apply brightness boost for hover state
                bright_surface = pygame.Surface(scaled_button.get_size(), pygame.SRCALPHA)
                bright_surface.fill((brightness_boost, brightness_boost, brightness_boost, 0))
                scaled_button.blit(bright_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.renderer.screen.blit(scaled_button, (button_x, button_y))
        else:
            # Fallback to colored rectangle if sprite not found
            if can_craft:
                button_color = (0, 200, 0) if is_hovering else (0, 150, 0)
            else:
                button_color = (100, 100, 100)
            pygame.draw.rect(self.renderer.screen, button_color, self.craft_button_rect)
            pygame.draw.rect(self.renderer.screen, (255, 255, 255), self.craft_button_rect, 2)
        
        # Save button position for text centering
        craft_button_x = button_x
        craft_button_y = button_y
        
        if result_surf:
            self.renderer.render([result_surf], [(result_x, result_y)])
        result_name = util.getItemName(result_item_id)
        
        result_font_size = result_icon_size // 3
        result_font = pygame.font.SysFont("arial", result_font_size)
        result_name_width = result_font.size(result_name.capitalize())[0]
        result_name_x = result_x + (result_icon_size - result_name_width) // 2
        text_color = util.getContrastColor(self.world.themeColor)
        self.renderer.createAndRenderText(
            "recipe_result_name", result_name.capitalize(), "arial", result_font_size, text_color,
            (result_name_x, result_y + result_icon_size), cache=False, silence=True
        )
        button_size = max(40, int(min(w, h) * 0.1))
        button_x = result_x + result_icon_size // 2 - button_size // 2
        button_y = result_y + result_icon_size + 40 
        
        
        button_text = "CRAFT"
        font_size = button_size // 3
        font = pygame.font.SysFont("arial", font_size)
        text_width = font.size(button_text)[0]
        text_x = craft_button_x + (button_width - text_width) // 2
        text_y = craft_button_y + (button_height - font_size) // 2
        self.renderer.createAndRenderText(
            "craft_button_text", button_text, "arial", font_size, text_color,
            (text_x, text_y), cache=False, silence=True
        )

class BlockManager:
    def __init__(self, world, ground, inventory, player, solid:bool=True):
        self.world = world
        self.ground = ground
        self.inventory = inventory
        self.player = player
        self.renderer = util.getRenderer()
        self.placed_blocks = []
        self.block_size = 40
        self.icon_cache = {}
        self._cached_dims = (0, 0)
        self.groundy = 0
        self.solid = solid
        self.updateGroundY()
    
    def updateGroundY(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self.groundy = h - self.ground.height - self.block_size
    
    def get_nearby_time_machine(self):
        player_x = self.player.x
        player_y = self.player.y
        interaction_range = 80
        
        for block in self.placed_blocks:
            if block.get("type") == "time machine" and not block.get("is_top", False):
                block_x = block["x"]
                block_y = self.groundy
                
                dist_x = abs(player_x - block_x)
                dist_y = abs(player_y - (block_y - 25))
                
                if dist_x < interaction_range and dist_y < interaction_range:
                    return block
        
        return None
    
    def fix_time_machine(self, block):
        if block and block.get("state") == "broken":
            screwdriver_id = util.getItemID("screwdriver")
            if screwdriver_id >= 0 and self.inventory.items.get(screwdriver_id, 0) > 0:
                # Remove screwdriver
                self.inventory.removeItem(screwdriver_id, 1)
                # Fix the time machine
                block["state"] = "fixed"
                return True
        return False
    
    def get_nearby_antenna(self, player_x, player_y):
        interaction_range = 100  # Range for antenna boost
        
        for block in self.placed_blocks:
            if block.get("type") == "antenna" and not block.get("is_top", False):
                block_x = block["x"]
                block_y = self.groundy
                
                dist_x = abs(player_x - block_x)
                dist_y = abs(player_y - (block_y - 25))
                
                if dist_x < interaction_range and dist_y < interaction_range:
                    return True
        
        return False
    
    def place_block(self, player_x, direction):
        items_list = list(self.inventory.items.items())
        if not items_list or self.inventory.currentSlot - 1 >= len(items_list):
            return False
        
        selected_item_id, amount = items_list[self.inventory.currentSlot - 1]
        if amount <= 0:
            return False
        
        block_type = util.getItemName(selected_item_id)
        block_type_normalized = block_type.lower()
        
        if block_type_normalized not in self.world.placeableBlocks:
            return False
        
        self.inventory.removeItem(selected_item_id, 1)
        
        offset = 70 * direction
        block_x = player_x + offset
        
        is_solid = self.world.blockProperties.get(block_type_normalized, {}).get("solid", True)
        
        # time machines and cookers have special states
        initial_state = "idle" if block_type_normalized == "cooker" else ("broken" if block_type_normalized == "time machine" else "default")
        
        self.placed_blocks.append({
            "type": block_type_normalized,
            "id": selected_item_id,
            "x": block_x,  # World x coordinate
            "solid": is_solid,  # Use block type's solidity setting
            "height": self.world.blockProperties.get(block_type_normalized, {}).get("height", 1),  # Block height in blocks
            "state": initial_state  # Initial state for different block types
        })
        
        if self.world.blockProperties.get(block_type_normalized, {}).get("height", 1) == 2:
            self.placed_blocks.append({
                "type": f"{block_type_normalized}_top",
                "id": selected_item_id,
                "x": block_x,
                "solid": is_solid,
                "height": 1,
                "is_top": True,
                "parent_x": block_x,
                "state": "default"
            })
        
        return True
    
    def get_block_under_player(self, player_x, player_y):
        player_left = player_x - 25
        player_right = player_x + 25
        player_bottom = player_y + 50
        
        for block in self.placed_blocks:
            if block.get("is_top", False):
                continue
            if not block.get("solid", True):
                continue
            
            block_left = block['x']
            block_right = block['x'] + self.block_size
            block_top = self.groundy
            
            if player_right > block_left and player_left < block_right:
                if abs(player_bottom - block_top) <= 10:
                    return block
        
        return None
    
    def check_collision(self, player_x, player_y, direction):
        player_left = player_x - 25
        player_right = player_x + 25
        player_bottom = player_y + 50
        
        for block in self.placed_blocks:
            if block.get("is_top", False):
                continue
            if not block.get("solid", True):
                continue
            
            block_left = block['x']
            block_right = block['x'] + self.block_size
            block_top = self.groundy
            
            if player_bottom > block_top:
                if direction == 1:
                    if player_right >= block_left - 5 and player_right <= block_right and player_left < block_left:
                        return True
                elif direction == -1:
                    if player_left <= block_right + 5 and player_left >= block_left and player_right > block_right:
                        return True
        
        return False
    
    def render_blocks(self):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.updateGroundY()
        
        player_x = self.player.x
        screenx = dims[0]
        
        for block in self.placed_blocks:
            if block.get("is_top", False):
                continue
                
            pos_on_screen = block['x'] - player_x + screenx // 2
            if -100 <= pos_on_screen <= screenx + 100:
                block_type = block['type']
                asset_path = self.world.blockAssets.get(block_type)
                block_state = block.get("state", "default")
                
                if asset_path:
                    if block_type == "cooker":
                        frame_num = 1 if block_state == "idle" else 2
                        asset_id = f"block_cooker_{frame_num:03d}"  # e.g., "block_cooker_001" or "block_cooker_002"
                    elif block_type == "time machine":
                        asset_id = "block_time_machine"  # Pre-loaded in worker.py
                    else:
                        asset_id = f"block_{block_type}"
                    
                    if block_type == "time machine":
                        cache_key = (asset_id, "time_machine")
                        surf = self.icon_cache.get(cache_key)
                        
                        if surf is None:
                            if self.renderer.getTexture(asset_id):
                                surf = self.renderer.ResizeTexture(asset_id, [self.block_size, self.block_size * 2], False, save=False)
                                if surf:
                                    self.icon_cache[cache_key] = surf
                        
                        if surf:
                            self.renderer.render([surf], [(pos_on_screen, self.groundy - self.block_size)])
                            
                            # show status text
                            if block_state == "broken":
                                text_x = pos_on_screen + self.block_size // 2 - 30
                                text_y = self.groundy - self.block_size - 30
                                self.renderer.createAndRenderText(
                                    f"broken_tm_{block['x']}", "Broken", "Arial", 18, (255, 0, 0),
                                    (text_x, text_y), cache=False, silence=True
                                )
                                # Show instruction below
                                instruction_x = pos_on_screen + self.block_size // 2 - 80
                                instruction_y = self.groundy - self.block_size - 10
                                self.renderer.createAndRenderText(
                                    f"fix_tm_{block['x']}", "Use screwdriver to fix", "Arial", 12, (255, 100, 100),
                                    (instruction_x, instruction_y), cache=False, silence=True
                                )
                    else:
                        cache_key = (asset_id, 24)
                        surf = self.icon_cache.get(cache_key)
                        
                        if surf is None:
                            if self.renderer.getTexture(asset_id) is None:
                                try:
                                    self.renderer.loadTexture(asset_path, asset_id)
                                except:
                                    pass
                            
                            if self.renderer.getTexture(asset_id):
                                surf = self.renderer.ResizeTexture(asset_id, [self.block_size, self.block_size], False, save=False)
                                if surf:
                                    self.icon_cache[cache_key] = surf
                        
                        if surf:
                            self.renderer.render([surf], [(pos_on_screen, self.groundy)])
                else:
                    icon_id = f"items_{block['id']:03d}"
                    cache_key = (block['id'], self.block_size)
                    surf = self.icon_cache.get(cache_key)
                    if surf is None:
                        base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
                        surf = self.renderer.ResizeTexture(base_id, [self.block_size, self.block_size], False, save=False)
                        if surf:
                            self.icon_cache[cache_key] = surf
                    
                    if surf:
                        self.renderer.render([surf], [(pos_on_screen, self.groundy)])


class CookerManager:
    def __init__(self, world, inventory, player, ground, block_manager):
        self.world = world
        self.inventory = inventory
        self.player = player
        self.ground = ground
        self.block_manager = block_manager
        self.renderer = util.getRenderer()
        self.is_open = False
        self.gui_base = f"gui_{world.world_index + 1:03d}"
        self.hotbar_unselected_id = f"hotbar_{(world.world_index * 2) + 1:03d}"
        self.hotbar_selected_id = f"hotbar_{(world.world_index * 2) + 2:03d}"
        self.overlay_id = "cooker_overlay"
        w, h = util.getScreenDimensions()
        self.renderer.createSolidTexture(self.overlay_id, (0, 0, 0, 180), (w, h), 4)
        self.screen_w = w
        self.screen_h = h
        self.cached_dims = (0, 0)
        self.gui_scaled = None
        self.gui_x = 0
        self.gui_y = 0
        self.gui_w = 0
        self.gui_h = 0
        self.slot_size = 24
        self.icon_cache = {}
        
        self.hotbarSprite = SpriteAnimation(self.hotbar_unselected_id, (24, 24), 1)
        
        self.selected_recipe = -1
        self.hovered_slot = -1
        self.is_smelting = False
        self.smelt_start_time = 0
        self.smelt_duration = 5000  # 5 seconds in ms
        self.current_input_id = -1
        self.current_fuel_id = -1
        self.current_output_id = -1
        
        self.fuels = world.cookingRecipes.get("fuels", [])
        self.recipes = world.cookingRecipes.get("recipes", {})
        self.recipe_list = list(self.recipes.keys())
        
        self.recalcLayout()
    def updateWorld(self, world):
        self.world = world
        self.gui_base = f"gui_{world.world_index + 1:03d}"
        self.hotbar_unselected_id = f"hotbar_{(world.world_index * 2) + 1:03d}"
        self.hotbar_selected_id = f"hotbar_{(world.world_index * 2) + 2:03d}"
        self.hotbarSprite = SpriteAnimation(self.hotbar_unselected_id, (24, 24), 1)
    
    def recalcLayout(self):
        w, h = util.getScreenDimensions()
        self.cached_dims = (w, h)
        self.screen_w = w
        self.screen_h = h
        self.renderer.createSolidTexture(self.overlay_id, (0, 0, 0, 180), (w, h), 4, cache=True)
        gui_texture = self.renderer.getTexture(self.gui_base)
        if gui_texture:
            gui_w = int(w * 0.6)
            gui_h = int(h * 0.7)
            self.gui_w = gui_w
            self.gui_h = gui_h
            self.gui_scaled = pygame.transform.scale(gui_texture, (gui_w, gui_h))
            self.gui_x = (w - gui_w) // 2
            self.gui_y = (h - gui_h) // 2
            self.slot_size = max(24, int(min(gui_w, gui_h) * 0.08))
            self.icon_cache.clear()
    
    def toggle(self):
        self.is_open = not self.is_open
        if not self.is_open:
            self.selected_recipe = -1
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def get_nearby_cooker(self):
        player_x = self.player.x
        player_y = self.player.y
        interaction_range = 80
        
        for block in self.block_manager.placed_blocks:
            if block.get("type") == "cooker" and block.get("solid", True):
                block_x = block["x"]
                block_y = self.block_manager.groundy
                
                dist_x = abs(player_x - block_x)
                dist_y = abs(player_y - (block_y - 25))
                
                if dist_x < interaction_range and dist_y < interaction_range:
                    return block
        
        return None
    
    def get_first_available_fuel(self):
        for fuel_name in self.fuels:
            fuel_id = util.getItemID(fuel_name)
            if fuel_id >= 0 and self.inventory.items.get(fuel_id, 0) > 0:
                return fuel_id
        return -1
    
    def has_ingredient(self, item_name, quantity_needed=1):
        item_id = util.getItemID(item_name)
        return self.inventory.items.get(item_id, 0) >= quantity_needed
    
    def can_smelt(self, recipe_name):
        recipe_data = self.recipes.get(recipe_name)
        if not recipe_data:
            return False
        
        input_quantity = recipe_data[0][0]
        input_item = recipe_data[0][1]
        output_item = recipe_name
        output_quantity = recipe_data[0][2]
        
        if not self.has_ingredient(input_item, input_quantity):
            return False
        if self.get_first_available_fuel() < 0:
            return False
        
        output_id = util.getItemID(output_item)
        if not self.inventory.canAddItem(output_id):
            return False
        
        return True
    
    def start_smelting(self, recipe_idx):
        if recipe_idx < 0 or recipe_idx >= len(self.recipe_list):
            return
        
        recipe_name = self.recipe_list[recipe_idx]
        if not self.can_smelt(recipe_name):
            return
        
        recipe_data = self.recipes[recipe_name][0]
        input_quantity = recipe_data[0]
        input_item = recipe_data[1]
        output_item = recipe_name
        output_quantity = recipe_data[2]
        
        input_id = util.getItemID(input_item)
        fuel_id = self.get_first_available_fuel()
        output_id = util.getItemID(output_item)
        
        self.inventory.removeItem(input_id, input_quantity)
        self.inventory.removeItem(fuel_id, 1)
        
        self.is_smelting = True
        self.smelt_start_time = pygame.time.get_ticks()
        self.current_input_id = input_id
        self.current_fuel_id = fuel_id
        self.current_output_id = output_id
        self.current_output_amount = output_quantity
        
        # Update cooker block state to "cooking"
        self._update_all_cooker_states("cooking")
    
    def update_smelting(self):
        if not self.is_smelting:
            return
        
        elapsed = pygame.time.get_ticks() - self.smelt_start_time
        if elapsed >= self.smelt_duration:
            self.inventory.addItem(self.current_output_id, self.current_output_amount)
            self.is_smelting = False
            self.current_input_id = -1
            self.current_fuel_id = -1
            self.current_output_id = -1
            
            self._update_all_cooker_states("idle")
    
    def get_smelt_progress(self):
        if not self.is_smelting:
            return 0.0
        elapsed = pygame.time.get_ticks() - self.smelt_start_time
        return min(1.0, elapsed / self.smelt_duration)
    
    def _update_all_cooker_states(self, new_state):
        for block in self.block_manager.placed_blocks:
            if block.get("type") == "cooker" and not block.get("is_top", False):
                block["state"] = new_state
    
    def on_click(self, idx):
        if self.is_smelting:
            return
        if idx >= 0 and idx < len(self.recipe_list):
            self.selected_recipe = idx
            try:
                click_sound = pygame.mixer.Sound("assets/click.mp3")
                click_sound.set_volume(0.5)
                click_sound.play()
            except:
                pass
            if self.can_smelt(self.recipe_list[idx]):
                self.start_smelting(idx)
    
    def render(self):
        self.update_smelting()
        
        if not self.is_open:
            return
        
        dims = util.getScreenDimensions()
        if dims != self.cached_dims:
            self.recalcLayout()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered_slot = -1
        cursor_changed = False
        
        self.renderer.render([self.overlay_id], [(0, 0)])
        if self.gui_scaled:
            self.renderer.screen.blit(self.gui_scaled, (self.gui_x, self.gui_y))
            
            line_x = self.gui_x + self.gui_w // 3
            pygame.draw.line(self.renderer.screen, self.world.themeColor, 
                           (line_x, round(self.gui_y * 1.4)), (line_x, self.gui_y + self.gui_h), 4)
            
            title_text = "Cooker"
            title_font = pygame.font.SysFont("arial", 24)
            title_width = title_font.size(title_text)[0]
            title_x = self.gui_x + self.gui_w // 2 - title_width // 2 + self.gui_w // 6
            title_y = round(self.gui_y * 1.3) + int(self.gui_h * 0.02)
            text_color = util.getContrastColor(self.world.themeColor)
            self.renderer.createAndRenderText(
                "cooker_title", title_text, "arial", 24, text_color,
                (title_x, title_y), cache=False, silence=True
            )
            
            if self.is_smelting:
                progress = self.get_smelt_progress()
                bar_width = int(self.gui_w * 0.5)
                bar_height = 20
                bar_x = self.gui_x + (self.gui_w - bar_width) // 2
                bar_y = self.gui_y + 10
                
                pygame.draw.rect(self.renderer.screen, (100, 100, 100), 
                               (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.renderer.screen, (0, 255, 100), 
                               (bar_x, bar_y, int(bar_width * progress), bar_height))
                pygame.draw.rect(self.renderer.screen, (255, 255, 255), 
                               (bar_x, bar_y, bar_width, bar_height), 2)
                
                progress_text = f"Smelting... {int(progress * 100)}%"
                prog_font = pygame.font.SysFont("arial", 14)
                prog_width = prog_font.size(progress_text)[0]
                self.renderer.createAndRenderText(
                    "smelt_progress_text", progress_text, "arial", 14, text_color,
                    (bar_x + (bar_width - prog_width) // 2, bar_y + 3), cache=False, silence=True
                )
            
            icon_size = self.slot_size - 4
            left_third_center_x = self.gui_x + (self.gui_w // 3) // 2
            list_x = left_third_center_x - self.slot_size // 2
            list_y = self.gui_y + int(self.gui_h * 0.15)
            item_spacing = int(self.slot_size * 1.6)
            
            for idx, recipe_name in enumerate(self.recipe_list):
                slot_pos = (list_x, list_y + idx * item_spacing)
                self.hotbarSprite.doSpriteAnimation(1, slot_pos, (self.slot_size, self.slot_size))
                
                can_smelt = self.can_smelt(recipe_name)
                outline_color = (0, 255, 0) if can_smelt else (255, 0, 0)
                pygame.draw.rect(self.renderer.screen, outline_color, 
                               (slot_pos[0], slot_pos[1], self.slot_size, self.slot_size), 2)
                
                item_id = util.getItemID(recipe_name)
                icon_id = f"items_{item_id:03d}"
                cache_key = (item_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = icon_id if self.renderer.getTexture(icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(slot_pos[0] + 2, slot_pos[1] + 2)])
                
                if (slot_pos[0] <= mouse_x <= slot_pos[0] + self.slot_size and
                    slot_pos[1] <= mouse_y <= slot_pos[1] + self.slot_size):
                    self.hovered_slot = idx
                    if can_smelt and not self.is_smelting:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        cursor_changed = True
            
            if not cursor_changed:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            self.render_cooking_slots()
    
    def render_cooking_slots(self):
        right_section_start = self.gui_x + self.gui_w // 3 + 20
        right_section_width = self.gui_w - self.gui_w // 3 - 40
        center_x = right_section_start + right_section_width // 2
        
        slot_size = max(40, int(min(self.gui_w, self.gui_h) * 0.12))
        icon_size = slot_size - 8
        slot_spacing = slot_size + 20
        
        top_y = self.gui_y + int(self.gui_h * 0.25)
        ingredient_x = center_x - slot_size - 20
        fuel_x = center_x + 20
        
        output_y = top_y + slot_size + 60
        output_x = center_x - slot_size // 2
        
        pygame.draw.rect(self.renderer.screen, (80, 80, 80), 
                        (ingredient_x, top_y, slot_size, slot_size))
        pygame.draw.rect(self.renderer.screen, (150, 150, 150), 
                        (ingredient_x, top_y, slot_size, slot_size), 2)
        
        # Draw fuel slot
        pygame.draw.rect(self.renderer.screen, (80, 60, 40), 
                        (fuel_x, top_y, slot_size, slot_size))
        pygame.draw.rect(self.renderer.screen, (200, 150, 100), 
                        (fuel_x, top_y, slot_size, slot_size), 2)
        
        # Draw output slot
        pygame.draw.rect(self.renderer.screen, (60, 80, 60), 
                        (output_x, output_y, slot_size, slot_size))
        pygame.draw.rect(self.renderer.screen, (100, 200, 100), 
                        (output_x, output_y, slot_size, slot_size), 2)
        
        font_size = 12
        font = pygame.font.SysFont("arial", font_size)
        label_color = util.getContrastColor(self.world.themeColor)
        
        ing_label = "Ingredient"
        ing_width = font.size(ing_label)[0]
        self.renderer.createAndRenderText(
            "ing_label", ing_label, "arial", font_size, label_color,
            (ingredient_x + (slot_size - ing_width) // 2, top_y - 18), cache=False, silence=True
        )
        
        fuel_label = "Fuel"
        fuel_width = font.size(fuel_label)[0]
        self.renderer.createAndRenderText(
            "fuel_label", fuel_label, "arial", font_size, label_color,
            (fuel_x + (slot_size - fuel_width) // 2, top_y - 18), cache=False, silence=True
        )
        
        output_label = "Output"
        output_width = font.size(output_label)[0]
        self.renderer.createAndRenderText(
            "output_label", output_label, "arial", font_size, label_color,
            (output_x + (slot_size - output_width) // 2, output_y - 18), cache=False, silence=True
        )
        
        if self.is_smelting:
            if self.current_input_id >= 0:
                input_icon_id = f"items_{self.current_input_id:03d}"
                cache_key = (self.current_input_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = input_icon_id if self.renderer.getTexture(input_icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(ingredient_x + 4, top_y + 4)])
            
            if self.current_fuel_id >= 0:
                fuel_icon_id = f"items_{self.current_fuel_id:03d}"
                cache_key = (self.current_fuel_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = fuel_icon_id if self.renderer.getTexture(fuel_icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(fuel_x + 4, top_y + 4)])
            
            arrow_y = top_y + slot_size + 20
            arrow_text = "↓"
            arrow_font = pygame.font.SysFont("arial", 24)
            arrow_width = arrow_font.size(arrow_text)[0]
            self.renderer.createAndRenderText(
                "smelt_arrow", arrow_text, "arial", 24, label_color,
                (center_x - arrow_width // 2, arrow_y), cache=False, silence=True
            )
            
            if self.current_output_id >= 0:
                output_icon_id = f"items_{self.current_output_id:03d}"
                cache_key = (self.current_output_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = output_icon_id if self.renderer.getTexture(output_icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    progress = self.get_smelt_progress()
                    if progress < 1.0:
                        surf = surf.copy()
                        surf.set_alpha(int(128 + 127 * progress))
                    self.renderer.render([surf], [(output_x + 4, output_y + 4)])
        
        elif self.hovered_slot >= 0 and self.hovered_slot < len(self.recipe_list) and not self.is_smelting:
            recipe_name = self.recipe_list[self.hovered_slot]
            recipe_data = self.recipes.get(recipe_name)
            if recipe_data:
                input_quantity = recipe_data[0][0]
                input_item = recipe_data[0][1]
                output_quantity = recipe_data[0][2]
                output_item = recipe_name
                
                input_id = util.getItemID(input_item)
                current_input_amount = self.inventory.items.get(input_id, 0)
                has_enough_input = current_input_amount >= input_quantity
                input_color = (0, 255, 0) if has_enough_input else (255, 0, 0)
                
                input_icon_id = f"items_{input_id:03d}"
                cache_key = (input_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = input_icon_id if self.renderer.getTexture(input_icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(ingredient_x + 4, top_y + 4)])
                
                font_size_small = max(8, icon_size // 4)
                font_small = pygame.font.SysFont("arial", font_size_small)
                input_amt_text = f"{current_input_amount}/{input_quantity}"
                amt_width = font_small.size(input_amt_text)[0]
                self.renderer.createAndRenderText(
                    f"preview_input_amt_{self.hovered_slot}", input_amt_text, "arial", font_size_small, input_color,
                    (ingredient_x + (slot_size - amt_width) // 2, top_y + slot_size - 15), cache=False, silence=True
                )
                
                has_fuel = self.get_first_available_fuel() >= 0
                fuel_color = (0, 255, 0) if has_fuel else (255, 0, 0)
                
                fuel_name = self.fuels[0] if self.fuels else "Fuel"
                if has_fuel:
                    fuel_id = self.get_first_available_fuel()
                    fuel_name = util.getItemName(fuel_id)
                
                fuel_id_num = util.getItemID(fuel_name)
                fuel_icon_id = f"items_{fuel_id_num:03d}"
                cache_key = (fuel_id_num, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = fuel_icon_id if self.renderer.getTexture(fuel_icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(fuel_x + 4, top_y + 4)])
                
                fuel_amt_text = "1/1" if has_fuel else "0/1"
                amt_width = font_small.size(fuel_amt_text)[0]
                self.renderer.createAndRenderText(
                    f"preview_fuel_amt_{self.hovered_slot}", fuel_amt_text, "arial", font_size_small, fuel_color,
                    (fuel_x + (slot_size - amt_width) // 2, top_y + slot_size - 15), cache=False, silence=True
                )
                
                output_id = util.getItemID(output_item)
                can_add_output = self.inventory.canAddItem(output_id)
                output_color = (0, 255, 0) if can_add_output else (255, 0, 0)
                
                output_icon_id = f"items_{output_id:03d}"
                cache_key = (output_id, icon_size)
                surf = self.icon_cache.get(cache_key)
                if surf is None:
                    base_id = output_icon_id if self.renderer.getTexture(output_icon_id) else "placeholder-item"
                    surf = self.renderer.ResizeTexture(base_id, [icon_size, icon_size], False, save=False)
                    if surf:
                        self.icon_cache[cache_key] = surf
                if surf:
                    self.renderer.render([surf], [(output_x + 4, output_y + 4)])
                
                output_amt_text = f"0/{output_quantity}"
                amt_width = font_small.size(output_amt_text)[0]
                self.renderer.createAndRenderText(
                    f"preview_output_amt_{self.hovered_slot}", output_amt_text, "arial", font_size_small, output_color,
                    (output_x + (slot_size - amt_width) // 2, output_y + slot_size - 15), cache=False, silence=True
                )
    
