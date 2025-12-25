import pygame
from animations import TypingAnimation
import util
from world import Sky
from entities import Ground

class TutorialManager:
    def __init__(self, renderer, world, craft_manager=None, player=None, chest_manager=None, cooker_manager=None, inventory=None):
        self.renderer = renderer
        self.world = world
        self.craft_manager = craft_manager
        self.player = player
        self.chest_manager = chest_manager
        self.cooker_manager = cooker_manager
        self.inventory = inventory
        self.is_active = True
        self.current_paragraph = 0
        self.animation_complete = False
        self.typing_anim = None
        
        # Save player state for restoration after tutorial
        if self.player:
            self.saved_health = self.player.health
            self.saved_hunger_timer = self.player.hunger_timer
            self.saved_last_food_time = self.player.last_food_time
        
        # Create tutorial ground and sky
        self.tutorial_ground = Ground(70, self.world.ground_id)
        self.tutorial_sky = Sky(self.world.sky_id, self.tutorial_ground.height)
        self.dummy_player = type('DummyPlayer', (), {'x': 0})()
        
        # Tutorial paragraphs
        self.paragraphs = [
            "Where am I? This place looks strange...",
            "Hi human, you are now trapped in the future, and you will have to time travel to get back to your time. Usual controls: A,D,SPACE",
            "Press E to open the Crafting Menu. Click on items to craft them. You need the required materials. HINT: Use it to view recipes for time travelling!",
            "Place a Cooker block by selecting it and pressing W. Press S near the Cooker to open the Smelting Menu.",
            "Use the Laser Gun to shoot enemies. Left click to fire. The gun uses energy.",
            "Press R while holding the Laser Gun to refill it using Battery or Liquid Fuel from your inventory.",
            "Press Q to drop items. Use number keys 1-9 and 0 to switch inventory slots.",
            "You can place blocks like Beacons and Brain blocks to help defend against zombies. (Unlocked later in the game)",
            "There will be special items with specials uses. So keep an eye out on the crafting recipes!",
            "The hunger bar at the top shows your health. Eat food (cooked monster flesh) by pressing R to refill it. High hunger gives damage boost!",
            "Chests contain loot. Walk near them and press S to open. They contiain random items required for progress.",
            "Good luck! The tutorial is complete. Click to start the game. But since I am nice, I will give you some starter loot.. Your cooked food will be preserved after time travel."
        ]
        
        # Speaker names for each paragraph
        self.speakers = ["You"] + ["Mysterious Voice"] * (len(self.paragraphs) - 1)
        
        self.message_box_height = 0
        self.message_box_y = 0
        self.text_x = 0
        self.text_y = 0
        self.font_size = 18  # Default, will be recalculated
        self.line_height = 24
        self.previous_font_size = 18  # Track font size changes
        self._recalc_layout()
        self._start_paragraph(0)

    def _recalc_layout(self):
        w, h = util.getScreenDimensions()
        # Message box takes bottom third of screen
        self.message_box_height = h // 3
        self.message_box_y = h - self.message_box_height
        # Text position with minimal padding to maximize text width
        self.text_x = int(w * 0.05)  # Reduced from 0.1 to 0.05 for more text space
        # Position text below speaker name (speaker at message_box_y + 20, with some spacing)
        self.text_y = self.message_box_y + 60
        
        # Calculate dynamic font size based on screen width
        # More aggressive scaling: base 20 for 960px, scales up faster
        if not self.animation_complete:
            self.font_size = max(14, int(20 * (w / 960.0)))
        self.line_height = self.font_size + 6  # Line spacing
    
    def _start_paragraph(self, index):
        if index >= len(self.paragraphs):
            self.is_active = False
            # Close any open menus
            if self.craft_manager:
                self.craft_manager.is_open = False
            if self.cooker_manager:
                self.cooker_manager.is_open = False
            return

        self.current_paragraph = index
        self.animation_complete = False

        w, h = util.getScreenDimensions()
        text_color = util.getContrastColor(self.world.themeColor)

        # Wrap the text to fit the screen
        import pygame
        font = pygame.font.SysFont("Arial", self.font_size)
        max_text_width = w - 2 * self.text_x
        self.wrapped_lines = self._wrap_text(self.paragraphs[index], font, self.font_size, max_text_width)
        wrapped_text = " ".join(self.wrapped_lines)  # Join for typing animation

        # Create typing animation
        self.typing_anim = TypingAnimation(
            wrapped_text,
            (self.text_x, self.text_y),
            "Arial",
            self.font_size,
            text_color,
            speed=10.0  # Fast typing speed
        )

    def handle_click(self):
        if not self.is_active:
            return
        
        if not self.animation_complete:
            # Animation still playing - show full text immediately
            self._show_full_paragraph()
            self.animation_complete = True
        else:
            # Animation complete - move to next paragraph
            self._start_paragraph(self.current_paragraph + 1)
    
    def _show_full_paragraph(self):
        w, h = util.getScreenDimensions()
        text_color = util.getContrastColor(self.world.themeColor)
        
        # Wrap the text to fit the screen
        import pygame
        font = pygame.font.SysFont("Arial", self.font_size)
        max_text_width = w - 2 * self.text_x
        self.wrapped_lines = self._wrap_text(self.paragraphs[self.current_paragraph], font, self.font_size, max_text_width)
        
        # Create the full text for typing animation (joined)
        wrapped_text = " ".join(self.wrapped_lines)
        self.renderer.createText(
            "TEMPTYPINGANIMATION",
            wrapped_text,
            "Arial",
            18,
            text_color,
            True
        )
    
    def _wrap_text(self, text, font, font_size, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            # Create a temporary text surface to measure width
            temp_surface = font.render(test_line, True, (0, 0, 0))
            if temp_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def update(self):
        if not self.is_active:
            return

        # Update typing animation
        if self.typing_anim and not self.animation_complete:
            is_done = self.typing_anim.doTypingAnimation()
            if is_done:
                self.animation_complete = True
                # Resize font when animation completes
                self._resize_font_on_completion()

        # Recalculate layout to adapt to screen size changes
        self._recalc_layout()
    
    def _resize_font_on_completion(self):
        w, h = util.getScreenDimensions()
        # Apply larger font size for completed text
        # Base 24 for 960px, scales more aggressively
        self.font_size = max(16, int(24 * (w / 960.0)))
        self.line_height = self.font_size + 6
        # Re-wrap text with new font size
        self._show_full_paragraph()

    def render(self):
        if not self.is_active:
            return

        # Render tutorial world background
        self.tutorial_sky.render(0)  # Static sky
        self.tutorial_ground.renderGround(self.dummy_player)  # Static ground

        w, h = util.getScreenDimensions()

        # Render interactive elements BEFORE message box so they appear beneath it
        if self.current_paragraph == 2 and self.craft_manager:  # Crafting paragraph
            # Temporarily open crafting menu for tutorial
            self.craft_manager.is_open = True
            self.craft_manager.render()
        elif self.current_paragraph == 3 and self.cooker_manager:  # Cooking paragraph
            # Temporarily open cooker menu for tutorial
            self.cooker_manager.is_open = True
            self.cooker_manager.render()
        elif self.current_paragraph == 4 and self.player:  # Laser gun paragraph
            # Show energy info
            energy = getattr(self.player, 'lasergun_energy', 100)
            energy_text = f"Laser Gun Energy: {energy}/100"
            text_color = util.getContrastColor(self.world.themeColor)
            self.renderer.createAndRenderText(
                "energy_info",
                energy_text,
                "Arial",
                16,
                text_color,
                (w // 2 - 100, h // 2),
                cache=False,
                silence=True
            )
        elif self.current_paragraph == 6 and self.player:  # Inventory paragraph
            # Show inventory slots
            if hasattr(self, 'inventory') and self.inventory:
                self.inventory.renderInventory()
        elif self.current_paragraph == 9 and self.player:  # Health and hunger bars paragraph
            # Show health and hunger bars
            self.player.render_healthbar()
            self.player.render_hunger_bar()
        elif self.current_paragraph == 10 and self.chest_manager:  # Chests paragraph
            # Render a sample chest in the middle of the screen
            chest_x = w // 2
            chest_y = h // 2 - 25  # Center vertically (chest is 50px tall)
            self.renderer.render([self.chest_manager.id], [(chest_x, chest_y)])

        # Render message box AFTER interactive elements so it appears on top
        gui_tex = self.renderer.getTexture("gui_001")
        if gui_tex:
            # Stretch to full width and bottom third height
            scaled_gui = pygame.transform.scale(gui_tex, (w, self.message_box_height))
            self.renderer.screen.blit(scaled_gui, (0, self.message_box_y))
        else:
            # Fallback to solid background
            box_surface = pygame.Surface((w, self.message_box_height))
            box_surface.fill((40, 40, 40))
            box_surface.set_alpha(230)
            self.renderer.screen.blit(box_surface, (0, self.message_box_y))

        # Render text (typing animation handles this)
        if self.typing_anim:
            # Render speaker name as title
            speaker_name = self.speakers[self.current_paragraph]
            speaker_color = util.getContrastColor(self.world.themeColor)
            speaker_font_size = int(self.font_size * 1.2)  # Slightly larger than message text
            speaker_y = self.message_box_y + 20  # Position near top of message box
            self.renderer.createAndRenderText(
                f"TEMPTYPINGANIMATION_SPEAKER",
                speaker_name,
                "Arial",
                speaker_font_size,
                speaker_color,
                (self.text_x, speaker_y),
                cache=False,
                silence=True
            )
            
            if self.animation_complete and hasattr(self, 'wrapped_lines'):
                # Render each wrapped line separately
                text_color = util.getContrastColor(self.world.themeColor)
                for i, line in enumerate(self.wrapped_lines):
                    y_pos = self.text_y + i * self.line_height
                    self.renderer.createAndRenderText(
                        f"TEMPTYPINGANIMATION_LINE_{i}",
                        line,
                        "Arial",
                        self.font_size,
                        text_color,
                        (self.text_x, y_pos),
                        cache=False,
                        silence=True
                    )
            else:
                self.renderer.render(["TEMPTYPINGANIMATION"], [(self.text_x, self.text_y)])

        # Show hint at bottom
        hint_text = "Click to continue..." if self.animation_complete else "Click to skip animation..."
        text_color = util.getContrastColor(self.world.themeColor)
        hint_y = self.message_box_y + self.message_box_height - 35
        self.renderer.createAndRenderText(
            "tutorial_hint",
            hint_text,
            "Arial",
            14,
            text_color,
            (self.text_x, hint_y),
            cache=False,
            silence=True
        )
