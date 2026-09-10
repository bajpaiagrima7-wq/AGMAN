import pygame
import random
import math
import json
import array
from pathlib import Path

# ============================================================
# AGMAN - Stage 5
# Python 3.12 + pygame-ce
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AGMAN")
clock = pygame.time.Clock()

# ------------------------- FONTS -----------------------------

TITLE_FONT = pygame.font.Font(None, 100)
HEADING_FONT = pygame.font.Font(None, 52)
BUTTON_FONT = pygame.font.Font(None, 38)
HUD_FONT = pygame.font.Font(None, 31)
SMALL_FONT = pygame.font.Font(None, 26)
TINY_FONT = pygame.font.Font(None, 21)

# ------------------------- COLOURS ---------------------------

WHITE = (245, 245, 255)
BLACK = (12, 12, 18)
RED = (255, 70, 90)
YELLOW = (255, 220, 70)
ORANGE = (255, 135, 40)
XP_COLOUR = (120, 255, 220)
SOFT_GREY = (185, 190, 210)

# -------------------------- THEMES ---------------------------

THEMES = {
    "CYBER BLUE": {
        "background": (6, 8, 24),
        "grid": (20, 28, 55),
        "star": (105, 125, 190),
        "accent": (0, 240, 255),
        "accent_2": (175, 90, 255),
        "panel": (18, 22, 44),
        "monster_body": (0, 220, 240),
        "monster_belly": (175, 255, 255),
    },
    "PINK BLAST": {
        "background": (18, 6, 24),
        "grid": (52, 20, 58),
        "star": (200, 120, 210),
        "accent": (255, 70, 180),
        "accent_2": (120, 240, 255),
        "panel": (40, 16, 46),
        "monster_body": (255, 95, 185),
        "monster_belly": (255, 210, 235),
    },
    "TOXIC LIME": {
        "background": (8, 18, 10),
        "grid": (24, 46, 24),
        "star": (140, 210, 140),
        "accent": (120, 255, 90),
        "accent_2": (0, 255, 200),
        "panel": (18, 35, 20),
        "monster_body": (120, 255, 90),
        "monster_belly": (220, 255, 200),
    },
}

THEME_NAMES = list(THEMES.keys())

# Difficulty is deliberately based mainly on ENEMY SPEED.
# Easy = slower enemies, Medium = normal enemies, Hard = faster enemies.
DIFFICULTIES = {
    "EASY":   {"enemy_speed": 0.70},
    "MEDIUM": {"enemy_speed": 1.00},
    "HARD":   {"enemy_speed": 1.40},
}

# -------------------------- SAVE FILE ------------------------

SAVE_DIR = Path.home() / ".agman"
SAVE_FILE = SAVE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "character": "MONSTER",
    "theme_index": 0,
    "display_mode": "DARK",
    "brightness": 82,
    "volume": 55,
    "music": True,
    "difficulty": "MEDIUM",
    "high_score": 0,
}


def load_settings():
    data = DEFAULT_SETTINGS.copy()
    try:
        if SAVE_FILE.exists():
            loaded = json.loads(SAVE_FILE.read_text())
            if isinstance(loaded, dict):
                data.update(loaded)
    except Exception:
        pass

    data["character"] = data["character"] if data["character"] in ("MONSTER", "HUMAN") else "MONSTER"
    data["theme_index"] = max(0, min(len(THEME_NAMES) - 1, int(data["theme_index"])))
    data["display_mode"] = data["display_mode"] if data["display_mode"] in ("DARK", "LIGHT") else "DARK"
    data["brightness"] = max(20, min(100, int(data["brightness"])))
    data["volume"] = max(0, min(100, int(data["volume"])))
    data["music"] = bool(data["music"])
    data["difficulty"] = data["difficulty"] if data["difficulty"] in DIFFICULTIES else "MEDIUM"
    data["high_score"] = max(0, int(data["high_score"]))
    return data


settings = load_settings()


def save_settings():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "character": character_choice,
        "theme_index": selected_theme_index,
        "display_mode": display_mode,
        "brightness": brightness,
        "volume": int(master_volume * 100),
        "music": music_enabled,
        "difficulty": selected_difficulty,
        "high_score": high_score,
    }
    try:
        SAVE_FILE.write_text(json.dumps(payload, indent=2))
    except Exception:
        pass


# --------------------------- AUDIO ---------------------------

audio_ok = True
try:
    pygame.mixer.quit()
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
except pygame.error:
    audio_ok = False


def make_tone(freq, duration, strength=0.15):
    if not audio_ok:
        return None
    sample_rate = 44100
    count = int(sample_rate * duration)
    samples = array.array("h")
    for i in range(count):
        fade = 1 - (i / max(1, count))
        value = int(
            32767
            * strength
            * fade
            * math.sin(2 * math.pi * freq * i / sample_rate)
        )
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_ambient_loop():
    if not audio_ok:
        return None
    sample_rate = 44100
    duration = 1.8
    count = int(sample_rate * duration)
    samples = array.array("h")
    for i in range(count):
        t = i / sample_rate
        env = 0.55 + 0.45 * math.sin(2 * math.pi * 0.55 * t)
        wave = (
            math.sin(2 * math.pi * 110 * t) * 0.45
            + math.sin(2 * math.pi * 165 * t) * 0.25
            + math.sin(2 * math.pi * 220 * t) * 0.12
        )
        samples.append(int(32767 * 0.025 * env * wave))
    return pygame.mixer.Sound(buffer=samples.tobytes())


shoot_sound = make_tone(720, 0.055, 0.12)
hit_sound = make_tone(210, 0.07, 0.12)
level_sound = make_tone(980, 0.18, 0.16)
boss_sound = make_tone(115, 0.38, 0.20)
ambient_sound = make_ambient_loop()

master_volume = settings["volume"] / 100
music_enabled = settings["music"]


def update_audio():
    for sound in (shoot_sound, hit_sound, level_sound, boss_sound):
        if sound:
            sound.set_volume(master_volume)

    if ambient_sound:
        ambient_sound.set_volume(master_volume * 0.32)
        if music_enabled and not pygame.mixer.get_busy():
            ambient_sound.play(loops=-1)
        elif not music_enabled:
            ambient_sound.stop()


update_audio()
if ambient_sound and music_enabled:
    ambient_sound.play(loops=-1)

# ------------------------- SETTINGS --------------------------

character_choice = settings["character"]
selected_theme_index = settings["theme_index"]
display_mode = settings["display_mode"]
brightness = settings["brightness"]
selected_difficulty = settings["difficulty"]
high_score = settings["high_score"]

# ------------------------ BACKGROUND -------------------------

stars = [
    [
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3),
        random.uniform(10, 40),
    ]
    for _ in range(125)
]

# -------------------------- PLAYER ---------------------------

player = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_radius = 24
player_speed = 330
max_health = 100
health = 100

# -------------------------- ATTACK ---------------------------

fireballs = []
fire_particles = []
fireball_speed = 780
fireball_radius = 7
fireball_damage = 1
shoot_delay = 150
last_shot = 0
multishot = 1

# ---------------------------- XP -----------------------------

xp_gems = []
xp = 0
level = 1
xp_needed = 50
upgrade_options = []
upgrade_card_rects = []

UPGRADES = [
    ("RAPID FIRE", "Fire 18% faster"),
    ("FIRE POWER", "+1 fire damage"),
    ("SWIFT FEET", "+45 movement speed"),
    ("BIG HEART", "+25 max HP + heal"),
    ("TRIPLE FLAME", "Add another fire stream"),
    ("GIANT FLAME", "Increase flame size"),
]

# -------------------------- ENEMIES --------------------------

enemies = []
last_enemy_spawn = 0
base_enemy_spawn_delay = 900

ENEMY_TYPES = {
    "BLOB": {
        "radius": 20,
        "speed": 95,
        "health": 2,
        "damage": 10,
        "score": 10,
        "xp": 10,
        "body": (255, 75, 170),
        "belly": (255, 200, 225),
    },
    "BAT": {
        "radius": 16,
        "speed": 150,
        "health": 1,
        "damage": 10,
        "score": 15,
        "xp": 12,
        "body": (170, 110, 255),
        "belly": (220, 205, 255),
    },
    "TANK": {
        "radius": 28,
        "speed": 72,
        "health": 5,
        "damage": 20,
        "score": 30,
        "xp": 20,
        "body": (80, 255, 170),
        "belly": (205, 255, 235),
    },
    "BOSS": {
        "radius": 52,
        "speed": 64,
        "health": 40,
        "damage": 30,
        "score": 250,
        "xp": 70,
        "body": (255, 95, 55),
        "belly": (255, 220, 120),
    },
}

# ------------------------- GAME STATE ------------------------

score = 0
wave = 1
wave_timer = 0.0
boss_waves_spawned = set()

announcement_text = ""
announcement_timer = 0.0

game_state = "MENU"
menu_buttons = {}
settings_rects = {}
rule_back_rect = pygame.Rect(0, 0, 0, 0)
pause_rects = {}
gameover_rects = {}

# ============================================================
# HELPERS
# ============================================================


def clamp(value, low, high):
    return max(low, min(high, value))


def theme():
    return THEMES[THEME_NAMES[selected_theme_index]]


def text_colour():
    return BLACK if display_mode == "LIGHT" else WHITE


def muted_colour():
    return (75, 80, 100) if display_mode == "LIGHT" else SOFT_GREY


def panel_colour():
    return (230, 233, 242) if display_mode == "LIGHT" else theme()["panel"]


def grid_colour():
    return (210, 214, 228) if display_mode == "LIGHT" else theme()["grid"]


def current_background_colour():
    b = brightness / 100
    if display_mode == "LIGHT":
        base = (250, 251, 255)
        return tuple(int(c * (0.60 + 0.40 * b)) for c in base)

    base = theme()["background"]
    return tuple(int(c * (0.30 + 0.70 * b)) for c in base)


def announce(message, seconds=1.8):
    global announcement_text, announcement_timer
    announcement_text = message
    announcement_timer = seconds


def draw_glow_circle(surface, colour, position, radius):
    radius = max(1, int(radius))
    glow_size = radius * 7
    glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    center = glow_size // 2
    pygame.draw.circle(glow, (*colour, 18), (center, center), radius * 3)
    pygame.draw.circle(glow, (*colour, 45), (center, center), radius * 2)
    pygame.draw.circle(glow, colour, (center, center), radius)
    surface.blit(
        glow,
        (int(position[0] - center), int(position[1] - center)),
    )


def draw_button(rect, label, active=False, accent=None, font=None):
    accent = accent or theme()["accent"]
    font = font or SMALL_FONT
    hover = rect.collidepoint(pygame.mouse.get_pos())

    fill = panel_colour()
    if active or hover:
        if display_mode == "DARK":
            fill = theme()["accent_2"]
        else:
            fill = (216, 221, 242)

    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(
        screen,
        accent,
        rect,
        3 if active else 2,
        border_radius=14,
    )

    txt = font.render(label, True, text_colour())
    screen.blit(txt, txt.get_rect(center=rect.center))


def draw_slider(rect, value, label):
    pct = clamp(value / 100, 0, 1)

    label_text = SMALL_FONT.render(
        f"{label}: {int(value)}%",
        True,
        text_colour(),
    )
    screen.blit(label_text, (rect.x, rect.y - 32))

    pygame.draw.rect(screen, grid_colour(), rect, border_radius=8)

    fill = pygame.Rect(rect.x, rect.y, int(rect.width * pct), rect.height)
    pygame.draw.rect(screen, theme()["accent"], fill, border_radius=8)

    knob_x = rect.x + int(rect.width * pct)
    pygame.draw.circle(screen, text_colour(), (knob_x, rect.centery), 11)
    pygame.draw.circle(screen, theme()["accent"], (knob_x, rect.centery), 8)


def draw_background(dt):
    screen.fill(current_background_colour())
    star_colour = theme()["star"] if display_mode == "DARK" else (150, 155, 175)

    for star in stars:
        star[1] += star[3] * dt
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

        pygame.draw.circle(
            screen,
            star_colour,
            (int(star[0]), int(star[1])),
            star[2],
        )


def draw_grid():
    colour = grid_colour()
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, colour, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, colour, (0, y), (WIDTH, y))


def aim_direction():
    mouse = pygame.Vector2(pygame.mouse.get_pos())
    direction = mouse - player
    if direction.length() == 0:
        return pygame.Vector2(1, 0)
    return direction.normalize()


# ============================================================
# CHARACTERS
# ============================================================


def draw_monster(pos, scale=1.0, aiming=True):
    x, y = int(pos[0]), int(pos[1])
    r = int(24 * scale)
    aim = aim_direction() if aiming else pygame.Vector2(1, 0)

    draw_glow_circle(screen, theme()["accent"], (x, y), r + 2)

    left_ear = [
        (x - int(14 * scale), y - int(10 * scale)),
        (x - int(24 * scale), y - int(30 * scale)),
        (x - int(5 * scale), y - int(18 * scale)),
    ]
    right_ear = [
        (x + int(14 * scale), y - int(10 * scale)),
        (x + int(24 * scale), y - int(30 * scale)),
        (x + int(5 * scale), y - int(18 * scale)),
    ]

    pygame.draw.polygon(screen, theme()["monster_body"], left_ear)
    pygame.draw.polygon(screen, theme()["monster_body"], right_ear)
    pygame.draw.circle(screen, theme()["monster_body"], (x, y), r)
    pygame.draw.circle(
        screen,
        theme()["monster_belly"],
        (x, y + int(8 * scale)),
        max(5, int(12 * scale)),
    )

    eye_r = max(3, int(6 * scale))
    pupil_r = max(1, int(2 * scale))
    eye_dx = int(8 * scale)
    eye_y = y - int(5 * scale)
    pupil_x = int(aim.x * 2 * scale)
    pupil_y = int(aim.y * 2 * scale)

    pygame.draw.circle(screen, WHITE, (x - eye_dx, eye_y), eye_r)
    pygame.draw.circle(screen, WHITE, (x + eye_dx, eye_y), eye_r)
    pygame.draw.circle(
        screen,
        BLACK,
        (x - eye_dx + pupil_x, eye_y + pupil_y),
        pupil_r,
    )
    pygame.draw.circle(
        screen,
        BLACK,
        (x + eye_dx + pupil_x, eye_y + pupil_y),
        pupil_r,
    )

    pygame.draw.arc(
        screen,
        BLACK,
        (x - int(10 * scale), y + int(1 * scale), int(20 * scale), int(12 * scale)),
        0,
        math.pi,
        max(1, int(2 * scale)),
    )

    if aiming:
        muzzle = pygame.Vector2(x, y) + aim * (34 * scale)
        draw_glow_circle(
            screen,
            ORANGE,
            (int(muzzle.x), int(muzzle.y)),
            max(3, int(5 * scale)),
        )


def draw_human(pos, scale=1.0, aiming=True):
    x, y = int(pos[0]), int(pos[1])
    aim = aim_direction() if aiming else pygame.Vector2(1, 0)

    body = theme()["accent"]
    trim = theme()["accent_2"]
    skin = (255, 210, 170)
    hair = (45, 30, 35)

    draw_glow_circle(screen, body, (x, y), int(26 * scale))

    pygame.draw.line(
        screen,
        trim,
        (x - int(7 * scale), y + int(14 * scale)),
        (x - int(11 * scale), y + int(30 * scale)),
        max(3, int(6 * scale)),
    )
    pygame.draw.line(
        screen,
        trim,
        (x + int(7 * scale), y + int(14 * scale)),
        (x + int(11 * scale), y + int(30 * scale)),
        max(3, int(6 * scale)),
    )

    torso = pygame.Rect(0, 0, int(28 * scale), int(32 * scale))
    torso.center = (x, y + int(8 * scale))
    pygame.draw.rect(screen, body, torso, border_radius=max(4, int(8 * scale)))
    pygame.draw.rect(
        screen,
        trim,
        torso,
        max(1, int(2 * scale)),
        border_radius=max(4, int(8 * scale)),
    )

    head_y = y - int(16 * scale)
    pygame.draw.circle(screen, skin, (x, head_y), max(6, int(12 * scale)))
    pygame.draw.arc(
        screen,
        hair,
        (x - int(13 * scale), head_y - int(13 * scale), int(26 * scale), int(22 * scale)),
        math.pi,
        math.pi * 2,
        max(2, int(7 * scale)),
    )
    pygame.draw.circle(screen, BLACK, (x - int(4 * scale), head_y), max(1, int(2 * scale)))
    pygame.draw.circle(screen, BLACK, (x + int(4 * scale), head_y), max(1, int(2 * scale)))

    hand = pygame.Vector2(x, y + int(2 * scale)) + aim * (24 * scale)
    pygame.draw.line(
        screen,
        skin,
        (x, y),
        (int(hand.x), int(hand.y)),
        max(3, int(5 * scale)),
    )
    pygame.draw.circle(
        screen,
        trim,
        (int(hand.x), int(hand.y)),
        max(3, int(5 * scale)),
    )

    if aiming:
        muzzle = hand + aim * (13 * scale)
        draw_glow_circle(
            screen,
            ORANGE,
            (int(muzzle.x), int(muzzle.y)),
            max(3, int(5 * scale)),
        )


def draw_player():
    if character_choice == "MONSTER":
        draw_monster(player)
    else:
        draw_human(player)


# ============================================================
# MENU / SETTINGS / RULE BOOK
# ============================================================


def draw_menu():
    global menu_buttons
    menu_buttons = {}

    shadow = TITLE_FONT.render("AGMAN", True, theme()["accent_2"])
    title = TITLE_FONT.render("AGMAN", True, theme()["accent"])

    screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 5, 92)))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 87)))

    sub = SMALL_FONT.render(
        "CHOOSE YOUR HERO • MASTER THE FLAME • SURVIVE",
        True,
        text_colour(),
    )
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 150)))

    preview_pos = (WIDTH // 2, 240)
    if character_choice == "MONSTER":
        draw_monster(preview_pos, 1.55, aiming=False)
    else:
        draw_human(preview_pos, 1.55, aiming=False)

    play = pygame.Rect(WIDTH // 2 - 175, 325, 350, 64)
    settings_btn = pygame.Rect(WIDTH // 2 - 175, 406, 350, 56)
    rules = pygame.Rect(WIDTH // 2 - 175, 478, 350, 56)
    exit_btn = pygame.Rect(WIDTH // 2 - 175, 550, 350, 52)

    menu_buttons = {
        "PLAY": play,
        "SETTINGS": settings_btn,
        "RULES": rules,
        "EXIT": exit_btn,
    }

    draw_button(play, "PLAY", font=BUTTON_FONT)
    draw_button(settings_btn, "PLAYER LAB / SETTINGS")
    draw_button(rules, "HOW TO PLAY")
    draw_button(exit_btn, "EXIT GAME")

    speed_pct = int(DIFFICULTIES[selected_difficulty]["enemy_speed"] * 100)
    summary = TINY_FONT.render(
        f"{character_choice} • {display_mode} • {selected_difficulty} ({speed_pct}% enemy speed) • HIGH SCORE {high_score}",
        True,
        muted_colour(),
    )
    screen.blit(summary, summary.get_rect(center=(WIDTH // 2, 640)))


def draw_settings():
    global settings_rects
    settings_rects = {}

    heading = HEADING_FONT.render("PLAYER LAB", True, theme()["accent"])
    screen.blit(heading, heading.get_rect(center=(WIDTH // 2, 42)))

    # Character
    screen.blit(SMALL_FONT.render("1. HERO", True, text_colour()), (80, 86))
    monster_rect = pygame.Rect(80, 116, 205, 58)
    human_rect = pygame.Rect(300, 116, 205, 58)
    settings_rects["MONSTER"] = monster_rect
    settings_rects["HUMAN"] = human_rect
    draw_button(monster_rect, "MONSTER", character_choice == "MONSTER")
    draw_button(human_rect, "HUMAN", character_choice == "HUMAN")

    # Theme
    screen.blit(SMALL_FONT.render("2. NEON WORLD", True, text_colour()), (80, 205))
    for i, name in enumerate(THEME_NAMES):
        rect = pygame.Rect(80 + i * 215, 235, 195, 54)
        settings_rects[f"THEME_{i}"] = rect
        draw_button(
            rect,
            name,
            i == selected_theme_index,
            accent=THEMES[name]["accent"],
            font=TINY_FONT,
        )

    # Screen
    screen.blit(SMALL_FONT.render("3. SCREEN", True, text_colour()), (80, 325))
    dark_rect = pygame.Rect(80, 355, 150, 52)
    light_rect = pygame.Rect(245, 355, 150, 52)
    settings_rects["DARK"] = dark_rect
    settings_rects["LIGHT"] = light_rect
    draw_button(dark_rect, "DARK", display_mode == "DARK")
    draw_button(light_rect, "LIGHT", display_mode == "LIGHT")

    brightness_rect = pygame.Rect(455, 371, 390, 14)
    settings_rects["BRIGHTNESS"] = brightness_rect
    draw_slider(brightness_rect, brightness, "BRIGHTNESS")

    # Difficulty
    screen.blit(SMALL_FONT.render("4. DIFFICULTY / ENEMY SPEED", True, text_colour()), (80, 448))
    for i, name in enumerate(("EASY", "MEDIUM", "HARD")):
        rect = pygame.Rect(80 + i * 185, 480, 165, 54)
        settings_rects[f"DIFF_{name}"] = rect
        draw_button(rect, name, selected_difficulty == name)

    speed_copy = {
        "EASY": "EASY: enemies move slowly — 70% speed",
        "MEDIUM": "MEDIUM: normal enemy speed — 100%",
        "HARD": "HARD: enemies move fast — 140%",
    }[selected_difficulty]
    screen.blit(TINY_FONT.render(speed_copy, True, muted_colour()), (80, 546))

    # Sound
    volume_rect = pygame.Rect(675, 495, 400, 14)
    settings_rects["VOLUME"] = volume_rect
    draw_slider(volume_rect, master_volume * 100, "SOUND")

    music_rect = pygame.Rect(675, 535, 190, 48)
    settings_rects["MUSIC"] = music_rect
    draw_button(
        music_rect,
        "MUSIC: ON" if music_enabled else "MUSIC: OFF",
        music_enabled,
    )

    back = pygame.Rect(WIDTH // 2 - 125, 628, 250, 52)
    settings_rects["BACK"] = back
    draw_button(back, "SAVE & BACK", active=True)


def draw_rules():
    global rule_back_rect

    heading = HEADING_FONT.render("AGMAN RULE BOOK", True, theme()["accent"])
    screen.blit(heading, heading.get_rect(center=(WIDTH // 2, 50)))

    columns = [
        (
            90,
            [
                ("MISSION", True),
                ("Survive as long as possible.", False),
                ("Defeat enemies with your fire attack.", False),
                ("Collect XP gems and evolve.", False),
                ("Bosses arrive every 5 waves.", False),
                ("", False),
                ("CONTROLS", True),
                ("WASD / Arrow Keys  —  Move", False),
                ("Mouse  —  Aim", False),
                ("Hold Left Click  —  Fire", False),
                ("P  —  Pause / Resume", False),
                ("ESC  —  Pause during gameplay", False),
            ],
        ),
        (
            650,
            [
                ("DIFFICULTY", True),
                ("Easy    —  enemies at 70% speed", False),
                ("Medium  —  enemies at 100% speed", False),
                ("Hard    —  enemies at 140% speed", False),
                ("", False),
                ("LEVEL UP", True),
                ("Collect glowing XP crystals.", False),
                ("Pick 1 of 3 upgrades each level.", False),
                ("Fire Power = stronger flames.", False),
                ("Rapid Fire = faster attacks.", False),
                ("Triple Flame = wider attack.", False),
                ("Big Heart = more maximum health.", False),
            ],
        ),
    ]

    for x, lines in columns:
        y = 110
        for text, is_heading in lines:
            if not text:
                y += 12
                continue
            font = SMALL_FONT if is_heading else TINY_FONT
            colour = theme()["accent_2"] if is_heading else text_colour()
            screen.blit(font.render(text, True, colour), (x, y))
            y += 35 if is_heading else 29

    tip_box = pygame.Rect(120, 525, 1040, 72)
    pygame.draw.rect(screen, panel_colour(), tip_box, border_radius=16)
    pygame.draw.rect(screen, theme()["accent"], tip_box, 2, border_radius=16)
    tip = SMALL_FONT.render(
        "TIP: Stay moving. XP gems become magnetic when you move near them.",
        True,
        text_colour(),
    )
    screen.blit(tip, tip.get_rect(center=tip_box.center))

    rule_back_rect = pygame.Rect(WIDTH // 2 - 110, 625, 220, 50)
    draw_button(rule_back_rect, "BACK")


# ============================================================
# ATTACK + PARTICLES
# ============================================================


def shoot():
    global last_shot

    now = pygame.time.get_ticks()
    if now - last_shot < shoot_delay:
        return

    direction = aim_direction()

    if multishot == 1:
        angles = [0]
    elif multishot == 2:
        angles = [-6, 6]
    else:
        angles = [-10, 0, 10]

    for angle in angles:
        shot_dir = direction.rotate(angle)
        start = player + shot_dir * 35

        fireballs.append(
            {
                "position": start.copy(),
                "velocity": shot_dir * fireball_speed,
                "life": 1.25,
                "damage": fireball_damage,
            }
        )

        for _ in range(3):
            fire_particles.append(
                {
                    "position": start.copy(),
                    "velocity": shot_dir.rotate(random.uniform(-35, 35)) * random.uniform(35, 95),
                    "life": random.uniform(0.15, 0.35),
                    "size": random.randint(2, 5),
                }
            )

    if shoot_sound:
        shoot_sound.play()

    last_shot = now


def update_fireballs(dt):
    for fireball in fireballs[:]:
        fireball["position"] += fireball["velocity"] * dt
        fireball["life"] -= dt
        x, y = fireball["position"]

        if (
            x < -60
            or x > WIDTH + 60
            or y < -60
            or y > HEIGHT + 60
            or fireball["life"] <= 0
        ):
            fireballs.remove(fireball)


def update_particles(dt):
    for p in fire_particles[:]:
        p["position"] += p["velocity"] * dt
        p["velocity"] *= 0.94
        p["life"] -= dt
        if p["life"] <= 0:
            fire_particles.remove(p)


def draw_fire():
    for p in fire_particles:
        colour = YELLOW if p["life"] > 0.16 else ORANGE
        pygame.draw.circle(
            screen,
            colour,
            (int(p["position"].x), int(p["position"].y)),
            max(1, p["size"]),
        )

    for fireball in fireballs:
        x, y = int(fireball["position"].x), int(fireball["position"].y)
        vel = fireball["velocity"]
        tail = pygame.Vector2(x, y) - vel.normalize() * 17
        pygame.draw.line(screen, ORANGE, (x, y), (int(tail.x), int(tail.y)), 5)
        draw_glow_circle(screen, ORANGE, (x, y), fireball_radius + 2)
        pygame.draw.circle(screen, YELLOW, (x, y), fireball_radius)
        pygame.draw.circle(screen, WHITE, (x, y), 3)


# ============================================================
# ENEMIES
# ============================================================


def spawn_position():
    side = random.choice(("TOP", "BOTTOM", "LEFT", "RIGHT"))
    if side == "TOP":
        return pygame.Vector2(random.randint(0, WIDTH), -70)
    if side == "BOTTOM":
        return pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 70)
    if side == "LEFT":
        return pygame.Vector2(-70, random.randint(0, HEIGHT))
    return pygame.Vector2(WIDTH + 70, random.randint(0, HEIGHT))


def create_enemy(kind=None):
    if kind is None:
        roll = random.random()
        if wave < 3:
            kind = "BLOB" if roll < 0.78 else "BAT"
        elif wave < 5:
            kind = "BLOB" if roll < 0.52 else "BAT" if roll < 0.82 else "TANK"
        else:
            kind = "BLOB" if roll < 0.40 else "BAT" if roll < 0.72 else "TANK"

    data = ENEMY_TYPES[kind]
    pos = spawn_position()

    wave_hp = 1.0 if kind == "BOSS" else 1 + (wave - 1) * 0.10
    hp = max(1, int(data["health"] * wave_hp))

    speed_scale = DIFFICULTIES[selected_difficulty]["enemy_speed"]

    enemies.append(
        {
            "type": kind,
            "position": pos,
            "radius": data["radius"],
            "speed": (data["speed"] + (wave - 1) * 2) * speed_scale,
            "health": hp,
            "max_health": hp,
            "damage": data["damage"],
            "score": data["score"],
            "xp": data["xp"],
            "body": data["body"],
            "belly": data["belly"],
        }
    )


def draw_enemy(enemy):
    x = int(enemy["position"].x)
    y = int(enemy["position"].y)
    r = enemy["radius"]

    draw_glow_circle(screen, enemy["body"], (x, y), r)
    pygame.draw.circle(screen, enemy["body"], (x, y), r)
    pygame.draw.circle(screen, enemy["belly"], (x, y + r // 4), max(8, r // 2))

    if enemy["type"] == "BOSS":
        pygame.draw.polygon(
            screen,
            enemy["body"],
            [(x - 30, y - 28), (x - 45, y - 60), (x - 10, y - 40)],
        )
        pygame.draw.polygon(
            screen,
            enemy["body"],
            [(x + 30, y - 28), (x + 45, y - 60), (x + 10, y - 40)],
        )

    eye_spacing = max(6, r // 3)
    eye_radius = 6 if enemy["type"] == "BOSS" else 4

    pygame.draw.circle(screen, WHITE, (x - eye_spacing, y - 5), eye_radius)
    pygame.draw.circle(screen, WHITE, (x + eye_spacing, y - 5), eye_radius)
    pygame.draw.circle(screen, BLACK, (x - eye_spacing, y - 5), max(2, eye_radius // 2))
    pygame.draw.circle(screen, BLACK, (x + eye_spacing, y - 5), max(2, eye_radius // 2))

    if enemy["type"] in ("TANK", "BOSS"):
        bar_w = r * 2
        pct = max(0, enemy["health"]) / enemy["max_health"]
        pygame.draw.rect(screen, BLACK, (x - r, y - r - 14, bar_w, 6))
        pygame.draw.rect(screen, RED, (x - r, y - r - 14, int(bar_w * pct), 6))


def update_enemies(dt):
    global health, score

    for enemy in enemies[:]:
        direction = player - enemy["position"]

        if direction.length() > 0:
            direction = direction.normalize()
            enemy["position"] += direction * enemy["speed"] * dt

        if enemy["position"].distance_to(player) < enemy["radius"] + player_radius:
            health -= enemy["damage"]

            if hit_sound:
                hit_sound.play()

            if enemy["type"] == "BOSS":
                enemy["position"] -= direction * 105
            elif enemy in enemies:
                enemies.remove(enemy)
            continue

        for fireball in fireballs[:]:
            if (
                enemy["position"].distance_to(fireball["position"])
                < enemy["radius"] + fireball_radius
            ):
                enemy["health"] -= fireball["damage"]

                if fireball in fireballs:
                    fireballs.remove(fireball)

                if enemy["health"] <= 0:
                    if enemy in enemies:
                        enemies.remove(enemy)

                    score += enemy["score"]
                    drop_xp(enemy["position"], enemy["xp"])

                    for _ in range(10):
                        fire_particles.append(
                            {
                                "position": enemy["position"].copy(),
                                "velocity": pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
                                * random.uniform(55, 170),
                                "life": random.uniform(0.20, 0.55),
                                "size": random.randint(2, 6),
                            }
                        )
                break


def draw_enemies():
    for enemy in enemies:
        draw_enemy(enemy)


# ============================================================
# XP + UPGRADES
# ============================================================


def drop_xp(position, amount):
    pieces = 5 if amount >= 60 else 2 if amount >= 20 else 1
    value = max(1, amount // pieces)

    for _ in range(pieces):
        offset = pygame.Vector2(
            random.randint(-16, 16),
            random.randint(-16, 16),
        )
        xp_gems.append(
            {
                "position": position.copy() + offset,
                "value": value,
            }
        )


def update_xp_gems(dt):
    global xp, level, xp_needed, game_state, upgrade_options

    for gem in xp_gems[:]:
        distance = gem["position"].distance_to(player)

        if 0 < distance < 150:
            gem["position"] += (player - gem["position"]).normalize() * 330 * dt

        if distance < player_radius + 12:
            xp += gem["value"]
            xp_gems.remove(gem)

    if xp >= xp_needed and game_state == "GAME":
        xp -= xp_needed
        level += 1
        xp_needed = int(xp_needed * 1.32)
        upgrade_options = random.sample(UPGRADES, 3)

        if level_sound:
            level_sound.play()

        game_state = "LEVELUP"


def draw_xp_gems():
    for gem in xp_gems:
        x = int(gem["position"].x)
        y = int(gem["position"].y)
        points = [(x, y - 8), (x + 7, y), (x, y + 8), (x - 7, y)]
        pygame.draw.polygon(screen, XP_COLOUR, points)
        pygame.draw.polygon(screen, WHITE, points, 1)


def draw_level_up():
    global upgrade_card_rects

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    heading = TITLE_FONT.render(f"LEVEL {level}!", True, theme()["accent"])
    screen.blit(heading, heading.get_rect(center=(WIDTH // 2, 125)))

    sub = SMALL_FONT.render("Choose one power", True, WHITE)
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 195)))

    upgrade_card_rects = []
    start_x = WIDTH // 2 - 480

    for i, (name, desc) in enumerate(upgrade_options):
        card = pygame.Rect(start_x + i * 330, 270, 300, 220)
        upgrade_card_rects.append(card)

        fill = theme()["accent_2"] if card.collidepoint(pygame.mouse.get_pos()) else theme()["panel"]
        pygame.draw.rect(screen, fill, card, border_radius=20)
        pygame.draw.rect(screen, theme()["accent"], card, 3, border_radius=20)

        num = BUTTON_FONT.render(str(i + 1), True, theme()["accent"])
        screen.blit(num, num.get_rect(center=(card.centerx, card.y + 42)))

        nm = SMALL_FONT.render(name, True, WHITE)
        screen.blit(nm, nm.get_rect(center=(card.centerx, card.y + 100)))

        ds = TINY_FONT.render(desc, True, WHITE)
        screen.blit(ds, ds.get_rect(center=(card.centerx, card.y + 145)))

    helper = TINY_FONT.render("Press 1 / 2 / 3 or click a card", True, WHITE)
    screen.blit(helper, helper.get_rect(center=(WIDTH // 2, 550)))


def apply_upgrade(index):
    global shoot_delay, fireball_damage, player_speed
    global max_health, health, multishot, fireball_radius, game_state

    if not (0 <= index < len(upgrade_options)):
        return

    name = upgrade_options[index][0]

    if name == "RAPID FIRE":
        shoot_delay = max(65, int(shoot_delay * 0.82))
    elif name == "FIRE POWER":
        fireball_damage += 1
    elif name == "SWIFT FEET":
        player_speed += 45
    elif name == "BIG HEART":
        max_health += 25
        health = min(max_health, health + 35)
    elif name == "TRIPLE FLAME":
        multishot = min(3, multishot + 1)
    elif name == "GIANT FLAME":
        fireball_radius = min(16, fireball_radius + 2)

    game_state = "GAME"


# ============================================================
# HUD / PAUSE / GAME OVER
# ============================================================


def draw_health_bar():
    bar_w, bar_h = 290, 22
    x, y = 25, 25

    pygame.draw.rect(screen, panel_colour(), (x, y, bar_w, bar_h), border_radius=10)

    hp_w = int(bar_w * max(0, health) / max_health)
    pygame.draw.rect(screen, RED, (x, y, hp_w, bar_h), border_radius=10)
    pygame.draw.rect(screen, text_colour(), (x, y, bar_w, bar_h), 2, border_radius=10)

    txt = TINY_FONT.render(f"HP {max(0, health)} / {max_health}", True, text_colour())
    screen.blit(txt, (x, y + 30))


def draw_xp_bar():
    bar_w, bar_h = 420, 16
    x = WIDTH // 2 - bar_w // 2
    y = 20

    pygame.draw.rect(screen, panel_colour(), (x, y, bar_w, bar_h), border_radius=8)
    pct = min(1, xp / xp_needed)
    pygame.draw.rect(
        screen,
        theme()["accent"],
        (x, y, int(bar_w * pct), bar_h),
        border_radius=8,
    )
    pygame.draw.rect(screen, text_colour(), (x, y, bar_w, bar_h), 2, border_radius=8)

    txt = TINY_FONT.render(f"LEVEL {level} • XP {xp}/{xp_needed}", True, text_colour())
    screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y + 30)))


def draw_boss_bar():
    bosses = [enemy for enemy in enemies if enemy["type"] == "BOSS"]
    if not bosses:
        return

    boss = bosses[0]
    bar_w, bar_h = 500, 20
    x = WIDTH // 2 - bar_w // 2
    y = 76

    pygame.draw.rect(screen, panel_colour(), (x, y, bar_w, bar_h), border_radius=8)
    pct = max(0, boss["health"]) / boss["max_health"]
    pygame.draw.rect(screen, ORANGE, (x, y, int(bar_w * pct), bar_h), border_radius=8)
    pygame.draw.rect(screen, text_colour(), (x, y, bar_w, bar_h), 2, border_radius=8)

    txt = TINY_FONT.render("BOSS", True, text_colour())
    screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y - 13)))


def draw_hud():
    draw_health_bar()
    draw_xp_bar()
    draw_boss_bar()

    score_text = HUD_FONT.render(f"SCORE: {score}", True, theme()["accent"])
    screen.blit(score_text, (WIDTH - score_text.get_width() - 25, 20))

    wave_text = SMALL_FONT.render(
        f"WAVE {wave} • {selected_difficulty}",
        True,
        text_colour(),
    )
    screen.blit(wave_text, (WIDTH - wave_text.get_width() - 25, 56))

    info = TINY_FONT.render(
        "WASD MOVE • HOLD LEFT CLICK FIRE • P PAUSE",
        True,
        text_colour(),
    )
    screen.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT - 24)))


def draw_announcement():
    if announcement_timer <= 0:
        return

    overlay = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 115))
    screen.blit(overlay, (0, HEIGHT // 2 - 50))

    txt = HEADING_FONT.render(announcement_text, True, theme()["accent"])
    screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


def draw_pause():
    global pause_rects

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    heading = TITLE_FONT.render("PAUSED", True, theme()["accent"])
    screen.blit(heading, heading.get_rect(center=(WIDTH // 2, 180)))

    resume = pygame.Rect(WIDTH // 2 - 150, 300, 300, 58)
    settings_btn = pygame.Rect(WIDTH // 2 - 150, 378, 300, 58)
    menu = pygame.Rect(WIDTH // 2 - 150, 456, 300, 58)

    pause_rects = {
        "RESUME": resume,
        "SETTINGS": settings_btn,
        "MENU": menu,
    }

    draw_button(resume, "RESUME", active=True)
    draw_button(settings_btn, "SETTINGS")
    draw_button(menu, "MAIN MENU")


def update_high_score():
    global high_score
    if score > high_score:
        high_score = score
        save_settings()


def draw_game_over():
    global gameover_rects

    update_high_score()
    gameover_rects = {}

    over = TITLE_FONT.render("GAME OVER", True, RED)
    screen.blit(over, over.get_rect(center=(WIDTH // 2, 165)))

    score_text = BUTTON_FONT.render(f"SCORE: {score}", True, text_colour())
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 270)))

    best_text = SMALL_FONT.render(f"HIGH SCORE: {high_score}", True, theme()["accent"])
    screen.blit(best_text, best_text.get_rect(center=(WIDTH // 2, 320)))

    detail = TINY_FONT.render(
        f"LEVEL {level} • WAVE {wave} • {selected_difficulty}",
        True,
        muted_colour(),
    )
    screen.blit(detail, detail.get_rect(center=(WIDTH // 2, 360)))

    restart = pygame.Rect(WIDTH // 2 - 150, 410, 300, 56)
    menu = pygame.Rect(WIDTH // 2 - 150, 482, 300, 56)
    exit_btn = pygame.Rect(WIDTH // 2 - 150, 554, 300, 52)

    gameover_rects = {
        "RESTART": restart,
        "MENU": menu,
        "EXIT": exit_btn,
    }

    draw_button(restart, "PLAY AGAIN", active=True)
    draw_button(menu, "MAIN MENU")
    draw_button(exit_btn, "EXIT GAME")


# ============================================================
# GAME RESET
# ============================================================


def reset_game():
    global player, player_speed, health, max_health
    global fireballs, fire_particles, fireball_damage, fireball_radius
    global shoot_delay, last_shot, multishot
    global enemies, xp_gems, score, level, xp, xp_needed
    global wave, wave_timer, boss_waves_spawned, last_enemy_spawn
    global announcement_text, announcement_timer

    player = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    player_speed = 330
    max_health = 100
    health = 100

    fireballs = []
    fire_particles = []
    fireball_damage = 1
    fireball_radius = 7
    shoot_delay = 150
    last_shot = 0
    multishot = 1

    enemies = []
    xp_gems = []

    score = 0
    level = 1
    xp = 0
    xp_needed = 50

    wave = 1
    wave_timer = 0
    boss_waves_spawned = set()
    last_enemy_spawn = pygame.time.get_ticks()

    announcement_text = "WAVE 1"
    announcement_timer = 1.7


# ============================================================
# MAIN LOOP
# ============================================================

running = True
settings_return_state = "MENU"

while running:
    dt = clock.tick(FPS) / 1000
    now = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            save_settings()
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "GAME" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                game_state = "PAUSE"

            elif game_state == "PAUSE" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                game_state = "GAME"

            elif event.key == pygame.K_ESCAPE:
                if game_state in ("SETTINGS", "RULES", "GAMEOVER"):
                    game_state = settings_return_state if game_state == "SETTINGS" else "MENU"

            if game_state == "MENU" and event.key == pygame.K_RETURN:
                reset_game()
                game_state = "GAME"

            elif game_state == "GAMEOVER" and event.key == pygame.K_RETURN:
                reset_game()
                game_state = "GAME"

            elif game_state == "LEVELUP":
                if event.key == pygame.K_1:
                    apply_upgrade(0)
                elif event.key == pygame.K_2:
                    apply_upgrade(1)
                elif event.key == pygame.K_3:
                    apply_upgrade(2)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # ---------------- MENU ----------------
            if game_state == "MENU":
                if menu_buttons.get("PLAY", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    reset_game()
                    game_state = "GAME"

                elif menu_buttons.get("SETTINGS", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    settings_return_state = "MENU"
                    game_state = "SETTINGS"

                elif menu_buttons.get("RULES", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    game_state = "RULES"

                elif menu_buttons.get("EXIT", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    save_settings()
                    running = False

            # --------------- SETTINGS -------------
            elif game_state == "SETTINGS":
                if settings_rects.get("MONSTER", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    character_choice = "MONSTER"

                elif settings_rects.get("HUMAN", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    character_choice = "HUMAN"

                for i in range(len(THEME_NAMES)):
                    if settings_rects.get(f"THEME_{i}", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        selected_theme_index = i

                if settings_rects.get("DARK", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    display_mode = "DARK"

                elif settings_rects.get("LIGHT", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    display_mode = "LIGHT"

                for name in ("EASY", "MEDIUM", "HARD"):
                    if settings_rects.get(f"DIFF_{name}", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        selected_difficulty = name

                if settings_rects.get("MUSIC", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    music_enabled = not music_enabled
                    if ambient_sound:
                        if music_enabled:
                            ambient_sound.play(loops=-1)
                        else:
                            ambient_sound.stop()

                if settings_rects.get("BACK", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    save_settings()
                    game_state = settings_return_state

            # ---------------- RULES ----------------
            elif game_state == "RULES":
                if rule_back_rect.collidepoint(event.pos):
                    game_state = "MENU"

            # ---------------- PAUSE ----------------
            elif game_state == "PAUSE":
                if pause_rects.get("RESUME", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    game_state = "GAME"

                elif pause_rects.get("SETTINGS", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    settings_return_state = "PAUSE"
                    game_state = "SETTINGS"

                elif pause_rects.get("MENU", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    update_high_score()
                    game_state = "MENU"

            # --------------- LEVEL UP --------------
            elif game_state == "LEVELUP":
                for i, card in enumerate(upgrade_card_rects):
                    if card.collidepoint(event.pos):
                        apply_upgrade(i)
                        break

            # --------------- GAME OVER -------------
            elif game_state == "GAMEOVER":
                if gameover_rects.get("RESTART", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    reset_game()
                    game_state = "GAME"

                elif gameover_rects.get("MENU", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    game_state = "MENU"

                elif gameover_rects.get("EXIT", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    save_settings()
                    running = False

    # ------------------------- SLIDERS -----------------------

    if game_state == "SETTINGS" and pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()

        brect = settings_rects.get("BRIGHTNESS")
        if (
            brect
            and brect.y - 18 <= my <= brect.bottom + 18
            and brect.x - 12 <= mx <= brect.right + 12
        ):
            pct = clamp((mx - brect.x) / brect.width, 0, 1)
            brightness = int(20 + pct * 80)

        vrect = settings_rects.get("VOLUME")
        if (
            vrect
            and vrect.y - 18 <= my <= vrect.bottom + 18
            and vrect.x - 12 <= mx <= vrect.right + 12
        ):
            pct = clamp((mx - vrect.x) / vrect.width, 0, 1)
            master_volume = pct
            update_audio()

    # ------------------------- GAME --------------------------

    if game_state == "GAME":
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            movement.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            movement.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1

        if movement.length() > 0:
            player += movement.normalize() * player_speed * dt

        player.x = clamp(player.x, player_radius, WIDTH - player_radius)
        player.y = clamp(player.y, player_radius, HEIGHT - player_radius)

        if pygame.mouse.get_pressed()[0]:
            shoot()

        wave_timer += dt

        if wave_timer >= 20:
            wave_timer = 0
            wave += 1
            announce(f"WAVE {wave}")

            if wave % 10 == 0:
                announce(f"MILESTONE! WAVE {wave}", 2.4)

        if wave % 5 == 0 and wave not in boss_waves_spawned:
            announce("BOSS INCOMING!", 2.3)

            if boss_sound:
                boss_sound.play()

            create_enemy("BOSS")
            boss_waves_spawned.add(wave)

        # Number of enemies rises with waves, but difficulty is
        # primarily controlled by enemy movement speed.
        spawn_delay = max(
            260,
            base_enemy_spawn_delay
            - (wave - 1) * 50
            - min(score, 3000) // 25,
        )

        if now - last_enemy_spawn >= spawn_delay:
            create_enemy()
            last_enemy_spawn = now

        update_fireballs(dt)
        update_particles(dt)
        update_enemies(dt)
        update_xp_gems(dt)

        if announcement_timer > 0:
            announcement_timer -= dt

        if health <= 0:
            update_high_score()
            game_state = "GAMEOVER"

    # -------------------------- DRAW -------------------------

    draw_background(dt)

    if game_state == "MENU":
        draw_menu()

    elif game_state == "SETTINGS":
        draw_settings()

    elif game_state == "RULES":
        draw_rules()

    elif game_state in ("GAME", "LEVELUP", "PAUSE"):
        draw_grid()
        draw_xp_gems()
        draw_fire()
        draw_enemies()
        draw_player()
        draw_hud()
        draw_announcement()

        if game_state == "LEVELUP":
            draw_level_up()

        elif game_state == "PAUSE":
            draw_pause()

    elif game_state == "GAMEOVER":
        draw_game_over()

    pygame.display.flip()

save_settings()
pygame.quit()
