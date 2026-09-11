import pygame
import random
import math
import json
import array
from pathlib import Path

from game.camera import Camera
from game.runner_world import RunnerWorld, WORLD_WIDTH, WORLD_HEIGHT
from game.inventory import Inventory
from game.loot import LootSystem
from game.missions import MissionSystem
from game.weapons import WeaponSystem
from game.zone import CollapsingZone
from game.camps import CampSystem
from game.levels import CampaignLevels
from game.rescue import RescueSystem

# ============================================================
# AGMAN - Stage 5
# Python 3.12 + pygame-ce
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AGMAN")

# Procedural AGMAN app/window icon — no external image file needed yet.
app_icon = pygame.Surface((64, 64), pygame.SRCALPHA)
pygame.draw.circle(app_icon, (0, 240, 255), (32, 32), 27)
pygame.draw.circle(app_icon, (15, 18, 30), (32, 32), 21)
pygame.draw.polygon(app_icon, (255, 135, 40), [(32, 8), (21, 34), (31, 31), (26, 54), (45, 26), (35, 30)])
pygame.draw.circle(app_icon, (245, 245, 255), (24, 26), 4)
pygame.draw.circle(app_icon, (245, 245, 255), (40, 26), 4)
pygame.draw.circle(app_icon, (12, 12, 18), (24, 26), 2)
pygame.draw.circle(app_icon, (12, 12, 18), (40, 26), 2)
pygame.display.set_icon(app_icon)

clock = pygame.time.Clock()

# Stage 8 world: a 3 km run-and-gun race to the finish line.
city = RunnerWorld()
camera = Camera(WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, look_ahead_x=260)
inventory = Inventory()
loot = LootSystem(city)
missions = MissionSystem()
weapons = WeaponSystem(city)
zone = CollapsingZone(city)
camps = CampSystem(city)
campaign = CampaignLevels()
rescue = RescueSystem(city)

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
    "highest_campaign_level": 1,
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
    data["highest_campaign_level"] = max(1, min(10, int(data.get("highest_campaign_level", 1))))
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
        "highest_campaign_level": highest_campaign_level,
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
highest_campaign_level = settings["highest_campaign_level"]
campaign_level = 1

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

player = city.spawn.copy()
camera.snap(player)
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
boss_kills = 0
invincible_until = 0
wave = 1
wave_timer = 0.0
boss_waves_spawned = set()

announcement_text = ""
announcement_timer = 0.0

race_started_ticks = 0
race_elapsed = 0.0
distance_announced = set()
finish_bonus_awarded = False
victory_rects = {}
level_select_rects = {}
final_boss_spawned = False
final_boss_defeated = False

game_state = "SPLASH"
splash_started = pygame.time.get_ticks()
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
    global race_started_ticks, race_elapsed, distance_announced
    global finish_bonus_awarded, final_boss_spawned, final_boss_defeated
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
    # Mouse is in screen coordinates; player is in world coordinates.
    mouse_world = camera.screen_to_world(pygame.mouse.get_pos())
    direction = mouse_world - player
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
    screen_pos = camera.world_to_screen(player)
    if character_choice == "MONSTER":
        draw_monster(screen_pos)
    else:
        draw_human(screen_pos)


# ============================================================
# SPLASH / LOADING PRESENTATION
# ============================================================


def draw_splash():
    elapsed = pygame.time.get_ticks() - splash_started
    progress = clamp(elapsed / 2400, 0, 1)

    # Center emblem
    cx, cy = WIDTH // 2, 245
    pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.006) * 0.05
    rr = int(62 * pulse)

    draw_glow_circle(screen, theme()["accent"], (cx, cy), rr)
    pygame.draw.circle(screen, panel_colour(), (cx, cy), rr)
    pygame.draw.circle(screen, theme()["accent"], (cx, cy), rr, 4)

    # Flame-shaped AGMAN mark
    flame = [
        (cx, cy - 43),
        (cx - 25, cy + 5),
        (cx - 7, cy - 2),
        (cx - 16, cy + 42),
        (cx + 30, cy - 10),
        (cx + 9, cy - 1),
    ]
    pygame.draw.polygon(screen, ORANGE, flame)
    pygame.draw.circle(screen, WHITE, (cx - 20, cy - 8), 6)
    pygame.draw.circle(screen, WHITE, (cx + 20, cy - 8), 6)
    pygame.draw.circle(screen, BLACK, (cx - 20, cy - 8), 2)
    pygame.draw.circle(screen, BLACK, (cx + 20, cy - 8), 2)

    title = TITLE_FONT.render("AGMAN", True, theme()["accent"])
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 105)))

    sub = SMALL_FONT.render(
        "RESCUE • RUN • SHOOT • ESCORT EVERYONE TO EXTRACTION",
        True,
        text_colour(),
    )
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 165)))

    status = TINY_FONT.render(
        "INITIALIZING PLAYER LAB..." if progress < 1 else "READY",
        True,
        muted_colour(),
    )
    screen.blit(status, status.get_rect(center=(WIDTH // 2, 390)))

    bar_w, bar_h = 470, 16
    x, y = WIDTH // 2 - bar_w // 2, 425

    pygame.draw.rect(
        screen,
        panel_colour(),
        (x, y, bar_w, bar_h),
        border_radius=8,
    )
    pygame.draw.rect(
        screen,
        theme()["accent"],
        (x, y, int(bar_w * progress), bar_h),
        border_radius=8,
    )
    pygame.draw.rect(
        screen,
        text_colour(),
        (x, y, bar_w, bar_h),
        2,
        border_radius=8,
    )

    pct = TINY_FONT.render(f"{int(progress * 100)}%", True, text_colour())
    screen.blit(pct, pct.get_rect(center=(WIDTH // 2, 465)))


# ============================================================
# MENU / SETTINGS / RULE BOOK
# ============================================================


def draw_menu():
    global menu_buttons
    menu_buttons = {}

    menu_time = pygame.time.get_ticks() / 1000
    title_bob = int(math.sin(menu_time * 2.2) * 4)
    preview_bob = int(math.sin(menu_time * 2.8) * 7)

    shadow = TITLE_FONT.render("AGMAN", True, theme()["accent_2"])
    title = TITLE_FONT.render("AGMAN", True, theme()["accent"])

    screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 5, 92 + title_bob)))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 87 + title_bob)))

    sub = SMALL_FONT.render(
        "RUN • SHOOT • SURVIVE • REACH THE FINISH LINE",
        True,
        text_colour(),
    )
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 150 + title_bob)))

    preview_pos = (WIDTH // 2, 240 + preview_bob)
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

    draw_button(play, "PLAY / LEVELS", font=BUTTON_FONT)
    draw_button(settings_btn, "PLAYER LAB / SETTINGS")
    draw_button(rules, "HOW TO PLAY")
    draw_button(exit_btn, "EXIT GAME")

    speed_pct = int(DIFFICULTIES[selected_difficulty]["enemy_speed"] * 100)
    summary = TINY_FONT.render(
        f"{character_choice} • {selected_difficulty} • LEVELS UNLOCKED {highest_campaign_level}/10 • HIGH SCORE {high_score}",
        True,
        muted_colour(),
    )
    screen.blit(summary, summary.get_rect(center=(WIDTH // 2, 640)))

    version = TINY_FONT.render("AGMAN • Stage 9 • 10-Level Campaign", True, muted_colour())
    screen.blit(version, version.get_rect(center=(WIDTH // 2, 680)))



def draw_level_select():
    global level_select_rects
    level_select_rects = {}

    title = HEADING_FONT.render(
        "SELECT CAMPAIGN LEVEL",
        True,
        theme()["accent"],
    )
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 52)))

    subtitle = TINY_FONT.render(
        f"Clear a level to unlock the next • {highest_campaign_level}/10 unlocked",
        True,
        muted_colour(),
    )
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 88)))

    card_w = 218
    card_h = 205
    gap_x = 22
    start_x = 45
    row_y = [125, 355]

    for i in range(1, 11):
        row = 0 if i <= 5 else 1
        col = (i - 1) % 5

        rect = pygame.Rect(
            start_x + col * (card_w + gap_x),
            row_y[row],
            card_w,
            card_h,
        )

        level_select_rects[i] = rect

        unlocked = i <= highest_campaign_level
        config = campaign.get(i)

        fill = panel_colour() if unlocked else (
            (36, 38, 48) if display_mode == "DARK" else (205, 208, 216)
        )

        pygame.draw.rect(screen, fill, rect, border_radius=14)
        pygame.draw.rect(
            screen,
            theme()["accent"] if unlocked else muted_colour(),
            rect,
            2,
            border_radius=14,
        )

        number = HEADING_FONT.render(
            str(i),
            True,
            theme()["accent"] if unlocked else muted_colour(),
        )
        screen.blit(number, number.get_rect(center=(rect.centerx, rect.y + 38)))

        name = TINY_FONT.render(
            config["name"],
            True,
            text_colour() if unlocked else muted_colour(),
        )
        screen.blit(name, name.get_rect(center=(rect.centerx, rect.y + 79)))

        tag = pygame.font.Font(None, 18).render(
            config["tagline"],
            True,
            muted_colour(),
        )
        screen.blit(tag, tag.get_rect(center=(rect.centerx, rect.y + 105)))

        threat = min(10, i)
        friend_count = rescue.friend_count_for_level(i)

        rescue_text = pygame.font.Font(None, 18).render(
            f"RESCUE {friend_count} FRIEND{'S' if friend_count != 1 else ''}",
            True,
            theme()["accent_2"] if unlocked else muted_colour(),
        )
        screen.blit(
            rescue_text,
            rescue_text.get_rect(center=(rect.centerx, rect.y + 130)),
        )

        threat_text = TINY_FONT.render(
            f"THREAT {'●' * min(5, 1 + (threat - 1) // 2)}",
            True,
            (255, 105, 110) if unlocked else muted_colour(),
        )
        screen.blit(
            threat_text,
            threat_text.get_rect(center=(rect.centerx, rect.y + 153)),
        )

        status = "PLAY" if unlocked else "LOCKED"
        status_colour = theme()["accent_2"] if unlocked else muted_colour()
        status_text = SMALL_FONT.render(status, True, status_colour)
        screen.blit(
            status_text,
            status_text.get_rect(center=(rect.centerx, rect.bottom - 24)),
        )

    back = pygame.Rect(WIDTH // 2 - 120, 590, 240, 52)
    level_select_rects["BACK"] = back
    draw_button(back, "BACK")


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
                ("10 campaign levels • each is a 5 km survival run.", False),
                ("Clear each level to unlock the next.", False),
                ("MAIN MISSION: rescue every trapped friend.", False),
                ("Press E beside a cage to unlock your friend.", False),
                ("Rescued friends follow you to extraction.", False),
                ("The finish stays LOCKED until everyone is rescued.", False),
                ("Survive as long as possible.", False),
                ("Defeat enemies with your fire attack.", False),
                ("Collect XP gems and evolve.", False),
                ("Bosses arrive every 5 waves.", False),
                ("", False),
                ("CONTROLS", True),
                ("D / Right  —  run faster forward", False),
                ("A / Left  —  slow down / move back", False),
                ("W/S or Up/Down  —  change running lane", False),
                ("Mouse  —  Aim", False),
                ("Hold Left Click  —  Fire", False),
                ("P  —  Pause / Resume", False),
                ("E  —  Open crates / use Safehouse", False),
                ("Q  —  Use medkit", False),
                ("TAB  —  Survival inventory", False),
                ("1 / 2 / 3  —  switch weapons", False),
                ("Search vehicle wrecks for guns/ammo", False),
                ("Keep ahead of the collapsing zone", False),
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

    if weapons.fallback_if_empty():
        announce("OUT OF AMMO • FIRE BLASTER", 0.8)

    profile = weapons.shot_profile(
        shoot_delay,
        fireball_damage,
        fireball_radius,
        multishot,
    )

    now = pygame.time.get_ticks()

    if now - last_shot < profile["delay"]:
        return

    direction = aim_direction()

    for angle in profile["angles"]:
        shot_dir = direction.rotate(angle)
        start = player + shot_dir * 35

        fireballs.append(
            {
                "position": start.copy(),
                "velocity": shot_dir * profile["speed"],
                "life": profile["life"],
                "damage": profile["damage"],
                "radius": profile["radius"],
                "colour": profile["colour"],
                "trail": profile["trail"],
            }
        )

        for _ in range(profile["particles"]):
            fire_particles.append(
                {
                    "position": start.copy(),
                    "velocity": shot_dir.rotate(
                        random.uniform(-35, 35)
                    )
                    * random.uniform(35, 105),
                    "life": random.uniform(0.15, 0.35),
                    "size": random.randint(2, 5),
                    "colour": profile["colour"],
                }
            )

    weapons.consume_ammo()

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
            or x > WORLD_WIDTH + 60
            or y < -60
            or y > WORLD_HEIGHT + 60
            or fireball["life"] <= 0
            or city.is_blocked_point(fireball["position"], 2)
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
        sp = camera.world_to_screen(p["position"])

        if -30 < sp.x < WIDTH + 30 and -30 < sp.y < HEIGHT + 30:
            colour = p.get("colour", ORANGE)

            pygame.draw.circle(
                screen,
                colour,
                (int(sp.x), int(sp.y)),
                max(1, p["size"]),
            )

    for fireball in fireballs:
        sp = camera.world_to_screen(fireball["position"])

        if not (
            -60 < sp.x < WIDTH + 60
            and -60 < sp.y < HEIGHT + 60
        ):
            continue

        vel = fireball["velocity"]
        tail = sp - vel.normalize() * 17
        x, y = int(sp.x), int(sp.y)

        colour = fireball.get("colour", YELLOW)
        trail = fireball.get("trail", ORANGE)
        radius = fireball.get("radius", fireball_radius)

        pygame.draw.line(
            screen,
            trail,
            (x, y),
            (int(tail.x), int(tail.y)),
            5,
        )

        draw_glow_circle(
            screen,
            trail,
            (x, y),
            radius + 2,
        )

        pygame.draw.circle(
            screen,
            colour,
            (x, y),
            radius,
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (x, y),
            max(2, radius // 2),
        )


# ============================================================
# ENEMIES
# ============================================================


def spawn_position():
    return city.spawn_near(
        player,
        min_distance=720,
        max_distance=1050,
        radius=55,
    )


def create_enemy(kind=None, position=None, tag=None):
    if kind is None:
        roll = random.random()
        if wave < 3:
            kind = "BLOB" if roll < 0.78 else "BAT"
        elif wave < 5:
            kind = "BLOB" if roll < 0.52 else "BAT" if roll < 0.82 else "TANK"
        else:
            kind = "BLOB" if roll < 0.40 else "BAT" if roll < 0.72 else "TANK"

    data = ENEMY_TYPES[kind]
    pos = (
        pygame.Vector2(position)
        if position is not None
        else spawn_position()
    )

    wave_hp = 1.0 if kind == "BOSS" else 1 + (wave - 1) * 0.10
    level_config = campaign.get(campaign_level)
    hp = max(
        1,
        int(
            data["health"]
            * wave_hp
            * level_config["enemy_health"]
        ),
    )

    level_config = campaign.get(campaign_level)
    speed_scale = (
        DIFFICULTIES[selected_difficulty]["enemy_speed"]
        * level_config["enemy_speed"]
    )

    enemies.append(
        {
            "type": kind,
            "position": pos,
            "radius": data["radius"],
            "speed": (data["speed"] + (wave - 1) * 2) * speed_scale,
            "health": hp,
            "max_health": hp,
            "damage": max(1, int(data["damage"] * level_config["enemy_damage"])),
            "score": data["score"],
            "xp": data["xp"],
            "body": data["body"],
            "belly": data["belly"],
            "tag": tag,
        }
    )


def draw_enemy(enemy):
    sp = camera.world_to_screen(enemy["position"])
    x = int(sp.x)
    y = int(sp.y)
    r = enemy["radius"]

    if x < -r * 3 or x > WIDTH + r * 3 or y < -r * 3 or y > HEIGHT + r * 3:
        return

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
    global health, score, boss_kills, final_boss_defeated

    for enemy in enemies[:]:
        direction = player - enemy["position"]

        if direction.length() > 0:
            direction = direction.normalize()
            step = direction * enemy["speed"] * dt
            before = enemy["position"].copy()
            moved = city.move_actor(
                enemy["position"],
                step,
                max(10, enemy["radius"] * 0.72),
            )

            # If a building blocks direct pursuit, try steering around it.
            if moved.distance_to(before) < step.length() * 0.20:
                side = direction.rotate(55 if random.random() < 0.5 else -55)
                moved = city.move_actor(
                    enemy["position"],
                    side * enemy["speed"] * dt,
                    max(10, enemy["radius"] * 0.72),
                )

            enemy["position"] = moved

        if enemy["position"].distance_to(player) < enemy["radius"] + player_radius:
            # Armor absorbs damage before HP.
            damage_to_health = inventory.absorb_damage(enemy["damage"])

            if pygame.time.get_ticks() >= invincible_until:
                health -= damage_to_health

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
                < enemy["radius"] + fireball.get("radius", fireball_radius)
            ):
                enemy["health"] -= fireball["damage"]

                if fireball in fireballs:
                    fireballs.remove(fireball)

                if enemy["health"] <= 0:
                    if enemy in enemies:
                        enemies.remove(enemy)

                    score += enemy["score"]
                    drop_xp(enemy["position"], enemy["xp"])
                    loot.spawn_enemy_drop(enemy["position"], enemy["type"])

                    if enemy["type"] == "BOSS":
                        boss_kills += 1

                    if enemy.get("tag") == "FINAL_BOSS":
                        final_boss_defeated = True
                        announce("FINAL BOSS DEFEATED • REACH EXTRACTION!", 2.5)

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
        sp = camera.world_to_screen(gem["position"])
        x = int(sp.x)
        y = int(sp.y)

        if not (-20 < x < WIDTH + 20 and -20 < y < HEIGHT + 20):
            continue

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


def draw_race_hud():
    distance = city.distance_km(player)
    progress = city.progress_ratio(player)

    # Campaign level label.
    config = campaign.get(campaign_level)
    campaign_text = TINY_FONT.render(
        f"CAMPAIGN {campaign_level}/10 • {config['name']}",
        True,
        theme()["accent_2"],
    )
    screen.blit(
        campaign_text,
        campaign_text.get_rect(center=(WIDTH // 2, 49)),
    )

    # Central target panel.
    panel = pygame.Rect(WIDTH // 2 - 225, 72, 450, 78)
    overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    overlay.fill((5, 7, 14, 190))
    screen.blit(overlay, panel.topleft)
    pygame.draw.rect(screen, theme()["accent"], panel, 2, border_radius=12)

    distance_text = HEADING_FONT.render(
        f"FINISH  {distance:.2f} KM",
        True,
        theme()["accent"],
    )
    screen.blit(distance_text, distance_text.get_rect(center=(WIDTH // 2, 101)))

    # Race progress bar.
    bar = pygame.Rect(panel.x + 28, panel.y + 55, panel.width - 56, 10)
    pygame.draw.rect(screen, (70, 75, 90), bar, border_radius=5)
    pygame.draw.rect(
        screen,
        theme()["accent_2"],
        (bar.x, bar.y, int(bar.width * progress), bar.height),
        border_radius=5,
    )

    friend_counter = SMALL_FONT.render(
        f"FRIENDS {rescue.rescued_count}/{rescue.total}",
        True,
        theme()["accent_2"] if rescue.all_rescued else YELLOW,
    )
    screen.blit(
        friend_counter,
        (25, 340),
    )

    # Timer.
    timer_text = SMALL_FONT.render(
        f"TIME  {race_elapsed:05.1f}s",
        True,
        text_colour(),
    )
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - 25, 92))

    # Permanent target direction.
    arrow = SMALL_FONT.render(
        "FINISH  >>>",
        True,
        theme()["accent"],
    )
    screen.blit(arrow, (WIDTH - arrow.get_width() - 25, 124))


def draw_survival_hud():
    # Armor bar
    x, y = 25, 105
    bar_w, bar_h = 200, 13

    pygame.draw.rect(screen, panel_colour(), (x, y, bar_w, bar_h), border_radius=7)
    pygame.draw.rect(
        screen,
        (90, 180, 255),
        (x, y, int(bar_w * inventory.armor / inventory.max_armor), bar_h),
        border_radius=7,
    )
    pygame.draw.rect(screen, text_colour(), (x, y, bar_w, bar_h), 1, border_radius=7)

    armor_text = TINY_FONT.render(f"ARMOR {inventory.armor}", True, text_colour())
    screen.blit(armor_text, (x, y + 18))

    # Coins and lifelines
    coin_text = SMALL_FONT.render(f"COINS  {inventory.coins}", True, YELLOW)
    screen.blit(coin_text, (25, 150))

    heart_colour = (255, 80, 120)
    heart_x = 28
    heart_y = 190

    for i in range(inventory.max_lifelines):
        cx = heart_x + i * 35
        active = i < inventory.lifelines
        colour = heart_colour if active else (80, 80, 90)

        pygame.draw.circle(screen, colour, (cx - 5, heart_y - 3), 6)
        pygame.draw.circle(screen, colour, (cx + 5, heart_y - 3), 6)
        pygame.draw.polygon(
            screen,
            colour,
            [(cx - 11, heart_y), (cx + 11, heart_y), (cx, heart_y + 14)],
        )

    medkit_text = TINY_FONT.render(
        f"MEDKITS {inventory.medkits}  •  Q TO USE",
        True,
        text_colour(),
    )
    screen.blit(medkit_text, (25, 215))

    # Objective panel
    panel = pygame.Rect(25, 250, 320, 76)
    overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    overlay.fill((5, 7, 14, 185))
    screen.blit(overlay, panel.topleft)
    pygame.draw.rect(screen, theme()["accent"], panel, 2, border_radius=10)

    objective_label = TINY_FONT.render("MAIN MISSION", True, theme()["accent"])

    if not rescue.all_rescued:
        mission_name = rescue.objective_text()
    else:
        mission_name = "ESCORT FRIENDS TO FINISH"

    objective = TINY_FONT.render(
        mission_name,
        True,
        WHITE,
    )
    secondary_text = missions.progress_text(
        inventory,
        city.distance_km(player),
        city.finished(player),
    )

    progress = TINY_FONT.render(
        f"{rescue.rescued_count}/{rescue.total} rescued • {secondary_text}",
        True,
        SOFT_GREY,
    )

    screen.blit(objective_label, (panel.x + 12, panel.y + 9))
    screen.blit(objective, (panel.x + 12, panel.y + 31))
    screen.blit(progress, (panel.x + 12, panel.y + 52))

    # Interaction prompt
    prompt = rescue.prompt(player) or weapons.prompt(player) or loot.prompt(player)

    if prompt:
        prompt_surface = SMALL_FONT.render(prompt, True, WHITE)
        prompt_box = prompt_surface.get_rect(
            center=(WIDTH // 2, HEIGHT - 74)
        ).inflate(30, 20)

        fade = pygame.Surface((prompt_box.width, prompt_box.height), pygame.SRCALPHA)
        fade.fill((5, 7, 14, 210))
        screen.blit(fade, prompt_box.topleft)
        pygame.draw.rect(screen, theme()["accent"], prompt_box, 2, border_radius=12)
        screen.blit(prompt_surface, prompt_surface.get_rect(center=prompt_box.center))


def draw_inventory_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 205))
    screen.blit(overlay, (0, 0))

    title = HEADING_FONT.render("AGMAN SURVIVAL PACK", True, theme()["accent"])
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 90)))

    left = 300
    top = 170
    lines = [
        ("COINS", str(inventory.coins)),
        ("LIFELINES", f"{inventory.lifelines}/{inventory.max_lifelines}"),
        ("MEDKITS", str(inventory.medkits)),
        ("ARMOR", f"{inventory.armor}/{inventory.max_armor}"),
        ("CRATES OPENED", str(inventory.crates_opened)),
        ("FIRE DAMAGE", str(fireball_damage)),
        ("FIRE STREAMS", str(multishot)),
        ("MOVE SPEED", str(int(player_speed))),
        ("WEAPON", weapons.current),
        ("RIFLE AMMO", str(weapons.ammo["PLASMA RIFLE"])),
        ("SHOTGUN", str(weapons.ammo["FLAME SHOTGUN"])),
    ]

    for i, (label, value) in enumerate(lines):
        y = top + i * 45
        screen.blit(SMALL_FONT.render(label, True, SOFT_GREY), (left, y))
        value_surface = SMALL_FONT.render(value, True, WHITE)
        screen.blit(value_surface, (760, y))

    help_text = SMALL_FONT.render(
        "TAB CLOSE • Q MEDKIT • E LOOT • 1/2/3 WEAPONS",
        True,
        theme()["accent_2"],
    )
    screen.blit(help_text, help_text.get_rect(center=(WIDTH // 2, 590)))


def draw_weapon_and_zone_hud():
    # Weapon panel
    weapon_panel = pygame.Rect(
        WIDTH - 315,
        105,
        290,
        78,
    )

    overlay = pygame.Surface(
        (weapon_panel.width, weapon_panel.height),
        pygame.SRCALPHA,
    )
    overlay.fill((5, 7, 14, 190))
    screen.blit(overlay, weapon_panel.topleft)

    pygame.draw.rect(
        screen,
        theme()["accent"],
        weapon_panel,
        2,
        border_radius=10,
    )

    label = TINY_FONT.render(
        "WEAPON",
        True,
        theme()["accent"],
    )

    current = SMALL_FONT.render(
        weapons.current,
        True,
        WHITE,
    )

    ammo = TINY_FONT.render(
        f"AMMO {weapons.ammo_text()}  •  1/2/3 SWITCH",
        True,
        SOFT_GREY,
    )

    screen.blit(label, (weapon_panel.x + 12, weapon_panel.y + 8))
    screen.blit(current, (weapon_panel.x + 12, weapon_panel.y + 28))
    screen.blit(ammo, (weapon_panel.x + 12, weapon_panel.y + 54))

    # Zone status
    zone_colour = (
        RED
        if zone.danger_level(player) >= 2
        else theme()["accent_2"]
    )

    zone_text = TINY_FONT.render(
        zone.hud_text(player),
        True,
        zone_colour,
    )

    screen.blit(
        zone_text,
        (
            WIDTH - zone_text.get_width() - 25,
            192,
        ),
    )


def draw_hud():
    draw_health_bar()
    draw_xp_bar()
    draw_boss_bar()
    draw_race_hud()
    draw_survival_hud()
    draw_weapon_and_zone_hud()

    score_text = HUD_FONT.render(f"SCORE: {score}", True, theme()["accent"])
    screen.blit(score_text, (WIDTH - score_text.get_width() - 25, 20))

    wave_text = SMALL_FONT.render(
        f"WAVE {wave} • {selected_difficulty}",
        True,
        text_colour(),
    )
    screen.blit(wave_text, (WIDTH - wave_text.get_width() - 25, 56))

    location_text = TINY_FONT.render(
        city.district_at(player),
        True,
        theme()["accent_2"],
    )
    screen.blit(location_text, (25, 80))

    info = TINY_FONT.render(
        "RUN • SHOOT • 1/2/3 WEAPONS • E LOOT • ZONE IS CLOSING",
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
        f"CAMPAIGN {campaign_level}/10 • {city.distance_km(player):.2f} KM LEFT • XP LV {level} • COINS {inventory.coins}",
        True,
        muted_colour(),
    )
    screen.blit(detail, detail.get_rect(center=(WIDTH // 2, 360)))

    if score > 0 and score >= high_score:
        badge = pygame.Rect(WIDTH // 2 - 115, 382, 230, 34)
        pygame.draw.rect(screen, panel_colour(), badge, border_radius=12)
        pygame.draw.rect(screen, theme()["accent"], badge, 2, border_radius=12)
        badge_text = TINY_FONT.render("★ BEST AGMAN RUN ★", True, theme()["accent"])
        screen.blit(badge_text, badge_text.get_rect(center=badge.center))

    restart = pygame.Rect(WIDTH // 2 - 150, 430, 300, 56)
    menu = pygame.Rect(WIDTH // 2 - 150, 502, 300, 56)
    exit_btn = pygame.Rect(WIDTH // 2 - 150, 574, 300, 52)

    gameover_rects = {
        "RESTART": restart,
        "MENU": menu,
        "EXIT": exit_btn,
    }

    draw_button(restart, "PLAY AGAIN", active=True)
    draw_button(menu, "MAIN MENU")
    draw_button(exit_btn, "EXIT GAME")


def draw_victory():
    global victory_rects

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    config = campaign.get(campaign_level)

    title_text = "CAMPAIGN COMPLETE!" if campaign_level == 10 else f"LEVEL {campaign_level} CLEARED!"
    title = TITLE_FONT.render(title_text, True, theme()["accent"])
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

    sub = HEADING_FONT.render(config["name"], True, WHITE)
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 190)))

    stat_lines = [
        f"TIME: {race_elapsed:.1f} seconds",
        f"SCORE: {score}",
        f"COINS: {inventory.coins}",
        f"XP LEVEL: {level}",
        f"LIFELINES LEFT: {inventory.lifelines}",
        f"FRIENDS RESCUED: {rescue.rescued_count}/{rescue.total}",
    ]

    for i, line in enumerate(stat_lines):
        txt = SMALL_FONT.render(line, True, WHITE)
        screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 245 + i * 30)))

    victory_rects = {}

    if campaign_level < 10:
        next_rect = pygame.Rect(WIDTH // 2 - 170, 455, 340, 58)
        victory_rects["NEXT"] = next_rect
        draw_button(next_rect, f"NEXT: LEVEL {campaign_level + 1}", active=True)

        restart_y = 530
        menu_y = 600
    else:
        restart_y = 480
        menu_y = 555

        completed = SMALL_FONT.render(
            "ALL 10 LEVELS CLEARED",
            True,
            theme()["accent_2"],
        )
        screen.blit(completed, completed.get_rect(center=(WIDTH // 2, 430)))

    restart = pygame.Rect(WIDTH // 2 - 150, restart_y, 300, 52)
    menu = pygame.Rect(WIDTH // 2 - 150, menu_y, 300, 52)

    victory_rects["RESTART"] = restart
    victory_rects["MENU"] = menu

    draw_button(restart, "RUN THIS LEVEL AGAIN")
    draw_button(menu, "MAIN MENU")




# ============================================================
# GAME RESET
# ============================================================


def reset_game():
    global player, player_speed, health, max_health
    global fireballs, fire_particles, fireball_damage, fireball_radius
    global shoot_delay, last_shot, multishot
    global enemies, xp_gems, score, boss_kills, invincible_until, level, xp, xp_needed
    global wave, wave_timer, boss_waves_spawned, last_enemy_spawn
    global announcement_text, announcement_timer

    player = city.spawn.copy()
    camera.snap(player)
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
    boss_kills = 0
    invincible_until = 0

    config = campaign.get(campaign_level)

    city.set_campaign_level(
        campaign_level,
        config["extra_obstacles"],
    )

    rescue.reset(campaign_level)

    inventory.reset()
    inventory.armor = min(
        inventory.max_armor,
        config["start_armor"],
    )

    loot.reset()
    missions.reset()
    weapons.reset()

    zone.configure(
        config["zone_speed"],
        config["zone_grace"],
        config["zone_damage"],
    )
    zone.reset()

    camps.configure(config["camp_bonus"])
    camps.reset()

    level = 1
    xp = 0
    xp_needed = 50

    wave = 1
    wave_timer = 0
    boss_waves_spawned = set()
    last_enemy_spawn = pygame.time.get_ticks()

    race_started_ticks = pygame.time.get_ticks()
    race_elapsed = 0.0
    distance_announced = set()
    finish_bonus_awarded = False
    final_boss_spawned = False
    final_boss_defeated = False

    announcement_text = f"LEVEL {campaign_level} • {campaign.name(campaign_level)}"

    announcement_timer = 2.2


# ============================================================
# MAIN LOOP
# ============================================================

running = True
settings_return_state = "MENU"

while running:
    dt = clock.tick(FPS) / 1000
    now = pygame.time.get_ticks()

    if game_state == "SPLASH" and now - splash_started >= 2500:
        game_state = "MENU"

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            save_settings()
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "SPLASH" and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                game_state = "MENU"

            elif game_state == "GAME" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                game_state = "PAUSE"

            elif game_state == "PAUSE" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                game_state = "GAME"

            elif game_state == "GAME" and event.key == pygame.K_TAB:
                game_state = "INVENTORY"

            elif game_state == "INVENTORY" and event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                game_state = "GAME"

            elif game_state == "GAME" and event.key == pygame.K_e:
                if rescue.interact(
                    player,
                    announce,
                ):
                    pass
                elif weapons.interact(
                    player,
                    inventory,
                    announce,
                ):
                    pass
                else:
                    loot.interact(
                        player,
                        inventory,
                        announce,
                    )

            elif game_state == "GAME" and event.key in (
                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
            ):
                slot = {
                    pygame.K_1: 1,
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                }[event.key]

                if not weapons.select_slot(slot):
                    announce("WEAPON NOT FOUND YET", 0.9)

            elif game_state == "GAME" and event.key == pygame.K_q:
                new_health, used = inventory.use_medkit(health, max_health)
                if used:
                    health = new_health
                    announce("MEDKIT USED • +45 HP", 1.3)
                else:
                    announce("NO MEDKIT NEEDED", 1.0)

            elif event.key == pygame.K_ESCAPE:
                if game_state in ("SETTINGS", "RULES", "GAMEOVER", "LEVEL_SELECT"):
                    game_state = settings_return_state if game_state == "SETTINGS" else "MENU"

            if game_state == "MENU" and event.key == pygame.K_RETURN:
                game_state = "LEVEL_SELECT"

            elif game_state == "GAMEOVER" and event.key == pygame.K_RETURN:
                reset_game()
                game_state = "GAME"

            elif game_state == "VICTORY" and event.key == pygame.K_RETURN:
                if campaign_level < 10:
                    campaign_level += 1
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
                    game_state = "LEVEL_SELECT"

                elif menu_buttons.get("SETTINGS", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    settings_return_state = "MENU"
                    game_state = "SETTINGS"

                elif menu_buttons.get("RULES", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    game_state = "RULES"

                elif menu_buttons.get("EXIT", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    save_settings()
                    running = False

            # ------------ LEVEL SELECT ------------
            elif game_state == "LEVEL_SELECT":
                if level_select_rects.get("BACK", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    game_state = "MENU"
                else:
                    for selected_level in range(1, 11):
                        rect = level_select_rects.get(selected_level)
                        if (
                            rect
                            and rect.collidepoint(event.pos)
                            and selected_level <= highest_campaign_level
                        ):
                            campaign_level = selected_level
                            reset_game()
                            game_state = "GAME"
                            break

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

            # ---------------- VICTORY ---------------
            elif game_state == "VICTORY":
                if victory_rects.get("NEXT", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    if campaign_level < 10:
                        campaign_level += 1
                    reset_game()
                    game_state = "GAME"

                elif victory_rects.get("RESTART", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    reset_game()
                    game_state = "GAME"

                elif victory_rects.get("MENU", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    game_state = "MENU"

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

        # RUN-AND-GUN:
        # The runner always pushes toward the finish line.
        # Obstacles can stop the forward motion, so W/S is used to change lanes.
        forward_speed = campaign.get(campaign_level)["auto_run"]

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            forward_speed += player_speed * 0.72

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            forward_speed -= player_speed * 0.62

        lane_direction = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            lane_direction -= 1

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            lane_direction += 1

        delta = pygame.Vector2(
            forward_speed * dt,
            lane_direction * player_speed * 0.82 * dt,
        )

        player = city.move_actor(
            player,
            delta,
            player_radius,
        )

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
            180,
            int(
                (
                    base_enemy_spawn_delay
                    - (wave - 1) * 50
                    - min(score, 3000) // 25
                )
                / campaign.get(campaign_level)["spawn_rate"]
            ),
        )

        if now - last_enemy_spawn >= spawn_delay:
            create_enemy()
            last_enemy_spawn = now

        update_fireballs(dt)
        update_particles(dt)
        update_enemies(dt)
        update_xp_gems(dt)
        loot.update(player, dt, inventory, announce)
        rescue.update(player, dt)

        # Enemy camps trigger fixed ambushes instead of relying only on
        # random waves.
        camp_spawns, camp_message = camps.update(player)

        if camp_message:
            announce(camp_message, 2.0)

        for camp_kind, camp_position in camp_spawns:
            create_enemy(
                camp_kind,
                camp_position,
            )

        # Battle-royale-inspired collapsing zone from behind.
        zone_damage = zone.update(
            dt,
            player,
            city.progress_ratio(player),
        )

        if zone_damage > 0:
            health -= zone_damage

        mission_message = missions.update(
            inventory,
            city.distance_km(player),
            city.finished(player),
        )
        if mission_message:
            announce(mission_message, 2.2)

        race_elapsed = max(
            0.0,
            (pygame.time.get_ticks() - race_started_ticks) / 1000.0,
        )

        distance_now = city.distance_km(player)

        missed_rescues = rescue.missed_friends_behind(player)

        if missed_rescues and announcement_timer <= 0:
            announce(
                f"FRIEND LEFT BEHIND • GO BACK FOR {missed_rescues[0]['name']}!",
                1.3,
            )

        if distance_now <= 4.0 and 4 not in distance_announced:
            distance_announced.add(4)
            announce("4 KM TO FINISH!", 1.8)

        if distance_now <= 3.0 and 3 not in distance_announced:
            distance_announced.add(3)
            announce("3 KM TO FINISH!", 1.8)

        if distance_now <= 2.0 and 2 not in distance_announced:
            distance_announced.add(2)
            announce("2 KM TO FINISH!", 1.8)

        if distance_now <= 1.0 and 1 not in distance_announced:
            distance_announced.add(1)
            announce("1 KM TO FINISH • FINAL PUSH!", 2.0)

        # Level 10 has a final extraction boss near the finish.
        if (
            campaign.requires_final_boss(campaign_level)
            and city.distance_km(player) <= 0.40
            and not final_boss_spawned
        ):
            final_boss_spawned = True
            boss_position = pygame.Vector2(
                min(city.finish_x - 180, player.x + 520),
                800,
            )
            create_enemy(
                "BOSS",
                boss_position,
                tag="FINAL_BOSS",
            )
            announce("FINAL EXTRACTION BOSS!", 2.8)

        if city.finished(player):
            if not rescue.all_rescued:
                player.x = city.finish_x - 95

                missed = rescue.missed_friends_behind(player)

                if missed:
                    announce(
                        f"FINISH LOCKED • RESCUE {rescue.total - rescue.rescued_count} FRIEND(S)!",
                        1.8,
                    )
                else:
                    announce(
                        "FINISH LOCKED • COMPLETE THE RESCUE MISSION!",
                        1.8,
                    )

            elif (
                campaign.requires_final_boss(campaign_level)
                and not final_boss_defeated
            ):
                player.x = city.finish_x - 95
                announce("FINISH LOCKED • DEFEAT THE FINAL BOSS!", 1.6)
            else:
                if not finish_bonus_awarded:
                    finish_bonus_awarded = True
                    score += 1000 * campaign_level
                    inventory.add_coins(100)
                    update_high_score()

                    if campaign_level < 10:
                        highest_campaign_level = max(
                            highest_campaign_level,
                            campaign_level + 1,
                        )
                    else:
                        highest_campaign_level = 10

                    save_settings()

                game_state = "VICTORY"

        if announcement_timer > 0:
            announcement_timer -= dt

        if health <= 0 and game_state == "GAME":
            if inventory.consume_lifeline():
                health = max(45, max_health // 2)
                invincible_until = now + 2500

                # Give the player breathing room.
                enemies = [
                    enemy
                    for enemy in enemies
                    if enemy["position"].distance_to(player) > 260
                ]

                announce("LIFELINE USED • REVIVED!", 2.0)
            else:
                update_high_score()
                game_state = "GAMEOVER"

    if game_state in ("GAME", "LEVELUP", "PAUSE", "INVENTORY"):
        camera.update(player, dt)

    # -------------------------- DRAW -------------------------

    draw_background(dt)

    if game_state == "SPLASH":
        draw_splash()

    elif game_state == "MENU":
        draw_menu()

    elif game_state == "LEVEL_SELECT":
        draw_level_select()

    elif game_state == "SETTINGS":
        draw_settings()

    elif game_state == "RULES":
        draw_rules()

    elif game_state in ("GAME", "LEVELUP", "PAUSE", "INVENTORY"):
        city.draw(screen, camera, theme(), display_mode)
        zone.draw(screen, camera, player, theme())
        camps.draw(screen, camera, theme())
        loot.draw(screen, camera, theme(), text_colour())
        weapons.draw(screen, camera, theme())
        rescue.draw(
            screen,
            camera,
            theme(),
            character_choice,
        )
        draw_xp_gems()
        draw_fire()
        draw_enemies()
        draw_player()
        campaign.draw_effect(
            screen,
            campaign_level,
            camera.world_to_screen(player),
            pygame.time.get_ticks() / 1000.0,
        )
        draw_hud()
        city.draw_minimap(
            screen,
            player,
            [enemy["position"] for enemy in enemies],
            theme()["accent"],
            text_colour(),
        )
        draw_announcement()

        if game_state == "LEVELUP":
            draw_level_up()

        elif game_state == "PAUSE":
            draw_pause()

        elif game_state == "INVENTORY":
            draw_inventory_overlay()

    elif game_state == "GAMEOVER":
        draw_game_over()

    elif game_state == "VICTORY":
        # Freeze the final race scene behind the victory card.
        city.draw(screen, camera, theme(), display_mode)
        zone.draw(screen, camera, player, theme())
        camps.draw(screen, camera, theme())
        loot.draw(screen, camera, theme(), text_colour())
        weapons.draw(screen, camera, theme())
        rescue.draw(
            screen,
            camera,
            theme(),
            character_choice,
        )
        draw_xp_gems()
        draw_fire()
        draw_enemies()
        draw_player()
        campaign.draw_effect(
            screen,
            campaign_level,
            camera.world_to_screen(player),
            pygame.time.get_ticks() / 1000.0,
        )
        draw_hud()
        city.draw_minimap(
            screen,
            player,
            [enemy["position"] for enemy in enemies],
            theme()["accent"],
            text_colour(),
        )
        draw_victory()

    pygame.display.flip()

save_settings()
pygame.quit()
