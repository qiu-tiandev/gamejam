import pygame
from renderer import Renderer
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
        self.laser_cooldown_time = 1.5
        self.active_lasers = []
    def detectinput(self):
        keys = pygame.key.get_pressed()
        self.dt = util.getDeltaTime()
        if keys:
            for key, direction in self.directions.items():
                if keys[key]: 
                    self.x += round(direction[0] * self.speed * self.dt * self.multiplier)
                    self.y += direction[1] * self.speed * self.dt * self.multiplier
            if keys[pygame.K_SPACE]:
                if not self.jumping and self.ground.isTouchingGround(self.y):
                    self.jumping = True
                    self.jumping_start = pygame.time.get_ticks()
    def move(self):
        self.detectinput()
        if self.jumping:
            elapsed = pygame.time.get_ticks() - self.jumping_start
            if elapsed >= (self.jump_duration+self.peak_jump_duration) *1000:
                self.jumping = False
                self.jumping_start = None
            if elapsed < self.jump_duration*1000:
                self.y -=self.jump_power*self.dt*self.multiplier
        if not self.ground.isTouchingGround(self.y)and not self.jumping:
            self.y += self.gravity * self.dt
        elif not self.jumping:
            screen_dims = util.getScreenDimensions()
            self.y = screen_dims[1]-self.ground.height - 50
        screen_w = util.getScreenDimensions()[0]
        self.renderer.render(["Player"], [(screen_w//2-25, self.y)])

    def update(self):
        self.detectinput()
    
    def updateLasers(self, dt):
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
    
    def shootLaser(self, mouse_pos, inventory):
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
        player_center_y = self.y + 25
        
        dx = mouse_pos[0] - player_center_x
        dy = mouse_pos[1] - player_center_y
        distance = (dx**2 + dy**2) ** 0.5
        
        if distance > 0:
            dx /= distance
            dy /= distance
        req_energy = random.randint(2, 10)
        # check if got energy
        if self.lasergun_energy < req_energy:
            return
        
        self.active_lasers.append({
            'x': float(player_center_x),
            'y': float(player_center_y),
            'dx': dx,
            'dy': dy
        })
        self.lasergun_energy -= req_energy
        self.laser_cooldown = self.laser_cooldown_time
        
