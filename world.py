import util
import pygame

class World:
    def __init__(self, gravity, chestLoot: dict = None):
        self.gravity = gravity
        if chestLoot is None:
            self.chestLoot = {
                "bones": (1, 3),
                "metal scrap": (2, 5),
                "string": (1, 2),
                "stone": (3, 6),
            }
        else:
            self.chestLoot = chestLoot
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