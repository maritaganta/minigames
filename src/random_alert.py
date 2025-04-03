import pygame
import time
import os
import random

# Initialize pygame
pygame.init()

# File paths - added os.path.join for better path handling
background_path = os.path.join("data", "mario_background.jpg")
font_path = os.path.join("data", "super_mario_font.ttf")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (227, 38, 54)        # Mario red
GREEN = (76, 187, 23)      # Mario green
BLUE = (0, 120, 255)       # Mario blue
DARK_RED = (180, 30, 30)   # Darker red for hover
DARK_GREEN = (50, 150, 50) # Darker green for hover
DARK_BLUE = (0, 80, 200)   # Darker blue for hover

# Initialize screen
screen = pygame.display.set_mode((400, 200), pygame.RESIZABLE)
pygame.display.set_caption("Mario Elapsed Time Clock")

# Load assets with better error handling
try:
    background = pygame.image.load(background_path)
except:
    print(f"Could not load background image at {background_path}")
    background = pygame.Surface((400, 200))
    background.fill((100, 100, 100))  # Fallback gray background

# Load fonts with better error handling
try:
    main_font = pygame.font.Font(font_path, 100)
    button_font = pygame.font.Font(font_path, 30)
    print("Successfully loaded custom font")
except Exception as e:
    print(f"Could not load custom font at {font_path}: {e}")
    print("Using system fonts as fallback")
    main_font = pygame.font.SysFont('Arial', 100, bold=True)
    button_font = pygame.font.SysFont('Arial', 30, bold=True)

# Load sound
try:
    beer_sound_path = os.path.join("data", "alert.mp3")
    beer_sound = pygame.mixer.Sound(beer_sound_path)
except:
    beer_sound = None

running = False
start_time = 0
elapsed_time = 0
next_beer_alert = time.time() + random.randint(1200, 1800)  # First alert between 20-30 minutes
show_beer_alert = False
beer_alert_start_time = 0
blink_state = False  # For blinking effect
blink_timer = 0

class Button:
    def __init__(self, rel_x, rel_y, rel_w, rel_h, color, hover_color, text, action):
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.rel_w = rel_w
        self.rel_h = rel_h
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text = text
        self.action = action
        self.rect = None
        self.hovering = False

    def update_rect(self, width, height):
        self.rect = pygame.Rect(
            int(self.rel_x * width),
            int(self.rel_y * height),
            int(self.rel_w * width),
            int(self.rel_h * height)
        )

    def draw(self, screen, font):
        # Draw button with rounded corners
        radius = min(15, self.rect.height // 3)
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=radius)
        
        # Draw white border
        border_rect = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, WHITE, border_rect, border_radius=radius-2, width=2)
        
        # Render text with automatic sizing
        text_surface = self._render_text(font)
        if text_surface:
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def _render_text(self, base_font):
        """Render text that fits the button"""
        max_width = self.rect.width * 0.9  # 90% of button width
        max_height = self.rect.height * 0.7  # 70% of button height
        
        # Try with the base font first
        text_surface = base_font.render(self.text, True, WHITE)
        if text_surface.get_width() <= max_width and text_surface.get_height() <= max_height:
            return text_surface
            
        # If too big, find the right size
        font_size = base_font.get_height()
        while font_size > 8:  # Minimum font size
            font_size -= 1
            try:
                font = pygame.font.Font(font_path, font_size)
            except:
                font = pygame.font.SysFont('Arial', font_size, bold=True)
            text_surface = font.render(self.text, True, WHITE)
            if text_surface.get_width() <= max_width and text_surface.get_height() <= max_height:
                return text_surface
        
        return None  # Couldn't find a suitable size

    def check_hover(self, pos):
        self.hovering = self.rect.collidepoint(pos) if self.rect else False
        self.current_color = self.hover_color if self.hovering else self.color
        return self.hovering

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()

# Timer functions (unchanged)
def start_timer():
    global running, start_time
    if not running:
        running = True
        start_time = time.time() - elapsed_time

def pause_timer():
    global running, elapsed_time
    if running:
        running = False
        elapsed_time = time.time() - start_time

def reset_timer():
    global running, elapsed_time
    running = False
    elapsed_time = 0

# Create buttons
buttons = [
    Button(0.1, 0.65, 0.25, 0.25, GREEN, DARK_GREEN, "START", start_timer),
    Button(0.4, 0.65, 0.25, 0.25, RED, DARK_RED, "PAUSE", pause_timer),
    Button(0.7, 0.65, 0.25, 0.25, BLUE, DARK_BLUE, "RESET", reset_timer)
]

# Main game loop
running_game = True
clock = pygame.time.Clock()

while running_game:
    current_time = time.time()
    screen.fill(WHITE)
    width, height = screen.get_size()
    
    # Draw background (scaled to window size)
    screen.blit(pygame.transform.scale(background, (width, height)), (0, 0))

    # Check for Beer O'Clock
    if not show_beer_alert and current_time >= next_beer_alert:
        show_beer_alert = True
        beer_alert_start_time = current_time
        next_beer_alert = current_time + random.randint(1200, 1800)  # Schedule next alert
        if beer_sound:
            beer_sound.play()
    
    if show_beer_alert:
        # Handle blinking effect (every 0.5 seconds)
        if current_time - beer_alert_start_time > 45:  # Show alert for 45 seconds
            show_beer_alert = False
            blink_state = False
        elif current_time - blink_timer > 0.5:
            blink_state = not blink_state
            blink_timer = current_time
        
        if blink_state:
            # Render beer alert text
            beer_text = "BEER O'CLOCK!"
            beer_font_size = max(30, height // 6)
            try:
                beer_font = pygame.font.Font(font_path, beer_font_size)
            except:
                beer_font = pygame.font.SysFont('Arial', beer_font_size, bold=True)
            
            beer_surface = beer_font.render(beer_text, True, RED)
            screen.blit(beer_surface, ((width - beer_surface.get_width()) // 2,
                                      (height - beer_surface.get_height()) // 2))
    else:
        # Normal timer display (only show when not in beer alert)
        # Adjust main font size
        main_font_size = max(30, height // 6)
        try:
            main_font = pygame.font.Font(font_path, main_font_size)
        except:
            main_font = pygame.font.SysFont('Arial', main_font_size, bold=True)
        
        # Calculate and display time
        elapsed = time.time() - start_time if running else elapsed_time
        hours, rem = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(rem, 60)
        time_text = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        # Render time with shadow
        shadow_surface = main_font.render(time_text, True, BLACK)
        text_surface = main_font.render(time_text, True, WHITE)
        screen.blit(shadow_surface, (width//2 - shadow_surface.get_width()//2 + 3, 
                                   height//4 + 3))
        screen.blit(text_surface, (width//2 - text_surface.get_width()//2, 
                                 height//4))
        
        # Handle buttons (only show when not in beer alert)
        button_font_size = max(20, min(width, height) // 15)
        try:
            button_font = pygame.font.Font(font_path, button_font_size)
        except:
            button_font = pygame.font.SysFont('Arial', button_font_size, bold=True)
        
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update_rect(width, height)
            button.check_hover(mouse_pos)
            button.draw(screen, button_font)
    
    pygame.display.flip()
    clock.tick(60)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_game = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and not show_beer_alert:
            # Only process button clicks when not in beer alert
            for button in buttons:
                button.check_click(event.pos)

pygame.quit()