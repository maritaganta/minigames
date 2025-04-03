import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

mario = "Roll Again"
luigi = "5 \n ~ 3 cans "
peach = "-3 \n or drink"
bowser = "attack ~ 2 cans"
wario = "2 \n ~ 1 can"
waluigi = "-1 \n or drink"

# Initial window size
INITIAL_WIDTH, INITIAL_HEIGHT = 600, 600

OPTIONS = [
    mario, 
    luigi, 
    peach, 
    # 'Yoshi', 
    # 'Toad', 
    bowser, 
    wario, 
    waluigi, 
    # 'Daisy', 
    # 'Rosalina'
]

COLORS = [
    (255, 0, 0),       # Mario red
    (0, 180, 0),       # Luigi green
    (255, 180, 220),   # Peach pink
    # (100, 255, 100),   # Yoshi green
    # (255, 220, 150),   # Toad tan
    (200, 100, 0),     # Bowser orange
    (255, 255, 0),     # Wario yellow
    (100, 0, 180),     # Waluigi purple
    # (255, 200, 0),     # Daisy yellow
    # (150, 200, 255)    # Rosalina blue
]

# Setup resizable Pygame window
screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mario Power-Up Spinner")

# Load Mario assets
try:
    background_img = pygame.image.load("./data/mario_wheel.jpeg").convert()
except:
    background_img = None

# Dynamic variables
current_size = (INITIAL_WIDTH, INITIAL_HEIGHT)
center = (INITIAL_WIDTH//2, INITIAL_HEIGHT//2)
radius = min(INITIAL_WIDTH, INITIAL_HEIGHT) // 3

# Mario-themed fonts
try:
    mario_font = pygame.font.Font("super_mario.ttf", 36)
except:
    mario_font = pygame.font.Font(None, 36)

def get_scaled_font(size_ratio=0.06):
    base_size = min(current_size)
    try:
        return pygame.font.Font("super_mario.ttf", int(base_size * size_ratio))
    except:
        return pygame.font.Font(None, int(base_size * size_ratio))

font = get_scaled_font()

def handle_resize(new_size):
    global current_size, center, radius, font
    current_size = new_size
    center = (current_size[0]//2, current_size[1]//2)
    radius = min(current_size) // 3
    font = get_scaled_font()
    if background_img:
        scaled_bg = pygame.transform.scale(background_img, current_size)
    pygame.display.flip()

def draw_wheel(angle):
    if background_img:
        screen.blit(pygame.transform.scale(background_img, current_size), (0, 0))
    else:
        screen.fill((80, 80, 255))  # Mario sky blue
    
    # Draw wheel with question block pattern
    pygame.draw.circle(screen, (255, 200, 0), center, radius + 10)  # Gold border
    pygame.draw.circle(screen, (255, 255, 255), center, radius)     # White base
    
    # Draw segments with Mario sprites if available
    for i, (option, color) in enumerate(zip(OPTIONS, COLORS)):
        theta1 = (2 * math.pi / len(OPTIONS)) * i + math.radians(angle)
        theta2 = theta1 + (2 * math.pi / len(OPTIONS))
        
        points = [center]
        for theta in [theta1, theta2]:
            x = center[0] + math.cos(theta) * radius
            y = center[1] + math.sin(theta) * radius
            points.append((x, y))
        pygame.draw.polygon(screen, color, points)
        
        # Draw item names
        text = font.render(option, True, (0, 0, 0))
        text_angle = (theta1 + theta2) / 2
        text_x = center[0] + math.cos(text_angle) * (radius * 0.6)
        text_y = center[1] + math.sin(text_angle) * (radius * 0.6)
        screen.blit(text, (text_x - text.get_width()//2, text_y - text.get_height()//2))

    # Draw Pointer
    pointer_size = radius * 0.1
    pygame.draw.polygon(screen, (255, 0, 0), [
        (center[0], center[1] - radius - pointer_size),
        (center[0] - pointer_size*1.5, center[1] - radius - pointer_size*3),
        (center[0] + pointer_size*1.5, center[1] - radius - pointer_size*3)
    ])

def draw_confetti():
    confetti_shapes = ['circle', 'square', 'star']
    for _ in range(100):
        x = random.randint(0, current_size[0])
        y = random.randint(0, current_size[1])
        shape = random.choice(confetti_shapes)
        color = random.choice(COLORS)
        size = random.randint(2, 8)
        
        if shape == 'circle':
            pygame.draw.circle(screen, color, (x, y), size)
        elif shape == 'square':
            pygame.draw.rect(screen, color, (x, y, size, size))
        elif shape == 'star':
            points = [
                (x, y-size), (x+size//3, y-size//3), (x+size, y),
                (x+size//3, y+size//3), (x, y+size),
                (x-size//3, y+size//3), (x-size, y),
                (x-size//3, y-size//3)
            ]
            pygame.draw.polygon(screen, color, points)


def draw_winner_box(selected_option, blink_state):
    # Box dimensions based on screen size
    box_width = current_size[0] // 2
    box_height = current_size[1] // 5
    
    # Mario-style box colors
    box_color = (255, 215, 0) if blink_state else (255, 180, 0)  # Gold/Orange blink
    border_color = (255, 50, 50)  # Mario red border
    
    # Draw the main box (question block inspired)
    pygame.draw.rect(screen, box_color, 
                    (center[0] - box_width//2, current_size[1]//4 - box_height//2,
                     box_width, box_height), border_radius=10)
    
    # Draw the border (thicker when blinking)
    border_width = 5 if blink_state else 3
    pygame.draw.rect(screen, border_color, 
                    (center[0] - box_width//2, current_size[1]//4 - box_height//2,
                     box_width, box_height), border_width, border_radius=10)
    
    # Draw the winning text (with Mario-style outline)
    result_font = get_scaled_font(0.09)
    text_surface = result_font.render(f"{selected_option}!", True, (255, 255, 255))
    
    # Text outline effect
    for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
        outline = result_font.render(f"{selected_option}!", True, (0, 0, 0))
        screen.blit(outline, (center[0] - outline.get_width()//2 + dx*2,
                            current_size[1]//4 - outline.get_height()//2 + dy*2))
    
    screen.blit(text_surface, (center[0] - text_surface.get_width()//2,
                             current_size[1]//4 - text_surface.get_height()//2))

# Sound effects
try:
    spin_sound = pygame.mixer.Sound("./data/mario_spin.wav")
    win_sound = pygame.mixer.Sound("./data/mario_win.wav")
    has_sound = True
except:
    has_sound = False

# Main Game Loop (same as before but with sound additions)
running = True
spinning = False
angle = 0
selected_option = None
waiting_for_reset = False
clock = pygame.time.Clock()
blink_state = True
blink_timer = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            handle_resize((event.w, event.h))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if waiting_for_reset:
                waiting_for_reset = False
                selected_option = None
            else:
                spinning = True
                if has_sound: spin_sound.play()
                spin_speed = random.uniform(10, 20)
                start_time = time.time()
                selected_option = None

    # Handle spinning
    if spinning:
        angle += spin_speed
        spin_speed *= 0.98
        if time.time() - start_time > 3:
            spinning = False
            if has_sound: win_sound.play()
            normalized_angle = (-angle % 360)
            selected_index = int((normalized_angle + (180/len(OPTIONS))) // (360//len(OPTIONS))) % len(OPTIONS)
            selected_option = OPTIONS[selected_index - 2]
            waiting_for_reset = True

    # Drawing
    draw_wheel(angle)
    
    if selected_option:
        draw_confetti()
        
        if time.time() - blink_timer > 0.5:
            blink_state = not blink_state
            blink_timer = time.time()
        
        if blink_state:
            draw_winner_box(selected_option, blink_state)

    
    # Draw instructions with Mario font
    instr_font = get_scaled_font(0.04)
    if waiting_for_reset:
        instr_text = instr_font.render("Press SPACE to spin again!", True, (255, 255, 255))
    else:
        instr_text = instr_font.render("Press SPACE to spin!", True, (255, 255, 255))
    
    # Add Mario-style text shadow
     # Draw instructions with Mario font
    instr_font = get_scaled_font(0.04)
    if waiting_for_reset:
        text_content = "Press SPACE to spin again!"
    else:
        text_content = "Press SPACE to spin!"
    
    # Render both shadow and main text
    shadow_text = instr_font.render(text_content, True, (0, 0, 0))
    instr_text = instr_font.render(text_content, True, (255, 255, 255))
    
    # Add Mario-style text shadow
    screen.blit(shadow_text, (center[0] - shadow_text.get_width()//2 + 2, 
                            current_size[1] - shadow_text.get_height() - 18))
    screen.blit(instr_text, (center[0] - instr_text.get_width()//2, 
                           current_size[1] - instr_text.get_height() - 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()