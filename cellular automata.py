import pygame
import numpy as np
from PIL import Image
import time
import easygui
# h/w & tick swpeed
GRID_SIZE = 100
CELL_SIZE = 4
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
FPS_DISPLAY = 60  
SIM_FPS = 10      

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Conway's Game of Life But You Can Import An Image")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

BG = (15, 15, 15)
CELL = (230, 230, 230)
GRID = (40, 40, 40)
UI_BG = (30, 30, 30)
UI_FG = (200, 200, 200)
running = False
image_types = ["*.png", "*.jpg", "*.jpeg"]  # define the allowed types
imagePath = easygui.fileopenbox(msg="Select Image", title="Image", default="*.png;*.jpg", filetypes=image_types)


# image to gol
def image_to_grid(path):
    img = Image.open(path).convert("L")
    img = img.resize((GRID_SIZE, GRID_SIZE), Image.BILINEAR)

    px = np.asarray(img, dtype=np.float32)
    px = (px - px.min()) / (np.ptp(px) + 1e-67)
    cutoff = np.quantile(px, 0.5)
    return (px < cutoff).astype(np.uint8)

if imagePath:  # make sure the user didn't cancel
    grid = image_to_grid(imagePath)
# conway's logic
def step(a):
    n = sum(
        np.roll(np.roll(a, i, 0), j, 1)
        for i in (-1, 0, 1)
        for j in (-1, 0, 1)
        if (i, j) != (0, 0)
    )
    return ((n == 3) | ((a == 1) & (n == 2))).astype(np.uint8)

def draw():
    screen.fill(BG)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y, x]:
                pygame.draw.rect(
                    screen,
                    CELL,
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )

    
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))
    pygame.draw.rect(screen, UI_BG, (0, HEIGHT, WIDTH, 50))

    # ui
    btn_text = "Pause" if running else "Play"
    pygame.draw.rect(screen, (70, 70, 70), (10, HEIGHT + 10, 80, 30))
    text_surf = font.render(btn_text, True, UI_FG)
    screen.blit(text_surf, (20, HEIGHT + 15))

    pygame.draw.rect(screen, (70, 70, 70), (110, HEIGHT + 20, 200, 10))
    slider_pos = int(((SIM_FPS - 1) / 30) * 200)  # max 30 FPS
    pygame.draw.circle(screen, (200, 100, 100), (110 + slider_pos, HEIGHT + 25), 8)
    speed_text = font.render(f"Speed: {SIM_FPS}", True, UI_FG)
    screen.blit(speed_text, (320, HEIGHT + 15))
    pygame.display.flip()

slider_drag = False
last_update = time.time()

while True:
    clock.tick(FPS_DISPLAY)
    now = time.time()
    dt = now - last_update

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if 10 <= mx <= 90 and HEIGHT + 10 <= my <= HEIGHT + 40:  #turns out u just make a box and if the mouse clicks there then it pauses/plays
                running = not running
            elif 110 <= mx <= 310 and HEIGHT + 15 <= my <= HEIGHT + 35:
                slider_drag = True

        if event.type == pygame.MOUSEBUTTONUP:
            slider_drag = False

    # tickspeed
    if slider_drag:
        mx, _ = pygame.mouse.get_pos()
        mx = max(110, min(310, mx))
        SIM_FPS = int(((mx - 110) / 200) * 30) + 1  

    mx, my = pygame.mouse.get_pos()
    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE and my < HEIGHT:
        buttons = pygame.mouse.get_pressed()
        if buttons[0] and not running:
            grid[gy, gx] = 1
        elif buttons[2] and not running:
            grid[gy, gx] = 0

    if running and dt >= 1 / SIM_FPS:
        grid = step(grid)
        last_update = now

    draw()


