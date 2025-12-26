import util
import pygame
import random
class Ground:
    def __init__(self,height:int,id:str):
        self.height = height
        self.renderer = util.getRenderer()
        self.id = id
        self.renderer.ResizeTexture(self.id,[None,height],True,True)
        self.texture = self.renderer.getTexture(self.id)
        self.texture_width = self.texture.get_width()
        self._cached_dims = (0, 0)
        self._screenx = 0
        self._screeny = 0
        self._updateDims()
    def _updateDims(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self._screenx = w
        self._screeny = h
    def renderGround(self,player):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self._updateDims()
        offset = -(player.x % self.texture_width)
        screenx = self._screenx
        screeny = self._screeny
        x = offset - self.texture_width if offset > 0 else offset
        while x < screenx:
            src = max(0, -x)
            dst = max(0, x)
            visible_width = min(self.texture_width - src, screenx - dst)
            cropped = self.texture.subsurface(pygame.Rect(src, 0, visible_width, self.height))
            self.renderer.render_surface(cropped, (dst, screeny - self.height))
            x += self.texture_width

    def isTouchingGround(self,y):
        return y >= util.getScreenDimensions()[1]-self.height-50 #entity size
def isOnScreen(x,playerx):
    screenx = util.getScreenDimensions()[0]
    pos_on_screen = x - playerx + (screenx)//2
    if -100 <= pos_on_screen <= screenx + 100:
        return pos_on_screen
class ItemEntityManager:
    def __init__(self,player,inventory,ground):
        self.player = player
        self.items:list[dict] = []
        self.inventoryManager = inventory
        self.ground = ground
        self.renderer = util.getRenderer()
        self._cached_dims = (0, 0)
        self._scale_factor = 1.0
        self.groundy = 0
        self.updateGroundY()
    def updateGroundY(self):
        w, h = util.getScreenDimensions()
        old_groundy = self.groundy
        self._cached_dims = (w, h)
        self.groundy = h - self.ground.height - 32
        self._scale_factor = max(0.5, h // 720)
        if old_groundy != 0 and old_groundy != self.groundy:
            for item in self.items:
                item["pos"] = (item["pos"][0], self.groundy)
    
    def spawnRandomItems(self):
        if random.random() < 0.00055:
            mysterious_meat_id = util.getItemID("mysterious meat")
            if mysterious_meat_id >= 0:
                screen_width = util.getScreenDimensions()[0]
                spawn_x = self.player.x + random.randint(-screen_width //2, screen_width // 2)
                self.addItemEntities(mysterious_meat_id, 1, (spawn_x, self.groundy))
    def addItemEntities(self,id:int,amount:int,pos:tuple[int,int]):
        now = pygame.time.get_ticks()
        count = min(amount, 10)
        base_x, _ = pos
        for i in range(count):
            ox = random.randint(-40, 40)
            self.items.append({"id": id, "amount": 1, "pos": (base_x + ox, self.groundy), "spawn": now})
        remaining = amount - count
        if remaining > 0:
            self.items.append({"id": id, "amount": remaining, "pos": (base_x, self.groundy), "spawn": now})
    def pickUpItems(self):
        New = []
        now = pygame.time.get_ticks()
        for i in self.items:
            itemX,itemY = i["pos"]
            if now - i["spawn"] < 2000:
                New.append(i)
                continue
            if self.player.x + 30 > itemX and self.player.x < itemX + 30 and self.player.y+30 > self.groundy and self.player.y < self.groundy + 30:
                if self.inventoryManager.addItem(i["id"], i["amount"]):
                    continue  # Item was added, don't keep it on ground
            New.append(i)
        self.items = New
    def RenderItemEntities(self):
        if not self.items:
            return
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.updateGroundY()
        render_ids = []
        render_pos = []
        scale_factor = self._scale_factor
        player_x = self.player.x
        for i in self.items:
            itemX, itemY = i["pos"]
            pos = isOnScreen(itemX, player_x)
            if pos is not None:
                tex_id = f"items_{i['id']:03d}"
                if self.renderer.getTexture(tex_id) is None:
                    tex_id = "placeholder-item"
                render_ids.append(tex_id)
                render_pos.append((int(pos), int(itemY)))
        if render_ids:
            self.renderer.render(render_ids, render_pos)
class ChestManager:
    def __init__(self,player,ground,world,id:str,itemManager:ItemEntityManager):
        self.id = id
        self.renderer= util.getRenderer()
        self.player = player
        self.ground = ground
        self.spawnChance = 1/1000
        self.cooldown_duration = 35000
        self.last_spawn_time = 0
        self.chests = {0:200}  #id: chestpos| starter chest will gen x=200
        self.lastChestPos = None
        self.minDist = 500
        self.loot =  world.chestLoot
        self.drop_chances = {
            "Common": 1.0,
            "Uncommon": 0.5,
            "Rare": 0.3
        }
        self.currentId = 1
        self.itemManager = itemManager
        self._cached_dims = (0, 0)
        self.groundy = 0
        self.screenx = 0
        self.updateGroundY()

    def is_far_enough(self, pos: int) -> bool:
        for existing in self.chests.values():
            if abs(pos - existing) < self.minDist:
                return False
        if self.lastChestPos is not None and abs(pos - self.lastChestPos) < self.minDist:
            return False
        return True
    def updateGroundY(self):
        w, h = util.getScreenDimensions()
        self._cached_dims = (w, h)
        self.groundy = h - self.ground.height - 50
        self.screenx = w
    def lootChest(self):
        playerx = self.player.x
        playery = self.player.y
        if pygame.key.get_pressed()[pygame.K_s]:
            for n,i in self.chests.items():
                if playerx + 60 > i and playerx < i +60 and playery+60 > self.groundy and playery < self.groundy + 60:
                    for name, loot_data in self.loot.items():
                        rarity = loot_data["rarity"]
                        drop_chance = self.drop_chances.get(rarity, 1.0)
                        if random.random() < drop_chance:
                            item_id = util.getItemID(name)
                            mn = loot_data["min"]
                            mx = loot_data["max"]
                            amt = random.randint(mn, mx)
                            drop_x = i + random.randint(-20, 20)
                            self.itemManager.addItemEntities(item_id, amt, (drop_x, self.groundy))
                    del self.chests[n]
                    break
    def generateAndRenderChest(self):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.updateGroundY()
        self.lootChest()
        current_time = pygame.time.get_ticks()
        time_since_last_spawn = current_time - self.last_spawn_time
        if random.random() < self.spawnChance and time_since_last_spawn >= self.cooldown_duration:
            chestPos = self.player.x + random.randint(self.screenx//2+50,self.screenx//2+300)
            if self.is_far_enough(chestPos):
                self.chests[self.currentId] = chestPos
                self.currentId+=1
                self.lastChestPos = chestPos
                self.last_spawn_time = current_time
        render_pos = []
        for i in self.chests.values():
            pos_on_screen = isOnScreen(i,self.player.x)
            if pos_on_screen:
                render_pos.append((pos_on_screen,self.groundy))
        if render_pos:self.renderer.render([self.id]*len(render_pos),render_pos)

class MonsterManager:
    def __init__(self, player, ground, block_manager=None, itemManager=None, loot_table=None, world=None):
        self.player = player
        self.ground = ground
        self.block_manager = block_manager
        self.itemManager = itemManager
        self.world = world
        self.renderer = util.getRenderer()
        self.base_loot_table = {
            "monster flesh": {"min": 2, "max": 3, "rarity": "Common"},
            "bones": {"min": 1, "max": 3, "rarity": "Common"},
            "liquid fuel": {"min": 1, "max": 3, "rarity": "Uncommon"},
            "mysterious powder": {"min": 1, "max": 3, "rarity": "Uncommon"},
            "metal scrap": {"min": 1, "max": 2, "rarity": "Rare"}
        }
        self.loot_table = self.base_loot_table.copy()
        if world and world.world_index >= 1:
            self.loot_table["Half-eaten Brain"] = {"min": 1, "max": 1, "rarity": "Uncommon"}
        if loot_table is not None:
            self.loot_table.update(loot_table)
        self.drop_chances = {
            "Common": 1.0,    # 100%
            "Uncommon": 0.5,  # 50%
            "Rare": 0.3       # 30%
        }
        self.monsters = []  # No initial monster
        self.monster_size = 40
        self.zombie_frame_width = 16
        self.zombie_frame_height = 29
        self.spawnChance = 1/1900  # Slightly higher than chests (1/2500)
        self.cooldown = 180
        self.currentId = 0
        self._cached_dims = (0, 0)
        self.groundy = 0
        self.screenx = 0
        self.brain_contact_duration = 60000  # 60 seconds in ms
        self.total_pause_time = 0  # Total time spent paused
        self.animation_frame = 0  # Current animation frame
        
        # Create health bar textures
        self.renderer.createSolidTexture("health_bar_bg", (100, 100, 100), (self.monster_size, 6), 4, True)
        self.renderer.createSolidTexture("health_bar_fg", (0, 255, 0), (self.monster_size, 6), 4, True)
        
        self.updateGroundY()
    
    def updateGroundY(self):
        w, h = util.getScreenDimensions()
        old_groundy = self.groundy
        self._cached_dims = (w, h)
        self.groundy = h - self.ground.height
        self.screenx = w
        # Recalculate monster y positions if screen was resized
        if old_groundy != 0 and old_groundy != self.groundy:
            for monster in self.monsters:
                if monster["y"] >= old_groundy - 5:  # If monster was on ground
                    monster["y"] = self.groundy
    
    def spawnMonster(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        
        # Check if there are any brain blocks for increased spawn rate
        brain_boost = 1.0
        if self.block_manager:
            brain_blocks = [b for b in self.block_manager.placed_blocks if b.get("type") == "half-eaten brain"]
            if brain_blocks:
                brain_boost = 4.0  # 4x spawn rate near brains
        
        # Adjust spawn chance based on brain presence
        adjusted_spawn_chance = self.spawnChance * brain_boost
        
        if random.random() < adjusted_spawn_chance:
            # Spawn monster off-screen (either left or right)
            side = random.choice([-1, 1])
            spawn_x = self.player.x + side * (self.screenx // 2 + random.randint(100, 300))
            
            self.monsters.append({
                "id": self.currentId,
                "x": spawn_x,
                "y": self.groundy,
                "speed": 1.2,  # Slower than player (player speed is 2)
                "direction": 1 if spawn_x > self.player.x else -1,  # Face towards player initially
                "jumping": False,
                "jump_start": None,
                "jump_duration": 0.7,  
                "jump_power": 4,  
                "health": 100,
                "max_health": 100,
                "vx": 0,  # Horizontal velocity during jump
                "brain_target": None,
            })
            self.currentId += 1
            self.cooldown = 180
            
            # Play zombie spawn sound
            try:
                zombie_sound = pygame.mixer.Sound("assets/zombie.mp3")
                zombie_sound.set_volume(0.5)  # 50% volume
                zombie_sound.play()
            except:
                pass  # Silently fail if sound not found
    
    def updateMonsters(self, is_focused=True):
        dims = util.getScreenDimensions()
        if dims != self._cached_dims:
            self.updateGroundY()
        
        dt = util.getDeltaTime()
        adjusted_time = pygame.time.get_ticks() / 1000 - self.total_pause_time
        multiplier = 50
        player_x = self.player.x
        
        # Get all brain blocks if available
        brain_blocks = []
        if self.block_manager:
            brain_blocks = [b for b in self.block_manager.placed_blocks if b.get("type") == "half-eaten brain"]
        
        # Initialize contact timers for brains if not already present
        for brain in brain_blocks:
            if "contact_start" not in brain:
                brain["contact_start"] = None
        
        monsters_to_remove = []
        brains_to_remove = []
        
        # Track which brains have active contact
        brain_contact_status = {id(brain): False for brain in brain_blocks}
        
        for monster in self.monsters:
            # Find nearest brain block (prioritize brain over player)
            target_x = player_x
            is_targeting_brain = False
            nearest_brain = None
            nearest_brain_dist = float('inf')
            
            for brain in brain_blocks:
                brain_x = brain["x"] + self.block_manager.block_size // 2
                dist = abs(brain_x - monster["x"])
                if dist < nearest_brain_dist:
                    nearest_brain_dist = dist
                    nearest_brain = brain
            
            # If brain exists and is reasonably close, target it
            if nearest_brain is not None and nearest_brain_dist < 2000:  # 2000px range
                # Target the side of the brain (left or right) instead of center
                brain_center_x = nearest_brain["x"] + self.block_manager.block_size // 2
                if monster["x"] < brain_center_x:
                    # Monster is to the left, target right side of brain
                    target_x = nearest_brain["x"] + self.block_manager.block_size + 20
                else:
                    # Monster is to the right, target left side of brain
                    target_x = nearest_brain["x"] - 20
                
                is_targeting_brain = True
                monster["brain_target"] = nearest_brain
                
                # Check if monster is in contact with brain (with lenient margin)
                monster_left = monster["x"] - self.monster_size // 2
                monster_right = monster["x"] + self.monster_size // 2
                brain_left = nearest_brain["x"]
                brain_right = nearest_brain["x"] + self.block_manager.block_size
                
                # Use a more lenient contact detection (20px margin on each side)
                is_in_contact = monster_right > brain_left - 20 and monster_left < brain_right + 20
                
                if is_in_contact:
                    # Mark that this brain has active contact
                    brain_contact_status[id(nearest_brain)] = True
                    
                    # Monster is in contact with brain
                    if nearest_brain["contact_start"] is None:
                        nearest_brain["contact_start"] = adjusted_time * 1000  # Store in ms
                    
                    monster["at_brain"] = True
                else:
                    monster["at_brain"] = False
                    
                    # Check total contact duration for this brain (across all zombies)
                    contact_duration = 0
                    if nearest_brain["contact_start"] is not None:
                        contact_duration = adjusted_time * 1000 - nearest_brain["contact_start"]
                    if contact_duration >= self.brain_contact_duration:
                        # Destroy the brain after 1 minute of total contact!
                        brains_to_remove.append(nearest_brain)
            else:
                monster["brain_target"] = None
            
            # Determine direction to chase target (brain or player)
            if target_x > monster["x"]:
                direction = 1
            elif target_x < monster["x"]:
                direction = -1
            else:
                direction = monster.get("direction", 1)  # Keep current direction if no movement
            
            monster["direction"] = direction
            
            # Find the highest block surface under the monster
            ground_level = self._getHighestBlockUnder(monster["x"])
            
            # Check if monster needs to jump over a block
            should_jump = False
            if self.block_manager and not monster["jumping"]:
                # Check if there's a block in the way within 20 pixels in front
                monster_left = monster["x"] - self.monster_size // 2
                monster_right = monster["x"] + self.monster_size // 2
                
                for block in self.block_manager.placed_blocks:
                    # Skip invisible top blocks
                    if block.get("is_top", False):
                        continue
                    if not block.get("solid", True):
                        continue
                    
                    # Don't jump over brain blocks - zombies should stand beside them, not on top
                    if block.get("type") == "half-eaten brain":
                        continue
                    
                    block_left = block["x"]
                    block_right = block["x"] + self.block_manager.block_size
                    
                    # Check if block is in front of monster within 20 pixels
                    if direction == 1:  # Moving right
                        if block_left > monster_right and block_left <= monster_right + 20:
                            should_jump = True
                            break
                    elif direction == -1:  # Moving left
                        if block_right < monster_left and block_right >= monster_left - 20:
                            should_jump = True
                            break
            
            # Start jump if needed
            if should_jump and not monster["jumping"] and monster["y"] >= ground_level - 5:
                monster["jumping"] = True
                monster["jump_start"] = pygame.time.get_ticks()
            
            # Handle jumping
            if monster["jumping"]:
                elapsed = pygame.time.get_ticks() - monster["jump_start"]
                if elapsed >= monster["jump_duration"] * 1000:
                    monster["jumping"] = False
                    monster["jump_start"] = None
                    monster["vx"] = 0  # Stop air movement
                elif elapsed < monster["jump_duration"] * 1000:
                    monster["y"] -= monster["jump_power"] * dt * multiplier
                    # Allow horizontal movement while jumping
                    monster["vx"] = direction * monster["speed"]
            
            # Apply gravity if not on ground and not jumping
            if monster["y"] < ground_level and not monster["jumping"]:
                monster["y"] += self.player.gravity * dt
                if monster["y"] > ground_level:
                    monster["y"] = ground_level
            elif not monster["jumping"]:
                monster["y"] = ground_level
            
            # Move horizontally towards player (check block collision first)
            # Use vx if jumping, otherwise use normal direction-based movement
            if monster["jumping"]:
                new_x = monster["x"] + monster["vx"] * dt * multiplier
            else:
                new_x = monster["x"] + direction * monster["speed"] * dt * multiplier
            
            # Check if new position would collide with a block
            can_move = True
            if self.block_manager and direction != 0:
                monster_left = new_x - self.monster_size // 2
                monster_right = new_x + self.monster_size // 2
                monster_bottom = monster["y"] + self.monster_size
                
                for block in self.block_manager.placed_blocks:
                    # Skip invisible top blocks
                    if block.get("is_top", False):
                        continue
                    if not block.get("solid", True):
                        continue
                    block_left = block["x"]
                    block_right = block["x"] + self.block_manager.block_size
                    block_top = self.block_manager.groundy
                    
                    # Check horizontal collision (only check when monster is at block level)
                    if monster_bottom > block_top:
                        if direction == 1:  # Moving right
                            if monster_right >= block_left - 10 and monster_right <= block_right + 5 and monster["x"] < block_left:
                                can_move = False
                                break
                        elif direction == -1:  # Moving left
                            if monster_left <= block_right + 10 and monster_left >= block_left - 5 and monster["x"] > block_right:
                                can_move = False
                                break
            
            # Only move if no collision
            if can_move:
                monster["x"] = new_x
            
            # Remove monsters that are too far away (cleanup) or dead
            # Only despawn when focused to prevent despawning during window unfocus periods
            current_time = pygame.time.get_ticks()
            monster_age_ms = current_time - monster.get("spawn_time", current_time)
            monster_age_seconds = monster_age_ms / 1000
            
            should_despawn = monster.get("health", 100) <= 0  # Always despawn if dead
            if should_despawn and monster.get("health", 100) <= 0 and not monster.get("loot_dropped", False):
                self._dropMonsterLoot(monster)
                monster["loot_dropped"] = True
            if monster_age_seconds > 120:  # 120 second despawn timer
                should_despawn = True
            if is_focused and abs(monster["x"] - player_x) > self.screenx * 10:
                should_despawn = True
            if should_despawn:
                monsters_to_remove.append(monster["id"])
        
        # Remove far away monsters
        self.monsters = [m for m in self.monsters if m["id"] not in monsters_to_remove]
        
        # Reset contact timers for brains with no active contact
        for brain in brain_blocks:
            if not brain_contact_status.get(id(brain), False):
                # No zombie is currently touching this brain, reset timer
                brain["contact_start"] = None
        
        # Remove destroyed brain blocks
        if self.block_manager and brains_to_remove:
            self.block_manager.placed_blocks = [b for b in self.block_manager.placed_blocks if b not in brains_to_remove]
    
    def _dropMonsterLoot(self, monster):
        if not self.itemManager:
            return
        
        for item_name, loot_data in self.loot_table.items():
            rarity = loot_data["rarity"]
            drop_chance = self.drop_chances.get(rarity, 1.0)
            if random.random() < drop_chance:
                item_id = util.getItemID(item_name)
                mn = loot_data["min"]
                mx = loot_data["max"]
                amt = random.randint(mn, mx)
                drop_x = monster["x"] + random.randint(-20, 20)
                self.itemManager.addItemEntities(item_id, amt, (drop_x, monster["y"]))
    
    def _getHighestBlockUnder(self, monster_x):
        if not self.block_manager:
            return self.groundy
        
        highest_block_top = self.groundy
        monster_left = monster_x - self.monster_size // 2
        monster_right = monster_x + self.monster_size // 2
        
        for block in self.block_manager.placed_blocks:
            # Skip invisible top blocks
            if block.get("is_top", False):
                continue
            if not block.get("solid", True):
                continue
            
            # Don't allow zombies to stand on brain blocks
            if block.get("type") == "half-eaten brain":
                continue
                
            block_left = block["x"]
            block_right = block["x"] + self.block_manager.block_size
            block_top = self.block_manager.groundy
            
            # Check if monster x-range overlaps with block x-range
            if monster_right > block_left and monster_left < block_right:
                # This block is under the monster, use its top as reference
                if block_top < highest_block_top:
                    highest_block_top = block_top
        
        return highest_block_top
    
    def renderMonsters(self):
        player_x = self.player.x
        screenx = self.screenx
        
        # Update animation frame
        self.animation_frame = (self.animation_frame + 1) % 20  # Change frame every 20 ticks
        zombie_frame_id = f"zombie_{(self.animation_frame // 10) + 1:03d}"
        
        # Update animation frame
        self.animation_frame = (self.animation_frame + 1) % 20  # Change frame every 20 ticks
        
        for monster in self.monsters:
            pos_on_screen = monster["x"] - player_x + screenx // 2
            
            # Only render if on screen
            if -100 <= pos_on_screen <= screenx + 100:
                monster_screen_x = pos_on_screen - self.monster_size // 2
                monster_screen_y = monster["y"] - self.monster_size
                
                # Get zombie texture and resize to original dimensions (40x40)
                if monster.get("at_brain", False):
                    zombie_frame_id = "zombie_001"  # Fixed frame 1 when at brain
                else:
                    zombie_frame_id = f"zombie_{(self.animation_frame // 10) + 1:03d}"
                
                zombie_tex = self.renderer.getTexture(zombie_frame_id)
                if zombie_tex:
                    resized_zombie = self.renderer.ResizeTexture(zombie_frame_id, [self.monster_size, self.monster_size], False, save=False)
                    if resized_zombie:
                        # Flip sprite based on direction
                        direction = monster.get("direction", 1)
                        if direction < 0:  # Facing left
                            flipped_zombie = pygame.transform.flip(resized_zombie, True, False)
                            self.renderer.render_surface(flipped_zombie, (int(monster_screen_x), int(monster_screen_y)))
                        else:  # Facing right
                            self.renderer.render_surface(resized_zombie, (int(monster_screen_x), int(monster_screen_y)))
                
                # Render health bar above monster
                health_bar_y = monster_screen_y - 10
                health_percent = monster.get("health", 100) / monster.get("max_health", 100)
                health_bar_width = int(self.monster_size * health_percent)
                
                # Background (gray)
                self.renderer.render(["health_bar_bg"], [(monster_screen_x, health_bar_y)])
                
                # Foreground (green/yellow/red based on health)
                if health_percent > 0:
                    if health_percent > 0.6:
                        color = (0, 255, 0)  # Green
                    elif health_percent > 0.3:
                        color = (255, 255, 0)  # Yellow
                    else:
                        color = (255, 0, 0)  # Red
                    
                    # Create dynamic health bar
                    health_surface = pygame.Surface((health_bar_width, 6))
                    health_surface.fill(color)
                    self.renderer.render_surface(health_surface, (monster_screen_x, health_bar_y))
    
    def checkLaserCollision(self, lasers):
        lasers_to_remove = []
        player_x = self.player.x
        screenx = self.screenx
        
        for laser_idx, laser in enumerate(lasers):
            # laser x/y are in screen coordinates
            laser_x = laser['x']
            laser_y = laser['y']
            
            for monster in self.monsters:
                # Convert monster world x to screen x
                hitbox_size = 60  # Even larger hitbox
                monster_screen_x = monster["x"] - player_x + screenx // 2 - hitbox_size // 2
                monster_screen_y = monster["y"] - (hitbox_size - self.monster_size) // 2  # Adjust y to center hitbox
                
                # Check collision (laser treated as 20x20 for better hit detection, monster hitbox is hitbox_size x hitbox_size)
                laser_right = laser_x + 20
                laser_bottom = laser_y + 20
                monster_right = monster_screen_x + hitbox_size
                monster_bottom = monster_screen_y + hitbox_size
                if (laser_right > monster_screen_x and laser_x < monster_right and
                    laser_bottom > monster_screen_y and laser_y < monster_bottom):
                    # Hit! Reduce health with player's damage boost applied
                    base_damage = random.randint(10, 25)
                    damage = int(base_damage * (1 + self.player.damage_boost / 100))
                    monster["health"] = monster.get("health", 100) - damage
                    lasers_to_remove.append(laser_idx)
                    break  # Each laser can only hit one monster
        
        return lasers_to_remove
    
    def checkPlayerCollision(self):
        player_x = self.player.x
        player_y = self.player.y
        player_width = 50
        player_height = 50
        
        for monster in self.monsters:
            # Simple AABB collision detection
            monster_width = self.monster_size
            monster_height = self.monster_size
            
            if (player_x < monster["x"] + monster_width and
                player_x + player_width > monster["x"] and
                player_y < monster["y"] + monster_height and
                player_y + player_height > monster["y"]):
                # Collision detected, try to damage player
                self.player.take_damage()
    
    def update(self, is_focused=True, is_paused=False):
        current_time = pygame.time.get_ticks() / 1000
        
        if is_paused:
            if not hasattr(self, 'pause_start'):
                self.pause_start = current_time
            return
        else:
            if hasattr(self, 'pause_start'):
                self.total_pause_time += current_time - self.pause_start
                del self.pause_start
        
        self.spawnMonster()
        self.updateMonsters(is_focused)
        self.checkPlayerCollision()  # Check for player damage
        # self.renderMonsters()  # Moved to separate render call


class BeaconManager:
    def __init__(self, player, ground, block_manager, monster_manager):
        self.player = player
        self.ground = ground
        self.block_manager = block_manager
        self.monster_manager = monster_manager
        self.renderer = util.getRenderer()
        
        # Beacon laser properties (1/3 the player's rate)
        self.laser_cooldown_time = 1.5  # Player is 0.1, so beacon is 15x slower
        self.beacon_range = 500  # Limited range of 500 pixels
        self.beacons = {}  # Dict mapping beacon block id to beacon state
        
    def update(self, dt, is_paused=False):
        if is_paused:
            return
        if not self.block_manager:
            return
        
        # Get all beacon blocks
        beacon_blocks = [b for b in self.block_manager.placed_blocks if b.get("type") == "beacon"]
        
        # Initialize beacon state for new beacons
        for beacon in beacon_blocks:
            beacon_id = id(beacon)
            if beacon_id not in self.beacons:
                self.beacons[beacon_id] = {
                    "laser_cooldown": 0,
                    "active_lasers": []
                }
        
        # Remove beacons that no longer exist
        existing_ids = {id(b) for b in beacon_blocks}
        self.beacons = {bid: state for bid, state in self.beacons.items() if bid in existing_ids}
        
        # Update cooldowns and shoot lasers
        for beacon in beacon_blocks:
            beacon_id = id(beacon)
            beacon_state = self.beacons[beacon_id]
            
            # Update cooldown
            if beacon_state["laser_cooldown"] > 0:
                beacon_state["laser_cooldown"] -= dt
            
            # Try to shoot at nearest zombie
            if beacon_state["laser_cooldown"] <= 0 and self.monster_manager.monsters:
                # Find nearest zombie
                beacon_center_x = beacon["x"] + self.block_manager.block_size // 2
                beacon_center_y = self.block_manager.groundy + 10  # Shoot from a bit lower
                
                nearest_monster = None
                nearest_dist = float('inf')
                
                for monster in self.monster_manager.monsters:
                    dx = monster["x"] - beacon_center_x
                    dy = monster["y"] - self.monster_manager.monster_size // 4 - beacon_center_y
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_monster = monster
                
                # Shoot laser at nearest zombie if within range
                if nearest_monster and nearest_dist <= self.beacon_range:
                    target_x = nearest_monster["x"]
                    target_y = nearest_monster["y"] - self.monster_manager.monster_size // 4  # Aim at monster middle/top
                    dx = target_x - beacon_center_x
                    dy = target_y - beacon_center_y
                    distance = (dx**2 + dy**2) ** 0.5
                    
                    if distance > 0:
                        dx /= distance
                        dy /= distance
                    
                    beacon_state["active_lasers"].append({
                        'x': float(beacon_center_x),
                        'y': float(beacon_center_y),
                        'dx': dx,
                        'dy': dy
                    })
                    beacon_state["laser_cooldown"] = self.laser_cooldown_time
                    
                    # Play laser sound effect
                    try:
                        laser_sound = pygame.mixer.Sound("assets/laser_gun.mp3")
                        laser_sound.set_volume(0.5)  # 50% volume
                        laser_sound.play()
                    except:
                        pass  # Silently fail if sound not found
        
        # Update laser positions
        self._update_lasers(dt)
        
    def _update_lasers(self, dt):
        screen_w, screen_h = util.getScreenDimensions()
        ground_y = screen_h - self.ground.height
        
        for beacon_state in self.beacons.values():
            lasers_to_remove = []
            
            for i, laser in enumerate(beacon_state["active_lasers"]):
                laser['x'] += laser['dx'] * dt * 500
                laser['y'] += laser['dy'] * dt * 500
                
                # Remove if off screen or hit ground
                if laser['y'] >= ground_y or laser['x'] < 0 or laser['x'] > screen_w or laser['y'] < 0:
                    lasers_to_remove.append(i)
            
            for i in reversed(lasers_to_remove):
                beacon_state["active_lasers"].pop(i)
    
    def render_lasers(self):
        player_x = self.player.x
        screen_w = util.getScreenDimensions()[0]
        player_screen_x = screen_w // 2
        
        for beacon_state in self.beacons.values():
            for laser in beacon_state["active_lasers"]:
                # Convert world coordinates to screen coordinates
                laser_screen_x = laser['x'] - player_x + player_screen_x
                laser_screen_y = laser['y']
                
                self.renderer.createAndRenderSolidTexture(
                    "beacon_laser", (255, 0, 0), (10, 10), 
                    (int(laser_screen_x), int(laser_screen_y)), 4, cache=False
                )
    
    def check_laser_collisions(self):
        for beacon_state in self.beacons.values():
            lasers_to_remove = []
            
            for laser_idx, laser in enumerate(beacon_state["active_lasers"]):
                # laser x/y are in world coordinates
                laser_x = laser['x']
                laser_y = laser['y']
                laser_width = 100
                laser_height = 100
                
                for monster in self.monster_manager.monsters:
                    monster_x = monster["x"]
                    monster_y = monster["y"]
                    monster_size = self.monster_manager.monster_size
                    
                    # Check overlap collision (laser is 100x100, monster is monster_size x monster_size)
                    laser_left = laser_x - laser_width // 2
                    laser_right = laser_x + laser_width // 2
                    laser_top = laser_y - laser_height // 2
                    laser_bottom = laser_y + laser_height // 2
                    
                    monster_left = monster_x - monster_size // 2
                    monster_right = monster_x + monster_size // 2
                    monster_top = monster_y
                    monster_bottom = monster_y + monster_size
                    
                    if (laser_right > monster_left and laser_left < monster_right and
                        laser_bottom > monster_top and laser_top < monster_bottom):
                        # Hit! Reduce health
                        base_damage = random.randint(10, 25)
                        damage = int(base_damage * (1 + self.player.damage_boost / 100))
                        monster["health"] = monster.get("health", 100) - damage
                        lasers_to_remove.append(laser_idx)
                        break  # Each laser can only hit one monster
            
            for i in reversed(lasers_to_remove):
                beacon_state["active_lasers"].pop(i)

