# ===== Nhập thư viện cần thiết =====
import pygame
import random
import math
import time
import sys
import os

# ===== KHỞI TẠO PYGAME =====
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
# Lấy đường dẫn thư mục chứa file code hiện tại
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_path(folder, filename):
    """Hàm hỗ trợ lấy đường dẫn file an toàn trên mọi máy"""
    return os.path.join(script_dir, folder, filename)

# ===== LOAD ICON GAME =====
try:
    # Tìm file logo trong thư mục images
    icon_path = get_path('images', 'logo.png')
    if os.path.exists(icon_path):
        programIcon = pygame.image.load(icon_path)
        pygame.display.set_icon(programIcon)
        print("-> Đã load Icon thành công!")
    else:
        print(f"-> Cảnh báo: Không tìm thấy logo tại {icon_path}")
except Exception as e:
    print(f"-> Lỗi load icon: {e}")

# ===== ÂM THANH =====
SOUNDS = {
    'click': pygame.mixer.Sound('sounds/click.wav'),
    'correct': pygame.mixer.Sound('sounds/correct.wav'),
    'wrong': pygame.mixer.Sound('sounds/wrong.wav'),
    'drop': pygame.mixer.Sound('sounds/drop.wav'),
    'over': pygame.mixer.Sound('sounds/over.wav')
}
SOUNDS['miss'] = SOUNDS['wrong']  # Dùng chung âm thanh với 'wrong'

# Điều chỉnh volume
VOLUMES = {'click': 0.5, 'correct': 0.6, 'wrong': 0.7, 'drop': 0.5, 'over': 0.8}
for key, vol in VOLUMES.items():
    SOUNDS[key].set_volume(vol)

# ===== MÀU SẮC =====
COLORS = {
    'bg': (35, 20, 75),
    'wall': (255, 197, 103),
    'pacman': (255, 197, 103),
    'ghost_red': (253, 90, 70),
    'dot': (255, 240, 245),
    'text': (255, 255, 255),
    'ui_bg': (85, 44, 183),
    'ui_border': (255, 255, 255),
    'flash_red': (253, 90, 70),
    'white': (240, 240, 240),
    'dark_gray': (60, 40, 100),
    'gray': (150, 160, 180),
    'numeric': (255, 215, 0),
    'string': (30, 210, 100),
    'boolean': (0, 180, 255),
    'error': (255, 69, 0)
}

# ===== MÀN HÌNH =====
SIZE = 700
screen = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("Data Drag - Pixel Edition")
clock = pygame.time.Clock()
center_x = SIZE // 2

# ===== FONT =====
title_font = pygame.font.Font(None, 72)
font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
title_font.set_bold(True)
font.set_bold(True)
button_font.set_bold(True)

# ===== TRẠNG THÁI GAME =====
MENU, GAME, HOW_TO_PLAY, ABOUT, CREDITS, HIGH_SCORE, GAME_OVER = range(7)
current_state = MENU

# ===== BIẾN GAME =====
score = 0
lives = 4
highest_score = 0
level = 1
flash_timer = 0
popup_timer = 0
start_time = 0
is_flashing = False
popup_message = ""
blocks = []
spawn_timer = 0
game_active_types = ["numeric", "string"]
targets = {}

# ===== DỮ LIỆU =====
DATA_POOL = {
    "numeric": ["12", "3.14", "56", "0", "-7", "100", "42", "3.1415", "1e3", "2.5e-2", "3E+8", "0b1010", "0xFF", "0o77", "1000000", "999.999", "-999", ".5", "3.", "00.00", " 123", "45 ", " 67  "],
    "string": ["Boy", "Cat", "hello", "world", "text", "python", "code", "btran", "bhan", "đhuy", "ueh", "data", "DA", "@name", "#tag", "$money", "hello_world", "' '", "'  '", "a1b2", "3items", "test123", "456abc", "'hello'", '"world"', '"null"', "'123'",'"undefined"', '"True"', '"False"'],
    "boolean": ["True", "False", "TRUE", "FALSE", "true", "false", "5 > 2", "3 == 4", "a == b", "x != y", "10 <= 20", "1 < 0", "5 >= 5", "100 == 100", "True && False", "False || True", "!True", "0", "1", "yes", "no", "on", "off", "==", "!=", ">=", "<="],
    "error": ["null", "??", "error", "NaN", "inf", "[2,3,]", "{key:}", "(1+2", "3+*4", "12.34.56", "0xGG", "0b123", "0o89", "5 / 0", "sqrt(-1)", "log(0)", "5 + 'hello'", "'a' - 1", "null + 5", "undefined", "not defined", "TRUEE", "FALS", "5 >> 2", "3 <<< 1"]
}

# ===== CẤU HÌNH BOX =====
BOX_W, BOX_H, BOX_Y, SPACING = 140, 60, SIZE - 100, 20

# ===== LỚP DATA BLOCK =====
class DataBlock:
    def __init__(self, dtype):
        self.dtype = dtype
        self.text = random.choice(DATA_POOL[dtype])
        self.rect = pygame.Rect(random.randint(100, SIZE - 200), -40, 90, 40)
        self.speed = random.uniform(1.0, 1.5)
        self.angle = random.uniform(0, math.pi * 2)
        self.dragging = False
        self.offset = (0, 0)

    def update(self):
        if not self.dragging:
            self.rect.y += self.speed
            self.rect.x += math.sin(self.angle) * 0.5
            self.angle += 0.02

    def draw(self):
        pygame.draw.rect(screen, COLORS['dark_gray'], self.rect, border_radius=4)
        pygame.draw.rect(screen, COLORS['gray'], self.rect.inflate(-4, -4), border_radius=3)
        txt = small_font.render(self.text, True, COLORS['white'])
        screen.blit(txt, txt.get_rect(center=self.rect.center))

# ===== LỚP BUTTON =====
class ArcadeButton:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        self.glow = 0
       
    def update(self):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        self.current_color = self.hover_color if self.hovered else self.color
        self.glow = min(self.glow + 0.2, 1) if self.hovered else max(self.glow - 0.1, 0)
           
    def draw(self, surface):
        if self.glow > 0:
            glow_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.hover_color[:3], int(100 * self.glow)),
            (0, 0, self.rect.width + 20, self.rect.height + 20), border_radius=15)
            surface.blit(glow_surf, (self.rect.x - 10, self.rect.y - 10))
       
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        border_color = tuple(min(c + 50, 255) for c in self.current_color)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=10)
       
        text_surf = button_font.render(self.text, True, COLORS['text'])
        shadow_surf = button_font.render(self.text, True, (50, 50, 100))
        text_rect = text_surf.get_rect(center=self.rect.center)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
       
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)
       
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# ===== TẠO BUTTONS =====
button_width, button_height, button_spacing = 250, 60, 20
start_y = 250

# Tạo các button menu
start_button = ArcadeButton(
    center_x - button_width // 2, start_y,
    button_width, button_height,
    "START", (30, 210, 100), (60, 230, 130)
)

highscore_button = ArcadeButton(
    center_x - button_width // 2, start_y + button_height + button_spacing,
    button_width, button_height,
    "HIGHEST SCORE", (0, 180, 255), (100, 220, 255)
)

howto_button = ArcadeButton(
    center_x - button_width // 2, start_y + (button_height + button_spacing) * 2,
    button_width, button_height,
    "HOW TO PLAY", (255, 215, 0), (255, 240, 100)
)

about_button = ArcadeButton(
    center_x - button_width // 2, start_y + (button_height + button_spacing) * 3,
    button_width, button_height,
    "ABOUT", (255, 105, 180), (255, 150, 200)
)

credits_button = ArcadeButton(
    center_x - button_width // 2, start_y + (button_height + button_spacing) * 4,
    button_width, button_height,
    "CREDITS", (255, 69, 0), (255, 100, 50)
)

menu_buttons = [start_button, highscore_button, howto_button, about_button, credits_button]
back_button = ArcadeButton(40, 40, 120, 45, "BACK", (253, 90, 70), (255, 130, 110))
restart_button = ArcadeButton(SIZE//2 - 100, 380, 200, 50, "PLAY AGAIN", (30, 210, 100), (60, 230, 130))
menu_button_g = ArcadeButton(SIZE//2 - 100, 450, 200, 50, "MENU", (0, 180, 255), (100, 220, 255))

# ===== HÀM TIỆN ÍCH =====
def calculate_box_positions(types):
    if not types: return {}
    total_width = len(types) * BOX_W + (len(types) - 1) * SPACING
    start_x = (SIZE - total_width) // 2
    return {t: pygame.Rect(start_x + i * (BOX_W + SPACING), BOX_Y, BOX_W, BOX_H) for i, t in enumerate(types)}

def draw_arcade_background():
    for y in range(50, SIZE, 40):
        for x in range(50, SIZE, 40):
            pygame.draw.circle(screen, COLORS['dot'], (x, y), 2)
    pygame.draw.rect(screen, COLORS['wall'], (30, 30, SIZE - 60, SIZE - 60), 5, border_radius=10)

def draw_title_screen(title, subtitle=""):
    title_shadow = title_font.render(title, True, (180, 100, 0))
    title_main = title_font.render(title, True, (255, 197, 103))
    title_x, title_y = center_x, 120
    
    for offset in [(2, 2), (3, 3), (4, 4)]:
        screen.blit(title_shadow, (title_x - title_shadow.get_width() // 2 + offset[0], title_y + offset[1]))
    screen.blit(title_main, (title_x - title_main.get_width() // 2, title_y))
    
    if subtitle:
        sub = small_font.render(subtitle, True, COLORS['pacman'])
        screen.blit(sub, (center_x - sub.get_width() // 2, title_y + 70))

def draw_info_screen(title, title_color, lines, start_y=100, line_spacing=30):
    screen.fill(COLORS['bg'])
    draw_arcade_background()
    title_surf = font.render(title, True, title_color)
    screen.blit(title_surf, (center_x - title_surf.get_width()//2, 57))
    
    for i, line in enumerate(lines):
        text = small_font.render(line, True, COLORS['white'])
        screen.blit(text, (center_x - text.get_width()//2, start_y + i * line_spacing))
    
    back_button.update()
    back_button.draw(screen)

# ===== CÁC MÀN HÌNH =====
def draw_menu():
    screen.fill(COLORS['bg'])
    draw_arcade_background()
    draw_title_screen("DATA DRAG", "ARCADE EDITION")
    
    for button in menu_buttons:
        button.update()
        button.draw(screen)

def draw_how_to_play():
    lines = [
        "Drag gray blocks to matching boxes:",
        "",
        "NUMERIC: Valid numbers only",
        "STRING: Text or numbers as text",
        "BOOLEAN: True/False or comparisons",
        "ERROR: Invalid or malformed data",
        "",
        "Correct: +10 points",
        "Wrong: -1 life (screen flashes red)",
        "Missed: -1 life",
        "",
        "Boxes appear gradually as you play."
    ]
    draw_info_screen("HOW TO PLAY", COLORS['pacman'], lines, 120, 32)

def draw_about():
    lines = [
        "Data Drag - Educational Game",
        "",
        "Final project for",
        "Computer Science 1",
        "",
        "Purpose:",
        "- Teach data types",
        "- Practice logic",
        "- Educational fun",
        "",
        "For programming beginners."
    ]
    draw_info_screen("ABOUT", (180, 0, 180), lines, 100, 30)

def draw_credits():
    lines = [
        "DEVELOPED BY:",
        "Hoang Bao Tran",
        "Le Huynh Duc Huy",
        "Nguyen Bao Han",
        "",
        "WITH HELP FROM:",
        "AI Assistants &",
        "Online Resources"
    ]
    draw_info_screen("CREDITS", (100, 100, 150), lines, 100, 35)

def draw_high_score():
    screen.fill(COLORS['bg'])
    draw_arcade_background()
    title = font.render("HIGH SCORE", True, (0, 150, 200))
    screen.blit(title, (center_x - title.get_width()//2, 57))
    
    score_text = font.render(str(highest_score), True, COLORS['pacman'])
    screen.blit(score_text, (center_x - score_text.get_width()//2, 150))
    
    back_button.update()
    back_button.draw(screen)

def draw_game():
    global lives, score, highest_score, level, blocks, spawn_timer, game_active_types, targets
    global flash_timer, is_flashing, popup_message, popup_timer
    
    screen.fill(COLORS['bg'])
    
    if is_flashing:
        flash_alpha = min(flash_timer, 30)
        flash_surface = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        flash_surface.fill((255, 50, 50, flash_alpha))
        screen.blit(flash_surface, (0, 0))
        flash_timer -= 2
        if flash_timer <= 0:
            is_flashing = False
    
    draw_arcade_background()
    
    elapsed = time.time() - start_time if start_time else 0
    game_active_types = ["numeric", "string"] if elapsed < 20 else \
                       ["numeric", "string", "boolean"] if elapsed < 40 else \
                       ["numeric", "string", "boolean", "error"]
    
    targets = calculate_box_positions(game_active_types)
    level = 1 + int(elapsed // 30)
    
    # UI Panel
    panel_rect = pygame.Rect(30, 30, SIZE - 60, 70)
    pygame.draw.rect(screen, COLORS['ui_bg'], panel_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS['ui_border'], panel_rect, 3, border_radius=8)
    
    # Score
    score_surf = font.render(f"SCORE: {score:06d}", True, COLORS['pacman'])
    screen.blit(score_surf, (60, 50))
    
    # Level
    level_surf = small_font.render(f"LEVEL {level}", True, (0, 200, 255))
    screen.blit(level_surf, (center_x - level_surf.get_width() // 2, 45))
    
    # Lives
    screen.blit(small_font.render("LIVES:", True, COLORS['text']), (SIZE - 250, 55))
    for i in range(lives):
        ghost_x, ghost_y = SIZE - 180 + i * 35, 62
        pygame.draw.circle(screen, COLORS['ghost_red'], (ghost_x, ghost_y), 12)
        pygame.draw.circle(screen, (255, 255, 255), (ghost_x - 4, ghost_y - 4), 4)
        pygame.draw.circle(screen, (255, 255, 255), (ghost_x + 4, ghost_y - 4), 4)
    
    # Time
    time_text = font.render(f"TIME: {int(elapsed)}s", True, COLORS['white'])
    screen.blit(time_text, (center_x - time_text.get_width()//2, 60))
    
    # Target boxes
    for t, rect in targets.items():
        color = COLORS[t]
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['ui_border'], rect, 3, border_radius=10)
        
        label = small_font.render(t.upper(), True, (20, 20, 40))
        label_rect = label.get_rect(center=rect.center)
        shadow = small_font.render(t.upper(), True, (240, 240, 255, 100))
        screen.blit(shadow, (label_rect.x + 1, label_rect.y + 1))
        screen.blit(label, label_rect)
    
    # Update blocks
    blocks[:] = [b for b in blocks if b.dtype in game_active_types]
    
    spawn_timer += 1
    if spawn_timer > 60 and len(blocks) < 5 and game_active_types:
        blocks.append(DataBlock(random.choice(game_active_types)))
        spawn_timer = 0
    
    # Process blocks
    for b in blocks[:]:
        try:
            b.update()
            b.draw()
            
            if b.rect.y > SIZE + 50:
                SOUNDS['miss'].play()
                lives -= 1
                blocks.remove(b)
                is_flashing = True
                flash_timer = 30
        except:
            blocks.remove(b)
    
    # Popup message
    if popup_timer > 0:
        progress = 1 - (popup_timer / 40)
        y_offset = int(progress * 50)
        popup_y = 300 - y_offset
        color = (0, 255, 0) if "+" in popup_message else (255, 0, 0)
        popup_text = small_font.render(popup_message, True, color)
        screen.blit(popup_text, (center_x - popup_text.get_width()//2, popup_y))
        popup_timer -= 1
    
    if lives <= 0:
        if score > highest_score:
            highest_score = score
        SOUNDS['over'].play()
        return "GAME_OVER"
    
    return "CONTINUE"

def draw_game_over():
    screen.fill(COLORS['bg'])
    draw_arcade_background()
    
    game_over_shadow = title_font.render("GAME OVER", True, (150, 0, 0))
    game_over_main = title_font.render("GAME OVER", True, COLORS['ghost_red'])
    screen.blit(game_over_shadow, (center_x - game_over_shadow.get_width() // 2 + 3, 153))
    screen.blit(game_over_main, (center_x - game_over_main.get_width() // 2, 150))
    
    score_surf = font.render(f"SCORE: {score:06d}", True, COLORS['pacman'])
    screen.blit(score_surf, (center_x - score_surf.get_width() // 2, 250))
    
    if score == highest_score:
        record_surf = button_font.render("NEW HIGH SCORE!", True, (0, 255, 0))
        screen.blit(record_surf, (center_x - record_surf.get_width() // 2, 300))
    
    high_surf = font.render(f"BEST: {highest_score:06d}", True, (0, 200, 255))
    screen.blit(high_surf, (center_x - high_surf.get_width() // 2, 340))
    
    restart_button.update()
    menu_button_g.update()
    restart_button.draw(screen)
    menu_button_g.draw(screen)

def reset_game():
    global score, lives, blocks, spawn_timer, start_time, level
    global game_active_types, flash_timer, is_flashing, popup_message, popup_timer, targets
    
    score = 0
    lives = 4
    level = 1
    flash_timer = 0
    popup_timer = 0
    spawn_timer = 0
    blocks = []
    start_time = time.time()
    game_active_types = ["numeric", "string"]
    is_flashing = False
    popup_message = ""
    targets = {}

# ===== VÒNG LẶP CHÍNH =====
running = True
try:
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Xử lý sự kiện theo trạng thái
            if current_state == MENU:
                for button in menu_buttons:
                    button.update()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = GAME
                        reset_game()
                    elif highscore_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = HIGH_SCORE
                    elif howto_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = HOW_TO_PLAY
                    elif about_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = ABOUT
                    elif credits_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = CREDITS
            
            elif current_state in [HOW_TO_PLAY, ABOUT, CREDITS, HIGH_SCORE]:
                back_button.update()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = MENU
            
            elif current_state == GAME_OVER:
                restart_button.update()
                menu_button_g.update()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = GAME
                        reset_game()
                    elif menu_button_g.is_clicked(event):
                        SOUNDS['click'].play()
                        current_state = MENU
                        reset_game()
            
            elif current_state == GAME:
                mouse_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for b in blocks:
                        if b.rect.collidepoint(mouse_pos):
                            b.dragging = True
                            SOUNDS['drop'].play()
                            b.offset = (b.rect.x - mouse_pos[0], b.rect.y - mouse_pos[1])
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    for b in blocks[:]:
                        if b.dragging:
                            b.dragging = False
                            made_mistake = False
                            
                            for t, box in targets.items():
                                if box.colliderect(b.rect):
                                    if t == b.dtype:
                                        score += 10
                                        popup_message = "+10"
                                        SOUNDS['correct'].play()
                                        popup_timer = 40
                                    else:
                                        lives -= 1
                                        made_mistake = True
                                        popup_message = "-1"
                                        SOUNDS['wrong'].play()
                                        popup_timer = 25
                                    
                                    if b in blocks:
                                        blocks.remove(b)
                                    break
                            
                            if made_mistake:
                                is_flashing = True
                                flash_timer = 30
                
                elif event.type == pygame.MOUSEMOTION:
                    for b in blocks:
                        if b.dragging:
                            b.rect.x = mouse_pos[0] + b.offset[0]
                            b.rect.y = mouse_pos[1] + b.offset[1]
        
        # Vẽ màn hình
        if current_state == MENU:
            draw_menu()
        elif current_state == HOW_TO_PLAY:
            draw_how_to_play()
        elif current_state == ABOUT:
            draw_about()
        elif current_state == CREDITS:
            draw_credits()
        elif current_state == HIGH_SCORE:
            draw_high_score()
        elif current_state == GAME:
            result = draw_game()
            if result == "GAME_OVER":
                current_state = GAME_OVER
        elif current_state == GAME_OVER:
            draw_game_over()
        
        pygame.display.flip()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    pygame.quit()
    sys.exit()