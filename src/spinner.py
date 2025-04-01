import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Initial window size
INITIAL_WIDTH, INITIAL_HEIGHT = 600, 600

# Game options
OPTIONS = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 
           'Orange', 'Pink', 'Brown', 'Cyan', 'Lime']
COLORS = [(255,0,0), (0,0,255), (0,255,0), (255,255,0), 
          (128,0,128), (255,165,0), (255,105,180), 
          (165,42,42), (0,255,255), (50,205,50)]

# Setup resizable Pygame window
screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Wheel Spinner")

# Dynamic variables that update on resize
current_size = (INITIAL_WIDTH, INITIAL_HEIGHT)
center = (INITIAL_WIDTH//2, INITIAL_HEIGHT//2)
radius = min(INITIAL_WIDTH, INITIAL_HEIGHT) // 3  # Responsive radius

# Font system that scales with window size
def get_scaled_font(size_ratio=0.06):
    base_size = min(current_size)
    return pygame.font.Font(None, int(base_size * size_ratio))

font = get_scaled_font()

def handle_resize(new_size):
    """Update all size-dependent variables when window is resized"""
    global current_size, center, radius, font
    current_size = new_size
    center = (current_size[0]//2, current_size[1]//2)
    radius = min(current_size) // 3  # Keep wheel proportional
    font = get_scaled_font()  # Recreate font at new size
    pygame.display.flip()

# Draw Wheel Function (now size-aware)
def draw_wheel(angle):
    screen.fill((255, 255, 255))
    
    # Draw wheel segments
    for i, (option, color) in enumerate(zip(OPTIONS, COLORS)):
        theta1 = (2 * math.pi / len(OPTIONS)) * i + math.radians(angle)
        theta2 = theta1 + (2 * math.pi / len(OPTIONS))
        
        # Calculate segment points
        points = [center]
        for theta in [theta1, theta2]:
            x = center[0] + math.cos(theta) * radius
            y = center[1] + math.sin(theta) * radius
            points.append((x, y))
        pygame.draw.polygon(screen, color, points)
        
        # Draw label (with responsive positioning)
        text = font.render(option, True, (0, 0, 0))
        text_angle = (theta1 + theta2) / 2
        text_x = center[0] + math.cos(text_angle) * (radius * 0.66)  # 2/3 radius
        text_y = center[1] + math.sin(text_angle) * (radius * 0.66)
        screen.blit(text, (text_x - text.get_width()//2, text_y - text.get_height()//2))
    
    # Draw pointer (triangle at top)
    pointer_size = radius * 0.1  # Responsive pointer
    pygame.draw.polygon(screen, (0, 0, 0), [
        (center[0], center[1] - radius - pointer_size),
        (center[0] - pointer_size*1.5, center[1] - radius - pointer_size*3),
        (center[0] + pointer_size*1.5, center[1] - radius - pointer_size*3)
    ])

# Confetti Effect (now window-size aware)
def draw_confetti():
    confetti_size = max(2, min(current_size)//100)  # Responsive confetti
    for _ in range(100):
        x = random.randint(0, current_size[0])
        y = random.randint(0, current_size[1])
        pygame.draw.circle(screen, random.choice(COLORS), (x, y), confetti_size)

# Main Game Loop
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
                spin_speed = random.uniform(10, 20)
                start_time = time.time()
                selected_option = None

    # Handle spinning
    if spinning:
        angle += spin_speed
        spin_speed *= 0.98  # Friction
        if time.time() - start_time > 3:  # 3 second spin
            spinning = False
            normalized_angle = (-angle % 360)
            selected_index = int((normalized_angle + (180/len(OPTIONS))) // (360//len(OPTIONS))) % len(OPTIONS)
            selected_option = OPTIONS[selected_index -3]
            waiting_for_reset = True

    # Drawing
    screen.fill((255, 255, 255))
    draw_wheel(angle)
    
    # Draw result if available
    if selected_option:
        draw_confetti()
        
        # Blinking effect
        if time.time() - blink_timer > 0.5:
            blink_state = not blink_state
            blink_timer = time.time()
        
        if blink_state:
            # Responsive result box
            box_width = current_size[0] // 3
            box_height = current_size[1] // 10
            pygame.draw.rect(screen, (0, 0, 0), 
                           (center[0]-box_width//2, current_size[1]//4-box_height//2, 
                            box_width, box_height))
            pygame.draw.rect(screen, (255, 255, 0), 
                           (center[0]-box_width//2, current_size[1]//4-box_height//2, 
                            box_width, box_height), 3)
            
            # Scaled result text
            result_font = get_scaled_font(0.08)  # Slightly larger font
            result_text = result_font.render(f"{selected_option}!", True, (255, 255, 255))
            screen.blit(result_text, 
                       (center[0] - result_text.get_width()//2, 
                        current_size[1]//4 - result_text.get_height()//2))
    
    # Draw instructions
    instr_font = get_scaled_font(0.04)
    if waiting_for_reset:
        instr_text = instr_font.render("Press SPACE to spin again!", True, (0, 0, 0))
    else:
        instr_text = instr_font.render("Press SPACE to spin!", True, (0, 0, 0))
    screen.blit(instr_text, 
               (center[0] - instr_text.get_width()//2, 
                current_size[1] - instr_text.get_height() - 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()