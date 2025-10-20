# 📁 FILE: display_cat.py
# Show the most recent cat PNG on a 480x320 display. Auto-reloads if file changes.
import os, time
import pygame
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, PNG_PATH

os.environ.setdefault("SDL_FBDEV", "/dev/fb1" if os.path.exists("/dev/fb1") else "/dev/fb0")
os.environ.setdefault("SDL_VIDEODRIVER", "fbcon")


class CatDisplay:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.last_mtime = 0
        self.image = None

    def load_image(self):
        if not os.path.exists(PNG_PATH):
            # placeholder screen
            self.screen.fill((245, 239, 230))
            font = pygame.font.SysFont("Verdana", 24)
            txt = font.render("No cat yet — run generate_cat.py", True, (40, 40, 40))
            self.screen.blit(txt, (20, DISPLAY_HEIGHT // 2 - 12))
            pygame.display.flip()
            return
        mtime = os.path.getmtime(PNG_PATH)
        if mtime != self.last_mtime:
            self.last_mtime = mtime
            img = pygame.image.load(PNG_PATH)
            self.image = pygame.transform.smoothscale(img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            self.load_image()
            if self.image:
                self.screen.blit(self.image, (0, 0))
                pygame.display.flip()
            self.clock.tick(10)


if __name__ == "__main__":
    app = CatDisplay()
    app.loop()
