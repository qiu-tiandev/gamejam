import pygame
from renderer import Renderer
from animations import SpriteAnimation
import util
import console
import random
class Player():
    def __init__(self,world,ground):
        self.renderer = util.getRenderer()
        self.renderer.createSolidTexture("Player", (0,0,0), (50,50), 1000, True)
        self.ground = ground 
        self.x = 10
        self.y = self.ground.height-50
        self.dt = None
        self.speed = 2
        self.multiplier = 50
        self.directions = {pygame.K_a: (-1,0),pygame.K_d:(1,0)}
        self.gravity = world.gravity
        self.jump_duration = 0.4
        self.peak_jump_duration = 0.05
        self.jumping = False
        self.jumping_start = None 
        self.jump_power = 4
        self.lasergun_energy = 100
        self.laser_cooldown = 0
        self.laser_cooldown_time = 0.7
        self.active_lasers = []
        self.block_manager = None
        self.animation_frames = {}
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Time per frame in seconds
        self.is_moving = False
        self.facing_direction = 1  # 1 = right, -1 = left
        self._load_player_sprites()
        
        self.max_health = 100
        self.health = 100
        self.last_hit_time = 0
        self.hit_cooldown = 2
        self.regen_delay = 10
        self.regen_interval = 3
        self.last_regen_time = 0
        self.monster_hit_damage = (10, 15)
        self.world = world
        self.max_hunger_time = 20  # Base hunger time in seconds
        self.hunger_timer = self.max_hunger_time  # Countdown from max_hunger_time seconds
        self.last_food_time = pygame.time.get_ticks() / 1000  # Last time player ate
        self.hunger_damage_rate = self.max_hunger_time / 4  # Damage scales with hunger time
        self.last_hunger_damage_time = 0
        self.eat_cooldown = 1  # 1 second cooldown between eating
        self.last_eat_time = 0  # Last time player ate (for cooldown)
        self.damage_boost = 0  # Current damage boost percentage
        self.total_pause_time = 0  # Total time spent paused
    def detectinput(self):
        keys = pygame.key.get_pressed()
        self.dt = util.getDeltaTime()
        self.is_moving = False
        
        if keys:
            for key, direction in self.directions.items():
                if keys[key]:
                    if self.block_manager and self.block_manager.check_collision(self.x, self.y, direction[0]):
                        continue 
                    self.x += direction[0] * self.speed * self.dt * self.multiplier
                    self.y += direction[1] * self.speed * self.dt * self.multiplier
                    self.is_moving = True
                    if direction[0] != 0:
                        self.facing_direction = direction[0]
            if keys[pygame.K_SPACE]:
                on_block = self.block_manager and self.block_manager.get_block_under_player(self.x, self.y)
                if not self.jumping and (self.ground.isTouchingGround(self.y) or on_block):
                    self.jumping = True
                    self.jumping_start = pygame.time.get_ticks()
    def move(self, is_paused=False):
        if is_paused:
            return
        self.detectinput()
        if self.jumping:
            elapsed = pygame.time.get_ticks() - self.jumping_start
            if elapsed >= (self.jump_duration+self.peak_jump_duration) *1000:
                self.jumping = False
                self.jumping_start = None
            if elapsed < self.jump_duration*1000:
                self.y -=self.jump_power*self.dt*self.multiplier
        
        # Check if standing on a block
        on_block = self.block_manager and self.block_manager.get_block_under_player(self.x, self.y)
        
        if not self.ground.isTouchingGround(self.y) and not self.jumping:
            if on_block:
                # Land on top of block
                block_top = self.block_manager.groundy
                self.y = block_top - 50  # Player is 50px tall
            else:
                self.y += self.gravity * self.dt
        elif not self.jumping and not on_block:
            screen_dims = util.getScreenDimensions()
            self.y = screen_dims[1]-self.ground.height - 50
        
        # Update animation and render player
        self._update_animation()
        # self._render_player()  # Moved to separate render call

    def _load_player_sprites(self):
        # Load player spritesheet (20x32 sprites, 11 frames total)
        player_sprite_anim = SpriteAnimation("player_spritesheet", (20, 32), 11)
        player_sprite_anim.save_frames("player")  # Creates player_001 to player_011
        
        util.getRenderer().cleanUp(["player_spritesheet"])
        
        # Calculate scaled width to maintain aspect ratio (20x32 -> ?x50)
        # Original aspect ratio: 20/32 = 0.625
        scaled_width = int(50 * 0.625)  # 31 pixels wide
        
        # Store frame ranges for different animations
        self.animation_frames = {
            "moving": list(range(1, 5)),     # Frames 1-4 for moving
            "ascending": [5, 6],              # Frames 5-6 for ascending
            "peak": [7],                      # Frame 7 for peak
            "descending": [8, 9, 10]         # Frames 8-10 for descending/landing
        }
        
        # Resize all frames to proper size
        for i in range(1, 12):
            frame_id = f"player_{i:03d}"
            if self.renderer.getTexture(frame_id):
                self.renderer.ResizeTexture(frame_id, [scaled_width, 50], False, save=True)
    
    def _update_animation(self):
        self.animation_timer += self.dt if self.dt else 0
        
        # Determine current animation state
        if self.jumping:
            elapsed = pygame.time.get_ticks() - self.jumping_start
            if elapsed < self.jump_duration * 1000 * 0.5:  # First half - ascending
                frames = self.animation_frames["ascending"]
                frame_index = min(int((elapsed / (self.jump_duration * 500)) * len(frames)), len(frames) - 1)
                self.current_frame = frames[frame_index]
            elif elapsed < self.jump_duration * 1000:  # Peak
                self.current_frame = self.animation_frames["peak"][0]
            else:  # Descending
                frames = self.animation_frames["descending"]
                desc_time = elapsed - self.jump_duration * 1000
                frame_index = min(int((desc_time / (self.peak_jump_duration * 1000)) * len(frames)), len(frames) - 1)
                self.current_frame = frames[frame_index]
        elif self.is_moving:
            # Cycle through moving frames
            if self.animation_timer >= self.animation_speed:
                frames = self.animation_frames["moving"]
                frame_idx = (frames.index(self.current_frame) + 1) % len(frames) if self.current_frame in frames else 0
                self.current_frame = frames[frame_idx]
                self.animation_timer = 0
        else:
            # Idle - use first moving frame
            self.current_frame = self.animation_frames["moving"][0]
            self.animation_timer = 0
    
    def _render_player(self):
        screen_w = util.getScreenDimensions()[0]
        frame_id = f"player_{self.current_frame:03d}"
        
        # Get the texture and flip if facing left
        texture = self.renderer.getTexture(frame_id)
        if texture:
            if self.facing_direction == -1:
                # Flip horizontally for left-facing
                flipped = pygame.transform.flip(texture, True, False)
                self.renderer.render_surface(flipped, (screen_w // 2 - 15, self.y))
            else:
                self.renderer.render([frame_id], [(screen_w // 2 - 15, self.y)])
        else:
            # Fallback to solid texture
            self.renderer.render(["Player"], [(screen_w // 2 - 25, self.y)])

    def render(self):
        self._render_player()

    def update(self):
        self.detectinput()
    
    def updateLasers(self, dt, is_paused=False):
        if is_paused:
            return
        if self.laser_cooldown > 0:
            self.laser_cooldown -= dt
        
        screen_w, screen_h = util.getScreenDimensions()
        ground_y = screen_h - self.ground.height
        lasers_to_remove = []
        
        for i, laser in enumerate(self.active_lasers):
            laser['x'] += laser['dx'] * dt * 500
            laser['y'] += laser['dy'] * dt * 500
            if laser['y'] >= ground_y or laser['x'] < 0 or laser['x'] > screen_w or laser['y'] < 0:
                lasers_to_remove.append(i)
        for i in reversed(lasers_to_remove):
            self.active_lasers.pop(i)

    def refillLaserEnergy(self, inventory):
        items_list = list(inventory.items.items())
        if not items_list or inventory.currentSlot - 1 >= len(items_list):
            return
        sel_id, sel_amt = items_list[inventory.currentSlot - 1]
        if sel_id != util.getItemID("laser gun") or sel_amt <= 0:
            return
        if self.lasergun_energy >= 100:
            return
        battery_id = util.getItemID("battery")
        fuel_id = util.getItemID("liquid fuel")
        if battery_id != -1 and inventory.items.get(battery_id, 0) > 0:
            inventory.removeItem(battery_id, 1)
            self.lasergun_energy = min(100, self.lasergun_energy + 25)
            return
        if fuel_id != -1 and inventory.items.get(fuel_id, 0) > 0:
            inventory.removeItem(fuel_id, 1)
            self.lasergun_energy = min(100, self.lasergun_energy + 15)
            return
    
    def renderLasers(self):
        for laser in self.active_lasers:
            self.renderer.createAndRenderSolidTexture(
                "laser_beam", (255, 0, 0), (10, 10), (int(laser['x']), int(laser['y'])), 4, cache=False
            )
    
    def shootLaser(self, mouse_pos, inventory, num_shots=1):
        if self.laser_cooldown > 0:
            return
        
        items_list = list(inventory.items.items())
        if not items_list or inventory.currentSlot - 1 >= len(items_list):
            return
        
        item_id, amount = items_list[inventory.currentSlot - 1]
        if item_id != util.getItemID("laser gun") or amount <= 0:
            return
        
        screen_w = util.getScreenDimensions()[0]
        player_center_x = screen_w // 2
        player_center_y = self.y + 35
        
        dx = mouse_pos[0] - player_center_x
        dy = mouse_pos[1] - player_center_y
        distance = (dx**2 + dy**2) ** 0.5
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        req_energy = random.randint(2, 10)
        total_energy = req_energy * 2 if num_shots > 1 else req_energy
        
        if self.lasergun_energy < total_energy:
            return
        
        for _ in range(num_shots):
            self.active_lasers.append({
                'x': float(player_center_x),
                'y': float(player_center_y),
                'dx': dx,
                'dy': dy
            })
        
        # Play laser sound effect
        try:
            laser_sound = pygame.mixer.Sound("assets/laser_gun.mp3")
            laser_sound.set_volume(0.5)  # 50% volume
            laser_sound.play()
        except:
            pass  # Silently fail if sound not found
        
        self.lasergun_energy -= total_energy
        self.laser_cooldown = self.laser_cooldown_time
    
    def take_damage(self, amount=None):
        raw_time = pygame.time.get_ticks() / 1000
        current_time = raw_time - self.total_pause_time
        
        if current_time - self.last_hit_time < self.hit_cooldown:
            return False
        
        if amount is None:
            amount = random.randint(self.monster_hit_damage[0], self.monster_hit_damage[1])
        
        self.health = max(0, self.health - amount)
        self.last_hit_time = current_time
        self.last_regen_time = current_time  # Reset regen timer on hit
        return True
    
    def update_health(self, is_paused=False):
        current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        
        if is_paused:
            if not hasattr(self, 'pause_start'):
                self.pause_start = current_time
            return
        else:
            if hasattr(self, 'pause_start'):
                self.total_pause_time += current_time - self.pause_start
                del self.pause_start
        
        adjusted_time = current_time - self.total_pause_time
        
        # Check if enough time has passed since last hit to start regenerating
        if adjusted_time - self.last_hit_time >= self.regen_delay:
            # Calculate hunger percentage
            hunger_percent = (self.hunger_timer / self.max_hunger_time) * 100
            
            # Adjust regen interval based on hunger level
            if hunger_percent > 75:
                # Much faster healing when well fed (>75% food)
                current_regen_interval = self.regen_interval * 0.3  # 3x faster (0.9 seconds instead of 3)
            else:
                current_regen_interval = self.regen_interval
            
            # Check if enough time has passed since last regen
            if adjusted_time - self.last_regen_time >= current_regen_interval:
                if self.health < self.max_health:
                    self.health = min(self.max_health, self.health + 5)  # Heal 5 HP per tick
                    self.last_regen_time = adjusted_time
    
    def render_healthbar(self):
        w, h = util.getScreenDimensions()
        bar_width = 200
        bar_height = 20
        bar_x = w - bar_width - 10
        bar_y = 10
        
        # Draw background (dark gray)
        self.renderer.createAndRenderSolidTexture("player_health_bg", (100, 100, 100), (bar_width, bar_height), (bar_x, bar_y), 4, cache=False)
        
        # Calculate health percentage
        health_percent = self.health / self.max_health
        health_width = int(health_percent * bar_width)
        
        # Change color based on health
        if health_percent > 0.5:
            # Green when above 50%
            color = (0, 255, 0)
        elif health_percent > 0.25:
            # Yellow when between 25-50%
            color = (255, 255, 0)
        else:
            # Red when below 25%
            color = (255, 0, 0)
        
        # Draw health bar with dynamic color
        if health_width > 0:
            self.renderer.createAndRenderSolidTexture("player_health_fg", color, (health_width, bar_height), (bar_x, bar_y), 4, cache=False)
        
        # Draw text with theme-based color
        health_text = f"{int(self.health)}/{int(self.max_health)}"
        text_color = util.getContrastColor(self.world.themeColor)
        self.renderer.createAndRenderText("player_health_text", health_text, "Arial", 14, text_color, (bar_x + 5, bar_y + 3), cache=False, silence=True)
    
    def update_hunger(self, is_paused=False):
        current_time = pygame.time.get_ticks() / 1000
        
        if is_paused:
            if not hasattr(self, 'pause_start'):
                self.pause_start = current_time
            return
        else:
            if hasattr(self, 'pause_start'):
                self.total_pause_time += current_time - self.pause_start
                del self.pause_start
        
        adjusted_time = current_time - self.total_pause_time
        time_since_food = adjusted_time - self.last_food_time
        
        # Update hunger timer (counts down from max_hunger_time)
        self.hunger_timer = max(0, self.max_hunger_time - time_since_food)
        
        # Calculate hunger percentage (0-100%)
        hunger_percent = (self.hunger_timer / self.max_hunger_time) * 100
        
        # Damage boost is proportionate to hunger level (0% at 0 hunger, 50% at 100% hunger)
        # Only apply boost above 75% hunger for display purposes, but scale proportionally
        if hunger_percent >= 75:
            # Scale from 0% at 75% hunger to 50% at 100% hunger
            self.damage_boost = ((hunger_percent - 75) / 25) * 50
        else:
            self.damage_boost = 0  # No boost below 75%
        
        # Apply starvation damage when timer reaches 0
        if self.hunger_timer <= 0:
            # Apply damage at rate scaled with hunger time (20 per 4 seconds base)
            damage_interval = 4
            if adjusted_time - self.last_hunger_damage_time >= damage_interval:
                self.health = max(0, self.health - 20)
                self.last_hunger_damage_time = adjusted_time
    
    def eat_food(self, inventory):
        raw_time = pygame.time.get_ticks() / 1000
        current_time = raw_time - self.total_pause_time  # Adjust for pause time
        
        # Check eat cooldown
        if current_time - self.last_eat_time < self.eat_cooldown:
            return False
        
        items_list = list(inventory.items.items())
        if not items_list or inventory.currentSlot - 1 >= len(items_list):
            return False
        
        selected_item_id, amount = items_list[inventory.currentSlot - 1]
        if amount <= 0:
            return False
        
        # Get item name
        item_name = util.getItemName(selected_item_id)
        
        # Check if item is edible
        if item_name not in self.world.eatables:
            return False
        
        # Remove item from inventory
        inventory.removeItem(selected_item_id, 1)
        
        # Reset hunger timer
        self.last_food_time = current_time
        self.last_eat_time = current_time  # Update eat cooldown
        self.hunger_timer = self.max_hunger_time
        self.last_hunger_damage_time = 0
        
        return True
    
    def render_hunger_bar(self):
        w, h = util.getScreenDimensions()
        bar_width = 200
        bar_height = 20
        bar_x = w - bar_width - 10
        bar_y = 35  # Below health bar
        
        # Draw background (dark gray)
        self.renderer.createAndRenderSolidTexture("player_hunger_bg", (100, 100, 100), (bar_width, bar_height), (bar_x, bar_y), 4, cache=False)
        
        # Draw hunger timer bar (fills as time passes, depletes as hunger increases)
        hunger_percent = self.hunger_timer / self.max_hunger_time
        hunger_width = int(hunger_percent * bar_width)
        
        # Change color based on hunger level
        if hunger_percent > 0.5:
            # Green when well fed
            color = (0, 255, 0)
        elif hunger_percent > 0.25:
            # Yellow when getting hungry
            color = (255, 255, 0)
        else:
            # Red when starving
            color = (255, 0, 0)
        
        # Draw hunger bar
        if hunger_width > 0:
            self.renderer.createAndRenderSolidTexture("player_hunger_fg", color, (hunger_width, bar_height), (bar_x, bar_y), 4, cache=False)
        
        # Draw text with theme-based color (1 decimal place)
        hunger_text = f"Food: {self.hunger_timer:.1f}s"
        text_color = util.getContrastColor(self.world.themeColor)
        self.renderer.createAndRenderText("player_hunger_text", hunger_text, "Arial", 14, text_color, (bar_x + 5, bar_y + 3), cache=False, silence=True)
        
        # Display damage boost below hunger bar if active (show with 1 decimal place)
        if self.damage_boost > 0:
            boost_text = f"Damage Boost: +{self.damage_boost:.1f}%"
            boost_y = bar_y + bar_height + 5
            # Use gold/yellow color for boost indicator
            boost_color = (255, 215, 0)
            self.renderer.createAndRenderText("damage_boost_text", boost_text, "Arial", 12, boost_color, (bar_x, boost_y), cache=False, silence=True)
    
    def use_clock(self, inventory):
        clock_id = util.getItemID("Clock")
        if clock_id < 0:
            return False
        
        # Check if player has a clock
        if inventory.items.get(clock_id, 0) <= 0:
            return False
        
        # Extend max hunger time by 10%
        self.max_hunger_time *= 1.1
        
        # Reset hunger timer to the new maximum
        self.hunger_timer = self.max_hunger_time
        self.last_food_time = pygame.time.get_ticks() / 1000
        
        # Remove one clock from inventory
        inventory.removeItem(clock_id, 1)
        
        return True
    
    def use_holy_book(self, inventory):
        holy_book_id = util.getItemID("Holy Book")
        if holy_book_id < 0:
            return False
        
        # Check if player has a holy book
        if inventory.items.get(holy_book_id, 0) <= 0:
            return False
        
        # Increase max health by 10
        self.max_health += 10
        
        # Restore current health to new maximum
        self.health = self.max_health
        
        # Remove one holy book from inventory
        inventory.removeItem(holy_book_id, 1)
        
        return True
