# Màu sắc (R, G, B) chung
COLORS = {
    "background": (12, 12, 12),
    "grid_line": (40, 40, 40),
    "text": (255, 255, 255),
    "text_dark": (10, 10, 10),
    "button": (57, 255, 20),
    "button_dark": (35, 35, 35),
    "panel": (20, 20, 20),
    "dpad_btn": (25, 25, 25)
}

# Các bộ áo của rắn (Skin)
SKINS = [
    {
        "name": "NEON CLASSIC",
        "head": (150, 255, 100),
        "body": (57, 255, 20),
        "food": (255, 0, 255)
    },
    {
        "name": "SYNTHWAVE",
        "head": (255, 0, 128),     # Hot Pink viền 80s
        "body": (0, 191, 255),     # Deep Sky Blue
        "food": (255, 255, 0)      # Vàng rực sáng
    },
    {
        "name": "AMETHYST VOID",
        "head": (210, 100, 255),   # Tím sáng
        "body": (138, 43, 226),    # Tím Violet đậm
        "food": (0, 255, 127)      # Xanh ngọc 
    },
    {
        "name": "CRIMSON CYBER",
        "head": (255, 100, 100),
        "body": (255, 50, 0),
        "food": (0, 255, 255)
    },
    {
        "name": "FROSTBITE",
        "head": (255, 255, 255),
        "body": (0, 200, 255),
        "food": (255, 200, 0)
    },
    {
        "name": "GOLDEN EMPEROR",
        "head": (255, 230, 0),     # Vàng chói
        "body": (218, 165, 32),    # Vàng hoàng gia rực
        "food": (255, 69, 0)       # Cam cháy
    },
    {
        "name": "CHAMELEON VIP",
        "head": (255, 255, 255),
        "body": (200, 200, 200),
        "food": (255, 255, 255),
        "is_vip": True
    },
    {
        "name": "GLITCH MONSTER",
        "head": (255, 0, 50),
        "body": (0, 255, 100),
        "food": (255, 255, 0),
        "is_vip": True,
        "is_glitch": True
    },
    {
        "name": "GHOST PHANTOM",
        "head": (0, 255, 255),
        "body": (0, 150, 255),
        "food": (255, 255, 255),
        "is_vip": True,
        "is_ghost": True
    },
    {
        "name": "CYBER DRAGON",
        "head": (255, 150, 0),
        "body": (255, 50, 50),
        "food": (0, 255, 0),
        "is_dragon": True
    },
    {
        "name": "RAINBOW FLOW",
        "head": (255, 255, 255),
        "body": (255, 255, 255),
        "food": (255, 255, 255),
        "is_gradient": True
    }
]

# Cấu hình game (Mô phỏng App)
CONFIG = {
    "screen_width": 400,
    "screen_height": 700,
    "play_area_width": 360,
    "play_area_height": 360,
    "play_area_x": 20,
    "play_area_y": 120,
    "grid_size": 20,
    "fps": 15
}
