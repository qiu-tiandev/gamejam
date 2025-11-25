import worker
import console
renderer = worker.getRenderer()
InternalCache = {}
class SpriteAnimation:

    def doSpriteAnimation(spriteid, frame:int, spriteSize:tuple[int,int], position:tuple[int,int]):
        spritesheet = renderer.getTexture(spriteid)
        if not spritesheet:
            console.sendError(f"Sprite ID {spriteid} not found for animation.", __file__)
            return None
        frames = []
        numSpriteW = spritesheet.get_width() // spriteSize[0]
        numSpriteH = spritesheet.get_height() // spriteSize[1]
        for HorizontalFrames in range(numSpriteW):
            for VerticalFrames in range(numSpriteH):
                rect = pygame.Rect(HorizontalFrames * spriteSize[0], VerticalFrames * spriteSize[1], spriteSize[0], spriteSize[1])
                frames.append(rect)