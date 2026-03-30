import pygame
import sys
import json
import os
import math
import asyncio
import random
from assets import COLORS, CONFIG, SKINS
from snake_logic import Snake, Food, BonusFood

HIGH_SCORE_FILE = 'high_score.json'

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except:
            return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({"high_score": score}, f)

# --- VIP COLOR GAMUTS ---
VIP_GAMUTS = [
    {"head": (255, 255, 255), "body": (200, 200, 200), "food": (255, 255, 0), "bg": (10, 10, 10)},   # Trắng/Bạc
    {"head": (0, 255, 255), "body": (0, 150, 255), "food": (255, 0, 255), "bg": (5, 10, 25)},    # Cyber Blue
    {"head": (255, 0, 100), "body": (150, 0, 50), "food": (0, 255, 100), "bg": (25, 5, 10)},     # Blood Neon
    {"head": (200, 100, 255), "body": (100, 0, 200), "food": (255, 255, 50), "bg": (15, 5, 25)},  # Void Purple
    {"head": (50, 255, 50), "body": (0, 100, 0), "food": (255, 100, 0), "bg": (5, 20, 5)},       # Jungle Tox
    {"head": (255, 200, 50), "body": (210, 105, 30), "food": (0, 255, 255), "bg": (20, 15, 5)}   # Desert Gold
]

def draw_button_rounded(screen, text, font, x, y, w, h, bg_color, text_color, radius=15):
    pygame.draw.rect(screen, bg_color, (x, y, w, h), border_radius=radius)
    text_surf = font.render(text, True, text_color)
    screen.blit(text_surf, (x + (w - text_surf.get_width()) // 2, y + (h - text_surf.get_height()) // 2))

# --- HIỆU ỨNG NEON GLOW CACHE ---
glow_cache = {}
# --- HỆ THỐNG ZERO-CHURN: Surface dùng lại để tránh cấp phát bộ nhớ liên tục ---
glow_temp_surf = None

def get_glow_circle(color, radius, blur):
    key = (color, radius, blur, "circle")
    if key in glow_cache: return glow_cache[key]
    
    if len(glow_cache) > 200: glow_cache.clear()
    
    surf = pygame.Surface((radius*2 + blur*2, radius*2 + blur*2), pygame.SRCALPHA)
    for i in range(blur, 0, -2):
        alpha = int(40 - (40 * (i / blur)))
        pygame.draw.circle(surf, (*color[:3], alpha), (radius+blur, radius+blur), radius + i)
    pygame.draw.circle(surf, color, (radius+blur, radius+blur), radius)
    glow_cache[key] = surf
    return surf

def get_glow_rect(color, w, h, radius, blur):
    key = (color, w, h, radius, blur, "rect")
    if key in glow_cache: return glow_cache[key]
    
    if len(glow_cache) > 200: glow_cache.clear()
    
    surf = pygame.Surface((w + blur*2, h + blur*2), pygame.SRCALPHA)
    for i in range(blur, 0, -2):
        alpha = int(50 - (50 * (i / blur)))
        pygame.draw.rect(surf, (*color[:3], alpha), (blur-i, blur-i, w + i*2, h + i*2), border_radius=radius)
    pygame.draw.rect(surf, color, (blur, blur, w, h), border_radius=radius)
    glow_cache[key] = surf
    return surf

def draw_neon_rect_zero_churn(screen, color, x, y, w, h, radius, blur):
    """Vẽ hào quang mà không tạo Surface mới (Dành cho Skin động)"""
    global glow_temp_surf
    size = (int(w + blur * 2), int(h + blur * 2))
    if glow_temp_surf is None or glow_temp_surf.get_size() != size:
        glow_temp_surf = pygame.Surface(size, pygame.SRCALPHA)
    
    glow_temp_surf.fill((0, 0, 0, 0))
    for i in range(blur, 0, -2):
        alpha = int(50 - (50 * (i / blur)))
        pygame.draw.rect(glow_temp_surf, (*color[:3], alpha), (blur - i, blur - i, w + i * 2, h + i * 2), border_radius=radius)
    pygame.draw.rect(glow_temp_surf, color, (blur, blur, w, h), border_radius=radius)
    screen.blit(glow_temp_surf, (x - blur, y - blur))

def draw_glass_panel(screen, x, y, w, h, color, radius=15, alpha=60):
    # Tạo bề mặt kính mờ (Frosted Glass)
    glass_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # 1. Lớp màu nền mờ
    pygame.draw.rect(glass_surf, (*color[:3], alpha), (0, 0, w, h), border_radius=radius)
    # 2. Chi tiết bắt sáng (Top highlight)
    pygame.draw.line(glass_surf, (255, 255, 255, 50), (radius, 1), (w - radius, 1), 1)
    screen.blit(glass_surf, (x, y))
    # 3. Viền Neon mảnh
    pygame.draw.rect(screen, (*color[:3], 180), (x, y, w, h), border_radius=radius, width=1)

def draw_grid(screen, offset_x, offset_y):
    for x in range(0, CONFIG["play_area_width"] + 1, CONFIG["grid_size"]):
        pygame.draw.line(screen, COLORS["grid_line"], (x + offset_x, offset_y), (x + offset_x, offset_y + CONFIG["play_area_height"]))
    for y in range(0, CONFIG["play_area_height"] + 1, CONFIG["grid_size"]):
        pygame.draw.line(screen, COLORS["grid_line"], (offset_x, y + offset_y), (offset_x + CONFIG["play_area_width"], y + offset_y))

def draw_dpad_arrow(screen, cx, cy, direction, color):
    pygame.draw.circle(screen, COLORS["dpad_btn"], (cx, cy), 35)
    pygame.draw.circle(screen, (60, 60, 60), (cx, cy), 35, width=1) # Anti-aliased outer rim
    if direction == "U":
        pygame.draw.line(screen, color, (cx-12, cy+5), (cx, cy-10), 4)
        pygame.draw.line(screen, color, (cx+12, cy+5), (cx, cy-10), 4)
    elif direction == "D":
        pygame.draw.line(screen, color, (cx-12, cy-5), (cx, cy+10), 4)
        pygame.draw.line(screen, color, (cx+12, cy-5), (cx, cy+10), 4)
    elif direction == "L":
        pygame.draw.line(screen, color, (cx+5, cy-12), (cx-10, cy), 4)
        pygame.draw.line(screen, color, (cx+5, cy+12), (cx-10, cy), 4)
    elif direction == "R":
        pygame.draw.line(screen, color, (cx-5, cy-12), (cx+10, cy), 4)
        pygame.draw.line(screen, color, (cx-5, cy+12), (cx+10, cy), 4)

def draw_neon_orb(screen, color, x, y, size, is_bonus=False):
    # Vẽ mồi phong cách "Đơn giản mà đẹp" (Ngọc Neon)
    ticks = pygame.time.get_ticks()
    cx, cy = x + size // 2, y + size // 2
    
    # Hiệu ứng nhịp thở nhẹ (Breathing)
    pulse = math.sin(ticks * 0.005) * 2
    radius = (size // 2 - 2) + pulse
    
    # 1. Hào quang ngoài cùng (Soft Glow)
    glow_color = (*color[:3], 50)
    pygame.draw.circle(screen, glow_color, (cx, cy), radius + 6)
    
    # 2. Thân ngọc chính
    pygame.draw.circle(screen, color, (cx, cy), radius)
    
    # 3. Điểm nhấn sáng trắng (Core Highlighting)
    pygame.draw.circle(screen, (255, 255, 255), (cx - radius//3, cy - radius//3), radius // 3)
    
    # Nếu là mồi to: thêm một vòng nhẫn Neon mỏng (Halo Ring)
    if is_bonus:
        ring_radius = radius + 8 + math.sin(ticks * 0.01) * 3
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), ring_radius, width=1)


async def main():
    try:
        pygame.init()
        pygame.mixer.init()
        # Tải Âm thanh & Nhạc
        eat_sound = None
        lose_sound = None
        try:
            # Ưu tiên tìm trong thư mục src/
            s_path = os.path.dirname(__file__)
            eat_p = os.path.join(s_path, "eat.wav")
            lose_p = os.path.join(s_path, "lose.wav")
            bgm_p = os.path.join(s_path, "bgm.mp3")
            
            if os.path.exists(eat_p): eat_sound = pygame.mixer.Sound(eat_p)
            if os.path.exists(lose_p): lose_sound = pygame.mixer.Sound(lose_p)
            if os.path.exists(bgm_p):
                pygame.mixer.music.load(bgm_p)
                pygame.mixer.music.set_volume(0.4)
        except Exception as e:
            print(f"Cảnh báo âm thanh: {e}")

        screen = pygame.display.set_mode((CONFIG["screen_width"], CONFIG["screen_height"]))
        pygame.display.set_caption('Snake.IO Cyberpunk Mobile')
        clock = pygame.time.Clock()
        
        # Fonts - Sử dụng các font hỗ trợ Tiếng Việt tốt nhất trên Windows
        font_sm = pygame.font.SysFont(["Arial", "Tahoma", "Segoe UI"], 13, bold=True)
        font_md = pygame.font.SysFont(["Arial", "Tahoma", "Segoe UI"], 28, bold=True)
        btn_font = pygame.font.SysFont(["Arial", "Tahoma", "Segoe UI"], 18, bold=True)
        go_font = pygame.font.SysFont(["Arial", "Tahoma", "Segoe UI"], 55, bold=True, italic=True)

        snake = Snake()
        snake.prev_body = list(snake.body) # Phải khởi tạo prev_body ngay
        food = Food()
        food.randomize_position(snake.body)
        bonus_food = BonusFood()
        
        score = 0
        food_eaten = 0
        normal_food_for_bonus = 0 # Đếm để tạo mồi to
        high_score = load_high_score()
        
        state = "MENU"
        diff_idx = 0 # Mặc định DỄ
        diff_levels = [4.5, 7.2, 10.8]
        diff_texts = ["DỄ", "VỪA", "KHÓ"]
        base_fps = diff_levels[diff_idx]
        current_fps = base_fps
        skin_idx = 6 # Mặc định Skin CHAMELEON VIP
        vip_gamut_idx = 0 
        is_endless = False # Mặc định là có tường (Wall Mode)
        particles = [] # Hệ thống hạt lấp lánh
        stars = [(random.randint(0, CONFIG["play_area_width"]), random.randint(0, CONFIG["play_area_height"]), random.random()) for _ in range(50)]
        is_boosting = False
        running = True
        
        px, py = CONFIG["play_area_x"], CONFIG["play_area_y"]
        accumulated_time = 0
        
        while running:
            # 1. EVENT HANDLING (Chạy ở 60 FPS - Phản hồi cực nhạy)
            dt = clock.tick(60) / 1000.0
            
            # --- HỆ THỐNG ĐIỀU KHIỂN SIÊU NHẠY (CONTINUOUS SENSING) ---
            mx, my = pygame.mouse.get_pos()
            m_pressed = pygame.mouse.get_pressed()[0]
            
            if state == "PLAYING":
                # 1. Kiểm tra Boost (Radius 55px)
                is_boosting = m_pressed and math.hypot(mx - 310, my - 600) <= 55
                
                # 2. Kiểm tra D-Pad với trạng thái cảm ứng thời gian thực (Radius 60px)
                if m_pressed:
                    if math.hypot(mx - 110, my - 560) <= 60: snake.change_direction(0, -CONFIG["grid_size"])
                    elif math.hypot(mx - 110, my - 640) <= 60: snake.change_direction(0, CONFIG["grid_size"])
                    elif math.hypot(mx - 55, my - 600) <= 60: snake.change_direction(-CONFIG["grid_size"], 0)
                    elif math.hypot(mx - 165, my - 600) <= 60: snake.change_direction(CONFIG["grid_size"], 0)
            else:
                is_boosting = False
                
            if state != "PAUSED":
                boost_mult = 2.0 if is_boosting else 1.0
                accumulated_time += dt * boost_mult
            await asyncio.sleep(0) 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if state == "MENU":
                        # <> Nút chuyển Skin
                        if 210 <= y <= 260:
                            if 20 <= x <= 50: # <
                                skin_idx = (skin_idx - 1) % len(SKINS)
                            elif 350 <= x <= 380: # >
                                skin_idx = (skin_idx + 1) % len(SKINS)
                                
                        # Chọn Độ Khó
                        if 340 <= y <= 390:
                            if 50 <= x <= 140: diff_idx = 0; base_fps = diff_levels[0]; current_fps = base_fps
                            elif 150 <= x <= 250: diff_idx = 1; base_fps = diff_levels[1]; current_fps = base_fps
                            elif 260 <= x <= 350: diff_idx = 2; base_fps = diff_levels[2]; current_fps = base_fps
                        
                        # Chọn Chế Độ Bản Đồ (Single Glass Toggle) - y=510-550
                        if 510 <= y <= 550:
                            if 50 <= x <= 350:
                                is_endless = not is_endless



                        
                        # NÚT PLAY KHỔNG LỒ (Trả về vị trí nguyên bản y=430)
                        if 430 <= y <= 490:
                            if 80 <= x <= 320:
                                base_fps = diff_levels[diff_idx]
                                current_fps = base_fps
                                state = "PLAYING"
                                accumulated_time = 0
                                # Bắt đầu nhạc nền khi vào trận
                                try:
                                    if os.path.exists(os.path.join(os.path.dirname(__file__), "bgm.mp3")):
                                        pygame.mixer.music.play(-1)
                                except: pass
                    
                    elif state == "PLAYING":
                        # Nút Pause (Top Right) - Đồng bộ với diện mạo Neon mới
                        if 340 <= x <= 395 and 5 <= y <= 55:
                            state = "PAUSED"



                        
                        # D-Pad bên trái (Tâm x=110, y=600)
                        if math.hypot(x - 110, y - 560) <= 45: snake.change_direction(0, -CONFIG["grid_size"])
                        elif math.hypot(x - 110, y - 640) <= 45: snake.change_direction(0, CONFIG["grid_size"])
                        elif math.hypot(x - 55, y - 600) <= 45: snake.change_direction(-CONFIG["grid_size"], 0)
                        elif math.hypot(x - 165, y - 600) <= 45: snake.change_direction(CONFIG["grid_size"], 0)

                    elif state == "PAUSED":
                        # Cập nhật Hitbox cho Menu Pause Tối giản (y=340, y=400)
                        if 90 <= x <= 310:
                            if 340 <= y <= 390: # TIẾP TỤC
                                state = "PLAYING"
                            elif 400 <= y <= 450: # THOÁT
                                state = "MENU"
                                snake = Snake()
                                snake.prev_body = list(snake.body)
                                score = 0; food_eaten = 0; normal_food_for_bonus = 0; bonus_food.active = False




                    elif state == "GAME_OVER":
                        # Hitbox gọn cho Game Over (y=380, y=440)
                        if 100 <= x <= 300:
                            if 380 <= y <= 430: # CHƠI LẠI
                                snake = Snake()
                                snake.prev_body = list(snake.body)
                                food.randomize_position(snake.body)
                                score = 0; food_eaten = 0; current_fps = base_fps; state = "PLAYING"
                                normal_food_for_bonus = 0
                                bonus_food.active = False
                                # Chơi lại nhạc nền
                                try:
                                    if os.path.exists(os.path.join(os.path.dirname(__file__), "bgm.mp3")):
                                        pygame.mixer.music.play(-1)
                                except: pass
                            elif 440 <= y <= 490: # THOÁT
                                state = "MENU"
                                # Đảm bảo dừng mọi âm thanh khi về Menu
                                pygame.mixer.music.stop()
                                if lose_sound: lose_sound.stop()
                                snake = Snake()
                                snake.prev_body = list(snake.body)
                                score = 0; food_eaten = 0; normal_food_for_bonus = 0; bonus_food.active = False
                    

                                
                elif event.type == pygame.KEYDOWN:
                    if state == "GAME_OVER" and event.key == pygame.K_r:
                        snake = Snake()
                        food.randomize_position(snake.body)
                        score = 0; food_eaten = 0; current_fps = base_fps; state = "PLAYING"
                    elif state == "PLAYING":
                        if event.key == pygame.K_UP: snake.change_direction(0, -CONFIG["grid_size"])
                        elif event.key == pygame.K_DOWN: snake.change_direction(0, CONFIG["grid_size"])
                        elif event.key == pygame.K_LEFT: snake.change_direction(-CONFIG["grid_size"], 0)
                        elif event.key == pygame.K_RIGHT: snake.change_direction(CONFIG["grid_size"], 0)

            # 2. LOGIC UPDATE (Chỉ chạy ở tốc độ game được quy định)
            current_skin = SKINS[skin_idx].copy()
            if current_skin.get("is_vip"):
                # Ghi đè màu từ Gamut VIP hiện tại
                gamut = VIP_GAMUTS[vip_gamut_idx]
                current_skin["head"] = gamut["head"]
                current_skin["body"] = gamut["body"]
                current_skin["food"] = gamut["food"]
                current_skin["bg"] = gamut["bg"]
            else:
                current_skin["bg"] = (10, 10, 10) # Mặc định
                
            if state == "PLAYING":
                # Không cộng dt ở đây nữa vì đã cộng ở đầu vòng lặp
                if accumulated_time >= (1.0 / current_fps):
                    accumulated_time = 0
                    # Cập nhật Logic di chuyển theo chế độ
                    snake.update(is_endless=is_endless)
                    new_head = snake.get_head_pos()
                    
                    # Kiểm tra va chạm tập trung
                    if snake.check_collision(is_endless=is_endless):
                        state = "GAME_OVER"
                        # Dừng nhạc nền và phát âm thanh thua cuộc
                        pygame.mixer.music.stop()
                        if lose_sound: lose_sound.play()
                        
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                    else:
                        # Logic mồi thường
                        if new_head == food.position:
                            snake.grow = True
                            score += 10
                            food_eaten += 1
                            normal_food_for_bonus += 1
                            food.randomize_position(snake.body, bonus_food.position if bonus_food.active else None)
                            if eat_sound: eat_sound.play()
                            
                            # Kích hoạt mồi to sau mỗi 5 mồi thường
                            if normal_food_for_bonus >= 5 and not bonus_food.active:
                                bonus_food.spawn(snake.body, food.position)
                                normal_food_for_bonus = 0
                                if current_skin.get("is_vip"):
                                    vip_gamut_idx = (vip_gamut_idx + 1) % len(VIP_GAMUTS)
                                
                            # Tăng 5% tốc độ mỗi 7 mồi
                            if food_eaten % 7 == 0:
                                current_fps *= 1.05
                                
                        # Logic mồi to (Hồi phục)
                        if bonus_food.active:
                            if new_head == bonus_food.position:
                                snake.grow = True
                                score += 50
                                bonus_food.active = False
                                if eat_sound: eat_sound.play()
                
                # Cập nhật timer mồi to liên tục ở 60 FPS
                if bonus_food.active:
                    bonus_food.timer -= dt
                    if bonus_food.timer <= 0:
                        bonus_food.active = False
                
                # CẬP NHẬT HIỆU ỨNG LẤP LÁNH VIP (60 FPS)
                if current_skin.get("is_vip"):
                    # Cập nhật sao lấp lánh
                    new_stars = []
                    for sx, sy, sbright in stars:
                        nbright = sbright + random.uniform(-0.1, 0.1)
                        nbright = max(0.2, min(1.0, nbright))
                        new_stars.append((sx, sy, nbright))
                    stars = new_stars
                    
                    # Cập nhật hạt lấp lánh (Particles)
                    for p in particles[:]:
                        p['age'] += dt
                        p['y'] -= 10 * dt # Bay nhẹ lên
                        if p['age'] > p['life']:
                            particles.remove(p)
                    
                    # Sinh hạt mới tại đầu rắn (Cập nhật liên tục 60 FPS theo vị trí trượt)
                    interp = min(1.0, accumulated_time / (1.0 / current_fps))
                    hx_grid_curr, hy_grid_curr = snake.body[0]
                    hx_grid_prev, hy_grid_prev = snake.prev_body[0]
                    hx = hx_grid_prev + (hx_grid_curr - hx_grid_prev) * interp
                    hy = hy_grid_prev + (hy_grid_curr - hy_grid_prev) * interp
                    
                    if random.random() < 0.4:
                        particles.append({
                            'x': hx + random.randint(0, 20),
                            'y': hy + random.randint(0, 20),
                            'life': random.uniform(0.5, 1.2),
                            'age': 0,
                            'color': current_skin["head"]
                        })

            # 3. DRAW
            screen.fill(COLORS["background"])

            if state == "MENU":
                go_surf1 = go_font.render("SNAKE", True, COLORS["text"])
                go_surf2 = go_font.render(".IO", True, current_skin["body"])
                # Center Logo manually
                logo_w = go_surf1.get_width() + go_surf2.get_width()
                start_x = (CONFIG["screen_width"] - logo_w) // 2
                screen.blit(go_surf1, (start_x, 40))
                screen.blit(go_surf2, (start_x + go_surf1.get_width(), 40))

                # --- SKIN SHOWCASE CARD ---
                showcase_rect = (60, 130, 280, 210)
                pygame.draw.rect(screen, (15, 15, 15), showcase_rect, border_radius=20)
                pygame.draw.rect(screen, (50, 50, 50), showcase_rect, border_radius=20, width=1)
                
                # Skin Label (Màu của skin)
                skin_label = font_md.render(current_skin["name"], True, current_skin["head"])
                screen.blit(skin_label, (CONFIG["screen_width"]//2 - skin_label.get_width()//2, 145))

                # Artist Snake 'S' Shape inside Showcase
                cx, cy = 200, 250
                gs = CONFIG["grid_size"]
                f_glow = get_glow_circle(current_skin["food"], gs//2, 10)
                screen.blit(f_glow, (cx - 30 - gs//2 - 10, cy + 10 - gs//2 - 10))
                
                # Vẽ rắn tĩnh 'S' ngoằn ngoèo với hiệu ứng Skin tương ứng
                showcase_body = [
                    (cx - 30, cy - 30), (cx - 10, cy - 30), (cx + 10, cy - 30), (cx + 30, cy - 30),
                    (cx + 30, cy - 10), (cx + 10, cy - 10), (cx - 10, cy - 10), (cx - 10, cy + 10), 
                    (cx - 10, cy + 30), (cx + 10, cy + 30), (cx + 30, cy + 30)
                ]
                s_blur = 5
                ticks = pygame.time.get_ticks()
                for i, segment in enumerate(showcase_body):
                    # --- RENDERING SKIN TRONG MENU (Tối ưu ZERO-CHURN) ---
                    s_color = current_skin["head"] if i == 0 else current_skin["body"]
                    seg_gs = gs
                    is_dynamic = False
                    
                    if current_skin.get("is_gradient"):
                        hue = (ticks * 0.1 + i * 20) % 360
                        c = pygame.Color(0); c.set_hsla((hue, 100, 60, 100))
                        s_color = (c.r, c.g, c.b)
                        is_dynamic = True
                    
                    seg_x, seg_y = segment[0], segment[1]
                    if current_skin.get("is_glitch"):
                        is_dynamic = True
                        if random.random() < 0.05:
                            seg_x += random.randint(-1, 1); seg_y += random.randint(-1, 1)
                            if random.random() < 0.5: s_color = (random.randint(100, 255), 255, 255)
                    
                    if current_skin.get("is_dragon") and i % 2 == 0:
                        seg_gs += 4; seg_x -= 2; seg_y -= 2

                    if is_dynamic:
                        # Dùng Direct Draw để tránh tạo Surface mới
                        draw_neon_rect_zero_churn(screen, s_color, seg_x, seg_y, seg_gs-2, seg_gs-2, 4, s_blur)
                    else:
                        # Dùng Cache cho Skin tĩnh
                        s_glow = get_glow_rect(s_color, seg_gs-2, seg_gs-2, 4, s_blur)
                        if current_skin.get("is_ghost"): s_glow.set_alpha(120)
                        screen.blit(s_glow, (seg_x + 1 - s_blur, seg_y + 1 - s_blur))
                    
                    if i == 0: # Eyes
                        pygame.draw.circle(screen, (0,0,0), (int(seg_x + (seg_gs//2) - 4), int(seg_y + 6)), 2)
                        pygame.draw.circle(screen, (0,0,0), (int(seg_x + (seg_gs//2) + 4), int(seg_y + 6)), 2)

                # Nút < > viền nổi ngoài Showcase
                draw_button_rounded(screen, "<", font_md, 20, 210, 30, 50, (10, 10, 10), current_skin["body"], 10)
                pygame.draw.rect(screen, (60, 60, 60), (20, 210, 30, 50), border_radius=10, width=1)
                draw_button_rounded(screen, ">", font_md, 350, 210, 30, 50, (10, 10, 10), current_skin["body"], 10)
                pygame.draw.rect(screen, (60, 60, 60), (350, 210, 30, 50), border_radius=10, width=1)

                # --- BẢNG ĐỘ KHÓ (SWITCHES) ---
                diff_rects = [(50, 350, 90, 40), (150, 350, 100, 40), (260, 350, 90, 40)]
                for i, rect in enumerate(diff_rects):
                    bg_color = current_skin["body"] if diff_idx == i else (20, 20, 20)
                    txt_color = COLORS["text_dark"] if diff_idx == i else COLORS["text"]
                    draw_button_rounded(screen, diff_texts[i], btn_font, rect[0], rect[1], rect[2], rect[3], bg_color, txt_color, 20)
                    if diff_idx != i:
                        pygame.draw.rect(screen, (70, 70, 70), rect, border_radius=20, width=1)

                # --- NÚT PLAY GỌN (VÀO CHƠI) ---
                play_rect = (100, 430, 200, 50)
                draw_button_rounded(screen, "VÀO CHƠI", btn_font, play_rect[0], play_rect[1], play_rect[2], play_rect[3], current_skin["head"], COLORS["text_dark"], 25)

                # --- NÚT CHẾ ĐỘ BẢN ĐỒ GỌN ---
                m_txt = "BẢN ĐỒ: VÔ TẬN" if is_endless else "BẢN ĐỒ: CỔ ĐIỂN"
                m_glow_col = (0, 150, 255) if is_endless else (80, 80, 100)
                draw_button_rounded(screen, m_txt, font_sm, 100, 495, 200, 35, (25, 25, 30), COLORS["text"], 15)
                pygame.draw.rect(screen, m_glow_col, (100, 495, 200, 35), border_radius=15, width=1)






            elif state == "PLAYING" or state == "GAME_OVER" or state == "PAUSED":
                ticks = pygame.time.get_ticks()
                # --- PHẦN LOGO TRUNG TÂM (SNAKE.IO NEON) ---
                logo_glow_val = int(180 + 75 * math.sin(ticks * 0.004))
                l1_color = (*current_skin["head"][:3], logo_glow_val)
                logo_font_main = pygame.font.SysFont(["Arial", "Tahoma", "Segoe UI"], 32, bold=True)
                logo1 = logo_font_main.render("SNAKE", True, l1_color)
                logo2 = logo_font_main.render(".IO", True, (255, 255, 255, logo_glow_val))
                total_w = logo1.get_width() + logo2.get_width()
                lx = (CONFIG["screen_width"] - total_w) // 2
                screen.blit(logo1, (lx, 12))
                screen.blit(logo2, (lx + logo1.get_width(), 12))
                
                # --- NÚT PAUSE (CHẾ ĐỘ GLASS MỜ) ---
                p_cx, p_cy = 368, 30
                p_rad = 18
                p_glow = get_glow_circle(current_skin["head"], p_rad, 10 if math.sin(ticks*0.01)>0 else 5)
                screen.blit(p_glow, (p_cx - p_rad - 10, p_cy - p_rad - 10))
                p_surf = pygame.Surface((p_rad*2, p_rad*2), pygame.SRCALPHA)
                pygame.draw.circle(p_surf, (25, 25, 35, 150), (p_rad, p_rad), p_rad)
                screen.blit(p_surf, (p_cx - p_rad, p_cy - p_rad))
                pygame.draw.circle(screen, current_skin["head"], (p_cx, p_cy), p_rad, width=2)
                pygame.draw.rect(screen, (255, 255, 255), (p_cx - 5, p_cy - 7, 3, 14), border_radius=2)
                pygame.draw.rect(screen, (255, 255, 255), (p_cx + 2, p_cy - 7, 3, 14), border_radius=2)




                
                # --- BẢNG THÔNG SỐ GLASS PANEL ---
                panel_x, panel_y, panel_w, panel_h = px, 55, 360, 55
                draw_glass_panel(screen, panel_x, panel_y, panel_w, panel_h, current_skin["head"], radius=12, alpha=45)
                sc_val = font_md.render(f"{score:03d}", True, (255, 255, 255))
                screen.blit(font_sm.render("SCORE", True, (200, 200, 200)), (panel_x + 15, panel_y + 8))
                screen.blit(sc_val, (panel_x + 15, panel_y + 22))
                hs_val = font_sm.render(f"{high_score}", True, current_skin["head"])
                screen.blit(font_sm.render("BEST", True, (150, 150, 150)), (panel_x + panel_w // 2 - 20, panel_y + 10))
                screen.blit(hs_val, (panel_x + panel_w // 2 - hs_val.get_width() // 2, panel_y + 28))
                vel_val = font_md.render(f"x{(current_fps/10):.1f}", True, current_skin["food"])
                screen.blit(font_sm.render("SPEED", True, current_skin["food"]), (panel_x + panel_w - 75, panel_y + 8))
                screen.blit(vel_val, (panel_x + panel_w - vel_val.get_width() - 15, panel_y + 22))

                # --- PLAY AREA CARD (Nhúng viền Outline) ---
                play_rect = (px, py, CONFIG["play_area_width"], CONFIG["play_area_height"])
                pygame.draw.rect(screen, current_skin["bg"], play_rect, border_radius=20)
                
                # Vẽ sao lấp lánh trong sân đấu VIP
                if current_skin.get("is_vip"):
                    for sx, sy, sbright in stars:
                        s_color = tuple(int(c * sbright) for c in current_skin["head"])
                        pygame.draw.circle(screen, s_color, (sx + px, sy + py), 1)

                pygame.draw.rect(screen, (35, 35, 35), play_rect, border_radius=20, width=1) # Glass Outline
                
                # Thiết lập Clip để lưới và vật thể không tràn ra viền bo tròn
                screen.set_clip(pygame.Rect(*play_rect))
                draw_grid(screen, px, py)

                # Vẽ Food Neo (Ngọc Neon Tối Giản)
                fx, fy = food.position
                gs = CONFIG["grid_size"]
                draw_neon_orb(screen, current_skin["food"], fx + px, fy + py, gs)

                # Vẽ Bonus Food (Ngọc Neon To có Vòng Halo)
                if bonus_food.active:
                    bfx, bfy = bonus_food.position
                    draw_neon_orb(screen, current_skin["food"], bfx + px, bfy + py, gs, is_bonus=True)
                    
                    # Vẽ Timer Bar cho mồi to
                    bar_w = int((bonus_food.timer / 5.0) * (CONFIG["play_area_width"] - 40))
                    pygame.draw.rect(screen, (30, 30, 30), (px + 20, py + 5, CONFIG["play_area_width"] - 40, 4), border_radius=2)
                    pygame.draw.rect(screen, current_skin["food"], (px + 20, py + 5, bar_w, 4), border_radius=2)

                    
                    # Vẽ Timer Bar cho mồi to
                    bar_w = int((bonus_food.timer / 5.0) * (CONFIG["play_area_width"] - 40))
                    pygame.draw.rect(screen, (30, 30, 30), (px + 20, py + 5, CONFIG["play_area_width"] - 40, 4), border_radius=2)
                    pygame.draw.rect(screen, current_skin["food"], (px + 20, py + 5, bar_w, 4), border_radius=2)

                # Vẽ Snake Neo (Hệ thống Interpolation - Di chuyển trượt 100% mượt mà)
                s_blur = 6
                interp = min(1.0, accumulated_time / (1.0 / current_fps)) if state == "PLAYING" else 0
                
                for index in range(len(snake.body)):
                    curr_pos = snake.body[index]
                    # Nếu segment cũ có tồn tại ở Frame trước, chúng ta Trượt nó. 
                    if index < len(snake.prev_body):
                        prev_pos = snake.prev_body[index]
                        dist_x = curr_pos[0] - prev_pos[0]
                        dist_y = curr_pos[1] - prev_pos[1]
                        
                        if abs(dist_x) > CONFIG["grid_size"] or abs(dist_y) > CONFIG["grid_size"]:
                            # Khoảnh khắc xuyên tường, không interpolation để tránh bị kéo dãn toàn màn hình
                            sx, sy = curr_pos
                        else:
                            sx = prev_pos[0] + dist_x * interp
                            sy = prev_pos[1] + dist_y * interp
                    else:
                        sx, sy = curr_pos
                    
                    # --- RENDERING SKIN TRONG TRẬN (ZERO-CHURN) ---
                    color = current_skin["head"] if index == 0 else current_skin["body"]
                    seg_gs = gs
                    is_dynamic = False
                    
                    # 1. RAINBOW GRADIENT
                    if current_skin.get("is_gradient"):
                        hue = (ticks * 0.15 + index * 12) % 360
                        c = pygame.Color(0); c.set_hsla((hue, 100, 50, 100))
                        color = (c.r, c.g, c.b)
                        is_dynamic = True
                    
                    # 2. GLITCH
                    seg_x, seg_y = sx, sy
                    if current_skin.get("is_glitch"):
                        is_dynamic = True
                        if random.random() < 0.08:
                            seg_x += random.randint(-2, 2); seg_y += random.randint(-2, 2)
                            if random.random() < 0.2: color = (random.randint(100, 255), 0, random.randint(150, 255))
                    
                    # 3. DRAGON
                    if current_skin.get("is_dragon") and index % 2 == 0:
                        seg_gs += 4; seg_x -= 2; seg_y -= 2

                    # CHỌN PHƯƠNG THỨC VẼ TỐI ƯU
                    if is_dynamic:
                        draw_neon_rect_zero_churn(screen, color, seg_x + px, seg_y + py, seg_gs-2, seg_gs-2, 4, s_blur)
                    else:
                        snake_glow = get_glow_rect(color, seg_gs-2, seg_gs-2, radius=4, blur=s_blur)
                        if current_skin.get("is_ghost"): snake_glow.set_alpha(150)
                        screen.blit(snake_glow, (seg_x + px + 1 - s_blur, seg_y + py + 1 - s_blur))
                    
                    if index == 0:
                        e_x, e_y = seg_x + px, seg_y + py
                        pygame.draw.circle(screen, (0, 0, 0), (int(e_x + (seg_gs//2) - 4), int(e_y + 6)), 2)
                        pygame.draw.circle(screen, (0, 0, 0), (int(e_x + (seg_gs//2) + 4), int(e_y + 6)), 2)
                if current_skin.get("is_vip"):
                    for p in particles:
                        alpha = int(255 * (1 - p['age'] / p['life']))
                        p_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
                        pygame.draw.circle(p_surf, (*p['color'], alpha), (1, 1), 1)
                        screen.blit(p_surf, (p['x'] + px, p['y'] + py))
                
                screen.set_clip(None) # Gỡ bỏ giới hạn khung vẽ

                # D-Pad Gọn bên trái
                draw_dpad_arrow(screen, 110, 560, "U", current_skin["body"])
                draw_dpad_arrow(screen, 110, 640, "D", current_skin["body"])
                draw_dpad_arrow(screen, 55, 600, "L", current_skin["body"])
                draw_dpad_arrow(screen, 165, 600, "R", current_skin["body"])

                # --- NÚT BOOST bên phải ---
                b_cx, b_cy = 310, 600
                b_color = current_skin["food"] if is_boosting else current_skin["head"]
                b_alpha = 180 if is_boosting else 100
                b_radius = 45
                
                # Hào quang nút Boost
                b_glow = get_glow_circle(b_color, b_radius, 15 if is_boosting else 10)
                screen.blit(b_glow, (b_cx - b_radius - 15, b_cy - b_radius - 15))
                
                # Thân nút Boost
                pygame.draw.circle(screen, (30, 30, 40, b_alpha), (b_cx, b_cy), b_radius)
                pygame.draw.circle(screen, b_color, (b_cx, b_cy), b_radius, width=2)
                
                b_txt = font_sm.render("BOOST", True, b_color)
                screen.blit(b_txt, (b_cx - b_txt.get_width()//2, b_cy - b_txt.get_height()//2))

                if state == "GAME_OVER":
                    # Màn hình kết thúc tối giản
                    overlay = pygame.Surface((CONFIG["screen_width"], CONFIG["screen_height"]), pygame.SRCALPHA)
                    overlay.fill((5, 5, 10, 190))
                    screen.blit(overlay, (0, 0))
                    
                    go_rect = (80, 200, 240, 280)
                    pygame.draw.rect(screen, (25, 25, 35), go_rect, border_radius=20)
                    pygame.draw.rect(screen, (70, 70, 80), go_rect, border_radius=20, width=1)
                    
                    lbl = btn_font.render("KẾT QUẢ", True, (150, 150, 150))
                    screen.blit(lbl, (CONFIG["screen_width"]//2 - lbl.get_width()//2, 230))
                    
                    sc_val = font_md.render(f"ĐIỂM: {score}", True, current_skin["head"])
                    screen.blit(sc_val, (CONFIG["screen_width"]//2 - sc_val.get_width()//2, 270))
                    
                    hs_txt = font_sm.render(f"KỶ LỤC: {high_score}", True, (150, 150, 150))
                    screen.blit(hs_txt, (CONFIG["screen_width"]//2 - hs_txt.get_width()//2, 315))
                    
                    draw_button_rounded(screen, "CHƠI LẠI", btn_font, 100, 360, 200, 45, current_skin["head"], COLORS["text_dark"], 20)
                    draw_button_rounded(screen, "THOÁT", btn_font, 100, 420, 200, 45, (45, 45, 55), (200, 200, 200), 20)

                if state == "PAUSED":
                    # Màn hình tạm dừng tối giản
                    pause_overlay = pygame.Surface((CONFIG["screen_width"], CONFIG["screen_height"]), pygame.SRCALPHA)
                    pause_overlay.fill((5, 5, 10, 180))
                    screen.blit(pause_overlay, (0, 0))
                    
                    p_rect = (80, 250, 240, 200)
                    pygame.draw.rect(screen, (25, 25, 35), p_rect, border_radius=20)
                    pygame.draw.rect(screen, current_skin["head"], p_rect, border_radius=20, width=1)
                    
                    p_txt = btn_font.render("TẠM DỪNG", True, current_skin["head"])
                    screen.blit(p_txt, (CONFIG["screen_width"]//2 - p_txt.get_width()//2, 280))
                    
                    draw_button_rounded(screen, "TIẾP TỤC", btn_font, 100, 330, 200, 45, current_skin["head"], COLORS["text_dark"], 20)
                    draw_button_rounded(screen, "THOÁT", btn_font, 100, 390, 200, 45, (45, 45, 55), (200, 200, 200), 20)






            pygame.display.flip()
            
    except Exception as e:
        print(f"Lỗi hệ thống lập trình Neon: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Đã có vòng lặp đang chạy (môi trường Web/Pygbag)
        asyncio.ensure_future(main())
