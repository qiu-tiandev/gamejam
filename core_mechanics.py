import util
from animations import SpriteAnimation
class InventoryManager:
    def __init__(self,id):
        self.items:dict[int,int] = {} # itemID:amount
        self.renderer = util.getRenderer()
        self.currentSlot = 1
        self.slotSize = 30
        self.num_slots = 10
        self.spriteAnimation = SpriteAnimation(id,(24,24),2)
        self.lastDir = 1
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
        x_offset = 10
        y_offset = 40
        spacing = self.slotSize
        items_list = list(self.items.items())
        for idx in range(1, self.num_slots + 1):
            pos = (x_offset, y_offset + (idx - 1) * spacing)
            frame = 1 if idx == self.currentSlot else 0
            self.spriteAnimation.doSpriteAnimation(frame, pos)
            if idx <= len(items_list):
                item_id, amount = items_list[idx - 1]
                if amount <= 0:
                     continue
                icon_id = f"items_{item_id:03d}"
                icon = self.renderer.getTexture(icon_id) or self.renderer.getTexture("placeholder-item")
                if icon:
                    self.renderer.render([icon], [(pos[0] + 2, pos[1] + 2)])
                text_pos = (pos[0] + self.slotSize + 8, pos[1] + self.slotSize // 4)
                self.renderer.createAndRenderText(
                    f"inv_amt_{item_id}", str(amount), "arial", 18, (255,255,255), text_pos, cache=False, silence=True
                 )
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
        
