import pygame
import random
import math
import array

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Survivor: Player Lab")
clock = pygame.time.Clock()

# =====================================================
# AUDIO
# =====================================================

audio_ok = True

try:
    pygame.mixer.quit()
    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=1
    )
except pygame.error:
    audio_ok = False


def make_tone(freq, duration, strength=0.20):

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
            * math.sin(
                2 * math.pi * freq * i / sample_rate
            )
        )

        samples.append(value)

    return pygame.mixer.Sound(
        buffer=samples.tobytes()
    )


shoot_sound = make_tone(720, 0.055, 0.12)
hit_sound = make_tone(210, 0.070, 0.12)
level_sound = make_tone(980, 0.18, 0.16)

master_volume = 0.55


def set_sound_volume():

    for sound in (
        shoot_sound,
        hit_sound,
        level_sound
    ):

        if sound:
            sound.set_volume(master_volume)


set_sound_volume()

# =====================================================
# FONTS
# =====================================================

title_font = pygame.font.Font(None, 96)
heading_font = pygame.font.Font(None, 52)
button_font = pygame.font.Font(None, 38)
hud_font = pygame.font.Font(None, 31)
small_font = pygame.font.Font(None, 26)
tiny_font = pygame.font.Font(None, 21)

# =====================================================
# COLOURS
# =====================================================

WHITE = (245, 245, 255)
BLACK = (12, 12, 18)

RED = (255, 70, 90)
YELLOW = (255, 220, 70)
ORANGE = (255, 135, 40)

XP_COLOUR = (120, 255, 220)

SOFT_GREY = (190, 195, 215)

# =====================================================
# THEMES
# =====================================================

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
    }
}

theme_names = list(THEMES.keys())

selected_theme_index = 0


def get_theme():

    return THEMES[
        theme_names[selected_theme_index]
    ]


# =====================================================
# PLAYER SETTINGS
# =====================================================

character_choice = "MONSTER"

display_mode = "DARK"

brightness = 82

selected_difficulty = "MEDIUM"


DIFFICULTIES = {

    "EASY": {

        "spawn": 1.28,

        "speed": 0.86,

        "damage": 0.75,

        "hp": 0.90,

        "score": 0.85
    },

    "MEDIUM": {

        "spawn": 1.00,

        "speed": 1.00,

        "damage": 1.00,

        "hp": 1.00,

        "score": 1.00
    },

    "HARD": {

        "spawn": 0.72,

        "speed": 1.20,

        "damage": 1.25,

        "hp": 1.20,

        "score": 1.35
    }
}

# =====================================================
# BACKGROUND STARS
# =====================================================

stars = [

    [
        random.randint(0, WIDTH),

        random.randint(0, HEIGHT),

        random.randint(1, 3),

        random.uniform(10, 40)
    ]

    for _ in range(120)
]

# =====================================================
# PLAYER
# =====================================================

player = pygame.Vector2(
    WIDTH // 2,
    HEIGHT // 2
)

player_radius = 24

player_speed = 330

max_health = 100

health = 100

# =====================================================
# FIRE
# =====================================================

fireballs = []

fireball_speed = 780

fireball_radius = 7

fireball_damage = 1

shoot_delay = 150

last_shot = 0

multishot = 1

# =====================================================
# XP
# =====================================================

xp_gems = []

xp = 0

level = 1

xp_needed = 50

upgrade_options = []

upgrade_card_rects = []


UPGRADES = [

    (
        "RAPID FIRE",
        "Shoot 18% faster"
    ),

    (
        "FIRE POWER",
        "+1 fireball damage"
    ),

    (
        "SWIFT PAWS",
        "+45 movement speed"
    ),

    (
        "BIG HEART",
        "+25 max HP and heal"
    ),

    (
        "TRIPLE FLAME",
        "Shoot extra fireballs"
    ),

    (
        "GIANT FLAME",
        "Bigger fireballs"
    )
]

# =====================================================
# ENEMIES
# =====================================================

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

        "belly": (255, 200, 225)
    },

    "BAT": {

        "radius": 16,

        "speed": 150,

        "health": 1,

        "damage": 10,

        "score": 15,

        "xp": 12,

        "body": (170, 110, 255),

        "belly": (220, 205, 255)
    },

    "TANK": {

        "radius": 28,

        "speed": 72,

        "health": 5,

        "damage": 20,

        "score": 30,

        "xp": 20,

        "body": (80, 255, 170),

        "belly": (205, 255, 235)
    },

    "BOSS": {

        "radius": 52,

        "speed": 64,

        "health": 40,

        "damage": 30,

        "score": 250,

        "xp": 70,

        "body": (255, 95, 55),

        "belly": (255, 220, 120)
    }
}

# =====================================================
# GAME STATE
# =====================================================

score = 0

wave = 1

wave_timer = 0.0

boss_waves_spawned = set()

game_state = "MENU"

menu_buttons = {}

settings_rects = {}

rule_back_rect = pygame.Rect(
    0,
    0,
    0,
    0
)

gameover_rects = {}

# =====================================================
# BASIC HELPERS
# =====================================================


def clamp(value, low, high):

    return max(
        low,
        min(high, value)
    )


def current_background_colour():

    b = brightness / 100

    if display_mode == "LIGHT":

        base = (
            250,
            251,
            255
        )

        return tuple(

            int(
                c * (
                    0.60
                    + 0.40 * b
                )
            )

            for c in base
        )

    base = get_theme()["background"]

    return tuple(

        int(
            c * (
                0.30
                + 0.70 * b
            )
        )

        for c in base
    )


def text_colour():

    if display_mode == "LIGHT":
        return BLACK

    return WHITE


def secondary_text_colour():

    if display_mode == "LIGHT":

        return (
            75,
            80,
            100
        )

    return SOFT_GREY


def panel_colour():

    if display_mode == "LIGHT":

        return (
            230,
            233,
            242
        )

    return get_theme()["panel"]


def grid_colour():

    if display_mode == "LIGHT":

        return (
            210,
            214,
            228
        )

    return get_theme()["grid"]


# =====================================================
# GLOW
# =====================================================


def draw_glow_circle(
    surface,
    colour,
    position,
    radius
):

    radius = max(
        1,
        int(radius)
    )

    glow_size = radius * 7

    glow = pygame.Surface(
        (
            glow_size,
            glow_size
        ),
        pygame.SRCALPHA
    )

    center = glow_size // 2

    pygame.draw.circle(

        glow,

        (*colour, 22),

        (center, center),

        radius * 3
    )

    pygame.draw.circle(

        glow,

        (*colour, 55),

        (center, center),

        radius * 2
    )

    pygame.draw.circle(

        glow,

        colour,

        (center, center),

        radius
    )

    surface.blit(

        glow,

        (
            int(
                position[0]
                - center
            ),

            int(
                position[1]
                - center
            )
        )
    )


# =====================================================
# BUTTON
# =====================================================


def draw_button(
    rect,
    label,
    active=False,
    accent=None,
    font=None
):

    theme = get_theme()

    accent = (
        accent
        or theme["accent"]
    )

    font = (
        font
        or small_font
    )

    hovered = rect.collidepoint(
        pygame.mouse.get_pos()
    )

    fill = panel_colour()

    if active:

        if display_mode == "DARK":

            fill = theme[
                "accent_2"
            ]

        else:

            fill = (
                215,
                220,
                245
            )

    elif hovered:

        if display_mode == "DARK":

            fill = theme[
                "accent_2"
            ]

        else:

            fill = (
                220,
                225,
                238
            )

    pygame.draw.rect(

        screen,

        fill,

        rect,

        border_radius=14
    )

    pygame.draw.rect(

        screen,

        accent,

        rect,

        3 if active else 2,

        border_radius=14
    )

    colour = text_colour()

    txt = font.render(
        label,
        True,
        colour
    )

    screen.blit(

        txt,

        txt.get_rect(
            center=rect.center
        )
    )


# =====================================================
# SLIDER
# =====================================================


def draw_slider(
    rect,
    value,
    low,
    high,
    label
):

    theme = get_theme()

    value = clamp(
        value,
        low,
        high
    )

    pct = (
        value - low
    ) / (
        high - low
    )

    label_text = small_font.render(

        f"{label}: {int(value)}%",

        True,

        text_colour()
    )

    screen.blit(

        label_text,

        (
            rect.x,
            rect.y - 32
        )
    )

    pygame.draw.rect(

        screen,

        grid_colour(),

        rect,

        border_radius=8
    )

    fill = pygame.Rect(

        rect.x,

        rect.y,

        int(
            rect.width * pct
        ),

        rect.height
    )

    pygame.draw.rect(

        screen,

        theme["accent"],

        fill,

        border_radius=8
    )

    knob_x = (
        rect.x
        + int(
            rect.width * pct
        )
    )

    pygame.draw.circle(

        screen,

        text_colour(),

        (
            knob_x,
            rect.centery
        ),

        11
    )

    pygame.draw.circle(

        screen,

        theme["accent"],

        (
            knob_x,
            rect.centery
        ),

        8
    )


# =====================================================
# BACKGROUND
# =====================================================


def draw_background(dt):

    theme = get_theme()

    screen.fill(
        current_background_colour()
    )

    if display_mode == "DARK":

        star_colour = theme[
            "star"
        ]

    else:

        star_colour = (
            150,
            155,
            175
        )

    for star in stars:

        star[1] += (
            star[3] * dt
        )

        if star[1] > HEIGHT:

            star[1] = 0

            star[0] = random.randint(
                0,
                WIDTH
            )

        pygame.draw.circle(

            screen,

            star_colour,

            (
                int(star[0]),
                int(star[1])
            ),

            star[2]
        )


def draw_grid():

    colour = grid_colour()

    for x in range(
        0,
        WIDTH,
        50
    ):

        pygame.draw.line(

            screen,

            colour,

            (x, 0),

            (x, HEIGHT)
        )

    for y in range(
        0,
        HEIGHT,
        50
    ):

        pygame.draw.line(

            screen,

            colour,

            (0, y),

            (WIDTH, y)
        )


# =====================================================
# AIM
# =====================================================


def aim_direction():

    mouse = pygame.Vector2(
        pygame.mouse.get_pos()
    )

    direction = (
        mouse - player
    )

    if direction.length() == 0:

        return pygame.Vector2(
            1,
            0
        )

    return direction.normalize()


# =====================================================
# CUTE MONSTER
# =====================================================


def draw_monster(
    pos,
    scale=1.0,
    aiming=True
):

    theme = get_theme()

    x = int(pos[0])

    y = int(pos[1])

    r = int(
        24 * scale
    )

    if aiming:

        aim = aim_direction()

    else:

        aim = pygame.Vector2(
            1,
            0
        )

    draw_glow_circle(

        screen,

        theme["accent"],

        (x, y),

        r + 2
    )

    pygame.draw.polygon(

        screen,

        theme[
            "monster_body"
        ],

        [

            (
                x - int(14 * scale),
                y - int(10 * scale)
            ),

            (
                x - int(24 * scale),
                y - int(30 * scale)
            ),

            (
                x - int(5 * scale),
                y - int(18 * scale)
            )
        ]
    )

    pygame.draw.polygon(

        screen,

        theme[
            "monster_body"
        ],

        [

            (
                x + int(14 * scale),
                y - int(10 * scale)
            ),

            (
                x + int(24 * scale),
                y - int(30 * scale)
            ),

            (
                x + int(5 * scale),
                y - int(18 * scale)
            )
        ]
    )

    pygame.draw.circle(

        screen,

        theme[
            "monster_body"
        ],

        (x, y),

        r
    )

    pygame.draw.circle(

        screen,

        theme[
            "monster_belly"
        ],

        (
            x,
            y + int(
                8 * scale
            )
        ),

        max(
            5,
            int(
                12 * scale
            )
        )
    )

    pygame.draw.circle(

        screen,

        theme[
            "monster_body"
        ],

        (
            x - int(10 * scale),

            y + int(20 * scale)
        ),

        max(
            3,
            int(6 * scale)
        )
    )

    pygame.draw.circle(

        screen,

        theme[
            "monster_body"
        ],

        (
            x + int(10 * scale),

            y + int(20 * scale)
        ),

        max(
            3,
            int(6 * scale)
        )
    )

    eye_r = max(
        3,
        int(6 * scale)
    )

    pupil_r = max(
        1,
        int(2 * scale)
    )

    eye_dx = int(
        8 * scale
    )

    eye_y = (
        y
        - int(5 * scale)
    )

    pupil_x = int(
        aim.x
        * 2
        * scale
    )

    pupil_y = int(
        aim.y
        * 2
        * scale
    )

    pygame.draw.circle(

        screen,

        WHITE,

        (
            x - eye_dx,
            eye_y
        ),

        eye_r
    )

    pygame.draw.circle(

        screen,

        WHITE,

        (
            x + eye_dx,
            eye_y
        ),

        eye_r
    )

    pygame.draw.circle(

        screen,

        BLACK,

        (
            x
            - eye_dx
            + pupil_x,

            eye_y
            + pupil_y
        ),

        pupil_r
    )

    pygame.draw.circle(

        screen,

        BLACK,

        (
            x
            + eye_dx
            + pupil_x,

            eye_y
            + pupil_y
        ),

        pupil_r
    )

    pygame.draw.arc(

        screen,

        BLACK,

        (
            x - int(10 * scale),

            y + int(1 * scale),

            int(20 * scale),

            int(12 * scale)
        ),

        0,

        math.pi,

        max(
            1,
            int(2 * scale)
        )
    )

    if aiming:

        muzzle = (
            pygame.Vector2(x, y)
            + aim
            * (
                34 * scale
            )
        )

        draw_glow_circle(

            screen,

            ORANGE,

            (
                int(muzzle.x),
                int(muzzle.y)
            ),

            max(
                3,
                int(5 * scale)
            )
        )


# =====================================================
# HUMAN CHARACTER
# =====================================================


def draw_human(
    pos,
    scale=1.0,
    aiming=True
):

    theme = get_theme()

    x = int(pos[0])

    y = int(pos[1])

    if aiming:

        aim = aim_direction()

    else:

        aim = pygame.Vector2(
            1,
            0
        )

    body = theme[
        "accent"
    ]

    trim = theme[
        "accent_2"
    ]

    skin = (
        255,
        210,
        170
    )

    hair = (
        45,
        30,
        35
    )

    draw_glow_circle(

        screen,

        body,

        (x, y),

        int(
            26 * scale
        )
    )

    # legs

    pygame.draw.line(

        screen,

        trim,

        (
            x - int(7 * scale),

            y + int(14 * scale)
        ),

        (
            x - int(11 * scale),

            y + int(30 * scale)
        ),

        max(
            3,
            int(6 * scale)
        )
    )

    pygame.draw.line(

        screen,

        trim,

        (
            x + int(7 * scale),

            y + int(14 * scale)
        ),

        (
            x + int(11 * scale),

            y + int(30 * scale)
        ),

        max(
            3,
            int(6 * scale)
        )
    )

    # torso

    torso = pygame.Rect(

        0,
        0,

        int(28 * scale),

        int(32 * scale)
    )

    torso.center = (

        x,

        y
        + int(8 * scale)
    )

    pygame.draw.rect(

        screen,

        body,

        torso,

        border_radius=max(
            4,
            int(8 * scale)
        )
    )

    pygame.draw.rect(

        screen,

        trim,

        torso,

        max(
            1,
            int(2 * scale)
        ),

        border_radius=max(
            4,
            int(8 * scale)
        )
    )

    # head

    head_y = (
        y
        - int(16 * scale)
    )

    pygame.draw.circle(

        screen,

        skin,

        (x, head_y),

        max(
            6,
            int(12 * scale)
        )
    )

    # hair

    pygame.draw.arc(

        screen,

        hair,

        (
            x - int(13 * scale),

            head_y
            - int(13 * scale),

            int(26 * scale),

            int(22 * scale)
        ),

        math.pi,

        math.pi * 2,

        max(
            2,
            int(7 * scale)
        )
    )

    # eyes

    pygame.draw.circle(

        screen,

        BLACK,

        (
            x - int(4 * scale),

            head_y
        ),

        max(
            1,
            int(1.8 * scale)
        )
    )

    pygame.draw.circle(

        screen,

        BLACK,

        (
            x + int(4 * scale),

            head_y
        ),

        max(
            1,
            int(1.8 * scale)
        )
    )

    # arm / fire blaster

    hand = (

        pygame.Vector2(
            x,
            y + int(2 * scale)
        )

        + aim
        * (
            24 * scale
        )
    )

    pygame.draw.line(

        screen,

        skin,

        (x, y),

        (
            int(hand.x),
            int(hand.y)
        ),

        max(
            3,
            int(5 * scale)
        )
    )

    pygame.draw.circle(

        screen,

        trim,

        (
            int(hand.x),
            int(hand.y)
        ),

        max(
            3,
            int(5 * scale)
        )
    )

    if aiming:

        muzzle = (

            pygame.Vector2(
                hand.x,
                hand.y
            )

            + aim
            * (
                13 * scale
            )
        )

        draw_glow_circle(

            screen,

            ORANGE,

            (
                int(muzzle.x),
                int(muzzle.y)
            ),

            max(
                3,
                int(5 * scale)
            )
        )


def draw_player():

    if character_choice == "MONSTER":

        draw_monster(
            player
        )

    else:

        draw_human(
            player
        )


# =====================================================
# MAIN MENU
# =====================================================


def draw_menu():

    global menu_buttons

    theme = get_theme()

    menu_buttons = {}

    shadow = title_font.render(

        "NEON SURVIVOR",

        True,

        theme[
            "accent_2"
        ]
    )

    title = title_font.render(

        "NEON SURVIVOR",

        True,

        theme[
            "accent"
        ]
    )

    screen.blit(

        shadow,

        shadow.get_rect(
            center=(
                WIDTH // 2 + 5,
                105
            )
        )
    )

    screen.blit(

        title,

        title.get_rect(
            center=(
                WIDTH // 2,
                100
            )
        )
    )

    subtitle = small_font.render(

        "PLAYER LAB EDITION",

        True,

        text_colour()
    )

    screen.blit(

        subtitle,

        subtitle.get_rect(
            center=(
                WIDTH // 2,
                157
            )
        )
    )

    preview_pos = (
        WIDTH // 2,
        255
    )

    if character_choice == "MONSTER":

        draw_monster(
            preview_pos,
            1.7,
            aiming=False
        )

    else:

        draw_human(
            preview_pos,
            1.7,
            aiming=False
        )

    play = pygame.Rect(

        WIDTH // 2 - 175,

        345,

        350,

        66
    )

    settings = pygame.Rect(

        WIDTH // 2 - 175,

        430,

        350,

        58
    )

    rules = pygame.Rect(

        WIDTH // 2 - 175,

        505,

        350,

        58
    )

    menu_buttons = {

        "PLAY": play,

        "SETTINGS": settings,

        "RULES": rules
    }

    draw_button(

        play,

        "PLAY",

        accent=theme[
            "accent"
        ],

        font=button_font
    )

    draw_button(

        settings,

        "PLAYER LAB / SETTINGS"
    )

    draw_button(

        rules,

        "HOW TO PLAY"
    )

    summary = (

        f"{character_choice}"

        f"  •  {display_mode}"

        f"  •  {selected_difficulty}"

        f"  •  SOUND {int(master_volume * 100)}%"
    )

    txt = tiny_font.render(

        summary,

        True,

        secondary_text_colour()
    )

    screen.blit(

        txt,

        txt.get_rect(
            center=(
                WIDTH // 2,
                600
            )
        )
    )

    version = tiny_font.render(

        "Fire. Evolve. Survive.",

        True,

        secondary_text_colour()
    )

    screen.blit(

        version,

        version.get_rect(
            center=(
                WIDTH // 2,
                642
            )
        )
    )


# =====================================================
# PLAYER LAB / SETTINGS
# =====================================================


def draw_settings():

    global settings_rects

    theme = get_theme()

    settings_rects = {}

    heading = heading_font.render(

        "PLAYER LAB",

        True,

        theme[
            "accent"
        ]
    )

    screen.blit(

        heading,

        heading.get_rect(
            center=(
                WIDTH // 2,
                48
            )
        )
    )

    # ---------------- CHARACTER ----------------

    label = small_font.render(

        "1. CHOOSE YOUR HERO",

        True,

        text_colour()
    )

    screen.blit(
        label,
        (105, 92)
    )

    monster_rect = pygame.Rect(
        105,
        123,
        215,
        72
    )

    human_rect = pygame.Rect(
        335,
        123,
        215,
        72
    )

    settings_rects[
        "MONSTER"
    ] = monster_rect

    settings_rects[
        "HUMAN"
    ] = human_rect

    draw_button(

        monster_rect,

        "MONSTER",

        character_choice
        == "MONSTER"
    )

    draw_button(

        human_rect,

        "HUMAN",

        character_choice
        == "HUMAN"
    )

    # ---------------- THEME ----------------

    label = small_font.render(

        "2. NEON WORLD",

        True,

        text_colour()
    )

    screen.blit(
        label,
        (105, 220)
    )

    for i, name in enumerate(
        theme_names
    ):

        rect = pygame.Rect(

            105 + i * 225,

            252,

            205,

            58
        )

        settings_rects[
            f"THEME_{i}"
        ] = rect

        draw_button(

            rect,

            name,

            i
            == selected_theme_index,

            accent=THEMES[
                name
            ][
                "accent"
            ],

            font=tiny_font
        )

    # ---------------- SCREEN ----------------

    label = small_font.render(

        "3. SCREEN STYLE",

        True,

        text_colour()
    )

    screen.blit(
        label,
        (105, 338)
    )

    dark_rect = pygame.Rect(
        105,
        370,
        160,
        54
    )

    light_rect = pygame.Rect(
        282,
        370,
        160,
        54
    )

    settings_rects[
        "DARK"
    ] = dark_rect

    settings_rects[
        "LIGHT"
    ] = light_rect

    draw_button(

        dark_rect,

        "DARK",

        display_mode
        == "DARK"
    )

    draw_button(

        light_rect,

        "LIGHT",

        display_mode
        == "LIGHT"
    )

    # ---------------- BRIGHTNESS ----------------

    brightness_rect = pygame.Rect(

        505,

        386,

        430,

        14
    )

    settings_rects[
        "BRIGHTNESS"
    ] = brightness_rect

    draw_slider(

        brightness_rect,

        brightness,

        20,

        100,

        "BRIGHTNESS"
    )

    # ---------------- DIFFICULTY ----------------

    label = small_font.render(

        "4. DIFFICULTY",

        True,

        text_colour()
    )

    screen.blit(
        label,
        (105, 463)
    )

    for i, name in enumerate(
        (
            "EASY",
            "MEDIUM",
            "HARD"
        )
    ):

        rect = pygame.Rect(

            105 + i * 190,

            495,

            170,

            56
        )

        settings_rects[
            f"DIFF_{name}"
        ] = rect

        draw_button(

            rect,

            name,

            selected_difficulty
            == name
        )

    diff_desc = {

        "EASY":
        "Relaxed spawns • slower enemies • softer damage",

        "MEDIUM":
        "Balanced survival experience",

        "HARD":
        "Faster swarm • stronger hits • higher score"

    }[
        selected_difficulty
    ]

    desc = tiny_font.render(

        diff_desc,

        True,

        secondary_text_colour()
    )

    screen.blit(
        desc,
        (105, 562)
    )

    # ---------------- SOUND ----------------

    volume_rect = pygame.Rect(

        690,

        512,

        420,

        14
    )

    settings_rects[
        "VOLUME"
    ] = volume_rect

    draw_slider(

        volume_rect,

        master_volume * 100,

        0,

        100,

        "SOUND"
    )

    if audio_ok:

        sound_state = "AUDIO ACTIVE"

    else:

        sound_state = (
            "AUDIO DEVICE UNAVAILABLE"
        )

    snd = tiny_font.render(

        sound_state,

        True,

        secondary_text_colour()
    )

    screen.blit(
        snd,
        (690, 545)
    )

    # ---------------- BACK ----------------

    back = pygame.Rect(

        WIDTH // 2 - 110,

        635,

        220,

        54
    )

    settings_rects[
        "BACK"
    ] = back

    draw_button(

        back,

        "SAVE & BACK",

        active=True
    )


# =====================================================
# RULE BOOK
# =====================================================


def draw_rules():

    global rule_back_rect

    theme = get_theme()

    heading = heading_font.render(

        "HOW TO SURVIVE",

        True,

        theme[
            "accent"
        ]
    )

    screen.blit(

        heading,

        heading.get_rect(
            center=(
                WIDTH // 2,
                55
            )
        )
    )

    left_x = 110

    right_x = 660

    y = 120

    left_lines = [

        (
            "CONTROLS",
            True
        ),

        (
            "WASD / Arrow Keys  —  Move",
            False
        ),

        (
            "Mouse  —  Aim",
            False
        ),

        (
            "Hold Left Click  —  Spread fire",
            False
        ),

        (
            "ESC  —  Return to menu",
            False
        ),

        (
            "",
            False
        ),

        (
            "YOUR GOAL",
            True
        ),

        (
            "Destroy enemies before they reach you.",
            False
        ),

        (
            "Collect glowing XP crystals.",
            False
        ),

        (
            "Fill the XP bar to level up.",
            False
        ),

        (
            "Pick 1 of 3 powers after each level.",
            False
        )
    ]

    right_lines = [

        (
            "ENEMIES",
            True
        ),

        (
            "Blob  —  normal enemy",
            False
        ),

        (
            "Bat  —  fast enemy",
            False
        ),

        (
            "Tank  —  slow but tough",
            False
        ),

        (
            "Boss  —  appears every 5 waves",
            False
        ),

        (
            "",
            False
        ),

        (
            "POWER TIPS",
            True
        ),

        (
            "Rapid Fire = attack faster",
            False
        ),

        (
            "Fire Power = more damage",
            False
        ),

        (
            "Triple Flame = wider attack",
            False
        ),

        (
            "Big Heart = more health",
            False
        )
    ]

    def draw_rule_column(
        lines,
        x,
        start_y
    ):

        yy = start_y

        for text, is_heading in lines:

            if text == "":

                yy += 14

                continue

            if is_heading:

                font = small_font

                colour = theme[
                    "accent_2"
                ]

            else:

                font = tiny_font

                colour = text_colour()

            surface = font.render(

                text,

                True,

                colour
            )

            screen.blit(

                surface,

                (
                    x,
                    yy
                )
            )

            if is_heading:

                yy += 35

            else:

                yy += 30

    draw_rule_column(

        left_lines,

        left_x,

        y
    )

    draw_rule_column(

        right_lines,

        right_x,

        y
    )

    tip_box = pygame.Rect(

        150,

        520,

        980,

        80
    )

    pygame.draw.rect(

        screen,

        panel_colour(),

        tip_box,

        border_radius=18
    )

    pygame.draw.rect(

        screen,

        theme[
            "accent"
        ],

        tip_box,

        2,

        border_radius=18
    )

    tip = small_font.render(

        "TIP: Keep moving. XP crystals become magnetic when you get close!",

        True,

        text_colour()
    )

    screen.blit(

        tip,

        tip.get_rect(
            center=tip_box.center
        )
    )

    rule_back_rect = pygame.Rect(

        WIDTH // 2 - 110,

        630,

        220,

        52
    )

    draw_button(

        rule_back_rect,

        "BACK"
    )


# =====================================================
# SHOOT
# =====================================================


def shoot():

    global last_shot

    now = pygame.time.get_ticks()

    if (
        now - last_shot
        < shoot_delay
    ):

        return

    direction = aim_direction()

    if multishot == 1:

        angles = [0]

    elif multishot == 2:

        angles = [
            -6,
            6
        ]

    else:

        angles = [
            -10,
            0,
            10
        ]

    for angle in angles:

        shot_dir = direction.rotate(
            angle
        )

        start = (

            player
            + shot_dir * 35
        )

        fireballs.append({

            "position":
            start.copy(),

            "velocity":
            shot_dir
            * fireball_speed,

            "life":
            1.25,

            "damage":
            fireball_damage
        })

    if shoot_sound:

        shoot_sound.play()

    last_shot = now


def update_fireballs(dt):

    for fireball in fireballs[:]:

        fireball[
            "position"
        ] += (
            fireball[
                "velocity"
            ]
            * dt
        )

        fireball[
            "life"
        ] -= dt

        x = fireball[
            "position"
        ].x

        y = fireball[
            "position"
        ].y

        if (
            x < -60
            or x > WIDTH + 60
            or y < -60
            or y > HEIGHT + 60
            or fireball["life"] <= 0
        ):

            fireballs.remove(
                fireball
            )


def draw_fireballs():

    for fireball in fireballs:

        x = int(
            fireball[
                "position"
            ].x
        )

        y = int(
            fireball[
                "position"
            ].y
        )

        vel = fireball[
            "velocity"
        ]

        if vel.length() > 0:

            tail = (

                pygame.Vector2(
                    x,
                    y
                )

                - vel.normalize()
                * 16
            )

            pygame.draw.line(

                screen,

                ORANGE,

                (x, y),

                (
                    int(tail.x),
                    int(tail.y)
                ),

                5
            )

        draw_glow_circle(

            screen,

            ORANGE,

            (x, y),

            fireball_radius + 2
        )

        pygame.draw.circle(

            screen,

            YELLOW,

            (x, y),

            fireball_radius
        )

        pygame.draw.circle(

            screen,

            WHITE,

            (x, y),

            3
        )


# =====================================================
# SPAWNING
# =====================================================


def spawn_position():

    side = random.choice(

        (
            "TOP",
            "BOTTOM",
            "LEFT",
            "RIGHT"
        )
    )

    if side == "TOP":

        return pygame.Vector2(

            random.randint(
                0,
                WIDTH
            ),

            -70
        )

    if side == "BOTTOM":

        return pygame.Vector2(

            random.randint(
                0,
                WIDTH
            ),

            HEIGHT + 70
        )

    if side == "LEFT":

        return pygame.Vector2(

            -70,

            random.randint(
                0,
                HEIGHT
            )
        )

    return pygame.Vector2(

        WIDTH + 70,

        random.randint(
            0,
            HEIGHT
        )
    )


# =====================================================
# CREATE ENEMY
# =====================================================


def create_enemy(
    kind=None
):

    diff = DIFFICULTIES[
        selected_difficulty
    ]

    if kind is None:

        roll = random.random()

        if wave < 3:

            if roll < 0.78:

                kind = "BLOB"

            else:

                kind = "BAT"

        elif wave < 5:

            if roll < 0.52:

                kind = "BLOB"

            elif roll < 0.82:

                kind = "BAT"

            else:

                kind = "TANK"

        else:

            if roll < 0.40:

                kind = "BLOB"

            elif roll < 0.72:

                kind = "BAT"

            else:

                kind = "TANK"

    data = ENEMY_TYPES[
        kind
    ]

    pos = spawn_position()

    if kind == "BOSS":

        wave_hp = 1.0

    else:

        wave_hp = (
            1
            + (
                wave - 1
            )
            * 0.10
        )

    hp = max(

        1,

        int(

            data[
                "health"
            ]

            * wave_hp

            * diff[
                "hp"
            ]
        )
    )

    enemies.append({

        "type":
        kind,

        "position":
        pos,

        "radius":
        data[
            "radius"
        ],

        "speed":

        (
            data[
                "speed"
            ]

            + (
                wave - 1
            )
            * 2
        )

        * diff[
            "speed"
        ],

        "health":
        hp,

        "max_health":
        hp,

        "damage":

        max(

            1,

            int(

                data[
                    "damage"
                ]

                * diff[
                    "damage"
                ]
            )
        ),

        "score":

        max(

            1,

            int(

                data[
                    "score"
                ]

                * diff[
                    "score"
                ]
            )
        ),

        "xp":
        data[
            "xp"
        ],

        "body":
        data[
            "body"
        ],

        "belly":
        data[
            "belly"
        ]
    })


# =====================================================
# DRAW ENEMY
# =====================================================


def draw_enemy(enemy):

    x = int(
        enemy[
            "position"
        ].x
    )

    y = int(
        enemy[
            "position"
        ].y
    )

    r = enemy[
        "radius"
    ]

    draw_glow_circle(

        screen,

        enemy[
            "body"
        ],

        (x, y),

        r
    )

    pygame.draw.circle(

        screen,

        enemy[
            "body"
        ],

        (x, y),

        r
    )

    pygame.draw.circle(

        screen,

        enemy[
            "belly"
        ],

        (
            x,
            y + r // 4
        ),

        max(
            8,
            r // 2
        )
    )

    if enemy[
        "type"
    ] == "BOSS":

        pygame.draw.polygon(

            screen,

            enemy[
                "body"
            ],

            [

                (
                    x - 30,
                    y - 28
                ),

                (
                    x - 45,
                    y - 60
                ),

                (
                    x - 10,
                    y - 40
                )
            ]
        )

        pygame.draw.polygon(

            screen,

            enemy[
                "body"
            ],

            [

                (
                    x + 30,
                    y - 28
                ),

                (
                    x + 45,
                    y - 60
                ),

                (
                    x + 10,
                    y - 40
                )
            ]
        )

    eye_spacing = max(
        6,
        r // 3
    )

    if enemy[
        "type"
    ] == "BOSS":

        eye_radius = 6

    else:

        eye_radius = 4

    pygame.draw.circle(

        screen,

        WHITE,

        (
            x - eye_spacing,
            y - 5
        ),

        eye_radius
    )

    pygame.draw.circle(

        screen,

        WHITE,

        (
            x + eye_spacing,
            y - 5
        ),

        eye_radius
    )

    pygame.draw.circle(

        screen,

        BLACK,

        (
            x - eye_spacing,
            y - 5
        ),

        max(
            2,
            eye_radius // 2
        )
    )

    pygame.draw.circle(

        screen,

        BLACK,

        (
            x + eye_spacing,
            y - 5
        ),

        max(
            2,
            eye_radius // 2
        )
    )

    if enemy[
        "type"
    ] in (
        "TANK",
        "BOSS"
    ):

        bar_w = r * 2

        pct = (

            max(
                0,
                enemy[
                    "health"
                ]
            )

            / enemy[
                "max_health"
            ]
        )

        pygame.draw.rect(

            screen,

            BLACK,

            (
                x - r,
                y - r - 14,
                bar_w,
                6
            )
        )

        pygame.draw.rect(

            screen,

            RED,

            (
                x - r,
                y - r - 14,

                int(
                    bar_w
                    * pct
                ),

                6
            )
        )


def draw_enemies():

    for enemy in enemies:

        draw_enemy(
            enemy
        )


# =====================================================
# ENEMY MOVEMENT
# =====================================================


def update_enemies(dt):

    global health

    global score

    for enemy in enemies[:]:

        direction = (

            player
            - enemy[
                "position"
            ]
        )

        if direction.length() > 0:

            direction = (
                direction.normalize()
            )

            enemy[
                "position"
            ] += (

                direction

                * enemy[
                    "speed"
                ]

                * dt
            )

        if (
            enemy[
                "position"
            ].distance_to(
                player
            )

            < enemy[
                "radius"
            ]
            + player_radius
        ):

            health -= enemy[
                "damage"
            ]

            if hit_sound:

                hit_sound.play()

            if enemy[
                "type"
            ] == "BOSS":

                enemy[
                    "position"
                ] -= (
                    direction
                    * 100
                )

            elif enemy in enemies:

                enemies.remove(
                    enemy
                )

            continue

        for fireball in fireballs[:]:

            if (
                enemy[
                    "position"
                ].distance_to(
                    fireball[
                        "position"
                    ]
                )

                < enemy[
                    "radius"
                ]
                + fireball_radius
            ):

                enemy[
                    "health"
                ] -= fireball[
                    "damage"
                ]

                if fireball in fireballs:

                    fireballs.remove(
                        fireball
                    )

                if enemy[
                    "health"
                ] <= 0:

                    if enemy in enemies:

                        enemies.remove(
                            enemy
                        )

                    score += enemy[
                        "score"
                    ]

                    drop_xp(

                        enemy[
                            "position"
                        ],

                        enemy[
                            "xp"
                        ]
                    )

                break


# =====================================================
# XP
# =====================================================


def drop_xp(
    position,
    amount
):

    if amount >= 60:

        pieces = 5

    elif amount >= 20:

        pieces = 2

    else:

        pieces = 1

    value = max(

        1,

        amount // pieces
    )

    for _ in range(
        pieces
    ):

        offset = pygame.Vector2(

            random.randint(
                -16,
                16
            ),

            random.randint(
                -16,
                16
            )
        )

        xp_gems.append({

            "position":
            position.copy()
            + offset,

            "value":
            value
        })


def update_xp_gems(dt):

    global xp

    global level

    global xp_needed

    global game_state

    global upgrade_options

    for gem in xp_gems[:]:

        distance = gem[
            "position"
        ].distance_to(
            player
        )

        if (
            0
            < distance
            < 150
        ):

            gem[
                "position"
            ] += (

                (
                    player
                    - gem[
                        "position"
                    ]
                ).normalize()

                * 330

                * dt
            )

        if (
            distance
            < player_radius
            + 12
        ):

            xp += gem[
                "value"
            ]

            xp_gems.remove(
                gem
            )

    if (
        xp >= xp_needed
        and game_state
        == "GAME"
    ):

        xp -= xp_needed

        level += 1

        xp_needed = int(
            xp_needed
            * 1.32
        )

        upgrade_options = (
            random.sample(
                UPGRADES,
                3
            )
        )

        if level_sound:

            level_sound.play()

        game_state = "LEVELUP"


def draw_xp_gems():

    for gem in xp_gems:

        x = int(
            gem[
                "position"
            ].x
        )

        y = int(
            gem[
                "position"
            ].y
        )

        points = [

            (
                x,
                y - 8
            ),

            (
                x + 7,
                y
            ),

            (
                x,
                y + 8
            ),

            (
                x - 7,
                y
            )
        ]

        pygame.draw.polygon(

            screen,

            XP_COLOUR,

            points
        )

        pygame.draw.polygon(

            screen,

            WHITE,

            points,

            1
        )


def draw_xp_bar():

    theme = get_theme()

    bar_w = 440

    bar_h = 16

    x = (
        WIDTH // 2
        - bar_w // 2
    )

    y = 20

    pygame.draw.rect(

        screen,

        panel_colour(),

        (
            x,
            y,
            bar_w,
            bar_h
        ),

        border_radius=8
    )

    pct = min(

        1,

        xp / xp_needed
    )

    pygame.draw.rect(

        screen,

        theme[
            "accent"
        ],

        (
            x,
            y,

            int(
                bar_w
                * pct
            ),

            bar_h
        ),

        border_radius=8
    )

    pygame.draw.rect(

        screen,

        text_colour(),

        (
            x,
            y,
            bar_w,
            bar_h
        ),

        2,

        border_radius=8
    )

    txt = tiny_font.render(

        f"LEVEL {level}   XP {xp}/{xp_needed}",

        True,

        text_colour()
    )

    screen.blit(

        txt,

        txt.get_rect(
            center=(
                WIDTH // 2,
                y + 30
            )
        )
    )


# =====================================================
# LEVEL-UP SCREEN
# =====================================================


def draw_level_up():

    global upgrade_card_rects

    theme = get_theme()

    overlay = pygame.Surface(

        (
            WIDTH,
            HEIGHT
        ),

        pygame.SRCALPHA
    )

    overlay.fill(
        (
            0,
            0,
            0,
            185
        )
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    heading = title_font.render(

        f"LEVEL {level}!",

        True,

        theme[
            "accent"
        ]
    )

    screen.blit(

        heading,

        heading.get_rect(
            center=(
                WIDTH // 2,
                130
            )
        )
    )

    sub = small_font.render(

        "Choose one new power",

        True,

        WHITE
    )

    screen.blit(

        sub,

        sub.get_rect(
            center=(
                WIDTH // 2,
                205
            )
        )
    )

    upgrade_card_rects = []

    start_x = (
        WIDTH // 2
        - 480
    )

    for i, (
        name,
        desc
    ) in enumerate(
        upgrade_options
    ):

        card = pygame.Rect(

            start_x
            + i * 330,

            285,

            300,

            220
        )

        upgrade_card_rects.append(
            card
        )

        if card.collidepoint(
            pygame.mouse.get_pos()
        ):

            fill = theme[
                "accent_2"
            ]

        else:

            fill = theme[
                "panel"
            ]

        pygame.draw.rect(

            screen,

            fill,

            card,

            border_radius=20
        )

        pygame.draw.rect(

            screen,

            theme[
                "accent"
            ],

            card,

            3,

            border_radius=20
        )

        num = button_font.render(

            str(i + 1),

            True,

            theme[
                "accent"
            ]
        )

        screen.blit(

            num,

            num.get_rect(
                center=(
                    card.centerx,
                    card.y + 42
                )
            )
        )

        nm = small_font.render(

            name,

            True,

            WHITE
        )

        screen.blit(

            nm,

            nm.get_rect(
                center=(
                    card.centerx,
                    card.y + 100
                )
            )
        )

        ds = tiny_font.render(

            desc,

            True,

            WHITE
        )

        screen.blit(

            ds,

            ds.get_rect(
                center=(
                    card.centerx,
                    card.y + 145
                )
            )
        )

    bottom = tiny_font.render(

        "Press 1 / 2 / 3 or click a card",

        True,

        WHITE
    )

    screen.blit(

        bottom,

        bottom.get_rect(
            center=(
                WIDTH // 2,
                570
            )
        )
    )


def apply_upgrade(index):

    global shoot_delay

    global fireball_damage

    global player_speed

    global max_health

    global health

    global multishot

    global fireball_radius

    global game_state

    if not (
        0
        <= index
        < len(
            upgrade_options
        )
    ):

        return

    name = upgrade_options[
        index
    ][0]

    if name == "RAPID FIRE":

        shoot_delay = max(

            65,

            int(
                shoot_delay
                * 0.82
            )
        )

    elif name == "FIRE POWER":

        fireball_damage += 1

    elif name == "SWIFT PAWS":

        player_speed += 45

    elif name == "BIG HEART":

        max_health += 25

        health = min(

            max_health,

            health + 35
        )

    elif name == "TRIPLE FLAME":

        multishot = min(

            3,

            multishot + 1
        )

    elif name == "GIANT FLAME":

        fireball_radius = min(

            16,

            fireball_radius + 2
        )

    game_state = "GAME"


# =====================================================
# HUD
# =====================================================


def draw_health_bar():

    bar_w = 290

    bar_h = 22

    x = 25

    y = 25

    pygame.draw.rect(

        screen,

        panel_colour(),

        (
            x,
            y,
            bar_w,
            bar_h
        ),

        border_radius=10
    )

    hp_w = int(

        bar_w

        * max(
            0,
            health
        )

        / max_health
    )

    pygame.draw.rect(

        screen,

        RED,

        (
            x,
            y,
            hp_w,
            bar_h
        ),

        border_radius=10
    )

    pygame.draw.rect(

        screen,

        text_colour(),

        (
            x,
            y,
            bar_w,
            bar_h
        ),

        2,

        border_radius=10
    )

    txt = tiny_font.render(

        f"HP {max(0, health)} / {max_health}",

        True,

        text_colour()
    )

    screen.blit(
        txt,
        (x, y + 30)
    )


def draw_boss_bar():

    bosses = [

        e

        for e in enemies

        if e[
            "type"
        ] == "BOSS"
    ]

    if not bosses:

        return

    boss = bosses[0]

    bar_w = 500

    bar_h = 20

    x = (
        WIDTH // 2
        - bar_w // 2
    )

    y = 72

    pygame.draw.rect(

        screen,

        panel_colour(),

        (
            x,
            y,
            bar_w,
            bar_h
        ),

        border_radius=8
    )

    pct = (

        max(
            0,
            boss[
                "health"
            ]
        )

        / boss[
            "max_health"
        ]
    )

    pygame.draw.rect(

        screen,

        ORANGE,

        (
            x,
            y,

            int(
                bar_w
                * pct
            ),

            bar_h
        ),

        border_radius=8
    )

    pygame.draw.rect(

        screen,

        text_colour(),

        (
            x,
            y,
            bar_w,
            bar_h
        ),

        2,

        border_radius=8
    )

    txt = tiny_font.render(

        "BOSS",

        True,

        text_colour()
    )

    screen.blit(

        txt,

        txt.get_rect(
            center=(
                WIDTH // 2,
                y - 13
            )
        )
    )


def draw_hud():

    theme = get_theme()

    draw_health_bar()

    draw_xp_bar()

    draw_boss_bar()

    score_text = hud_font.render(

        f"SCORE: {score}",

        True,

        theme[
            "accent"
        ]
    )

    screen.blit(

        score_text,

        (
            WIDTH
            - score_text.get_width()
            - 25,

            22
        )
    )

    wave_text = small_font.render(

        f"WAVE {wave}  •  {selected_difficulty}",

        True,

        text_colour()
    )

    screen.blit(

        wave_text,

        (
            WIDTH
            - wave_text.get_width()
            - 25,

            58
        )
    )

    info = tiny_font.render(

        "WASD MOVE • HOLD LEFT CLICK FIRE • COLLECT XP • ESC MENU",

        True,

        text_colour()
    )

    screen.blit(

        info,

        info.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 25
            )
        )
    )


# =====================================================
# GAME OVER
# =====================================================


def draw_game_over():

    global gameover_rects

    theme = get_theme()

    gameover_rects = {}

    over = title_font.render(

        "GAME OVER",

        True,

        RED
    )

    screen.blit(

        over,

        over.get_rect(
            center=(
                WIDTH // 2,
                180
            )
        )
    )

    score_text = button_font.render(

        f"FINAL SCORE: {score}",

        True,

        text_colour()
    )

    screen.blit(

        score_text,

        score_text.get_rect(
            center=(
                WIDTH // 2,
                285
            )
        )
    )

    level_text = small_font.render(

        f"LEVEL {level} • WAVE {wave} • {selected_difficulty}",

        True,

        theme[
            "accent"
        ]
    )

    screen.blit(

        level_text,

        level_text.get_rect(
            center=(
                WIDTH // 2,
                340
            )
        )
    )

    restart = pygame.Rect(

        WIDTH // 2 - 150,

        400,

        300,

        58
    )

    menu = pygame.Rect(

        WIDTH // 2 - 150,

        475,

        300,

        58
    )

    gameover_rects = {

        "RESTART":
        restart,

        "MENU":
        menu
    }

    draw_button(

        restart,

        "PLAY AGAIN",

        active=True
    )

    draw_button(

        menu,

        "MAIN MENU"
    )


# =====================================================
# RESET GAME
# =====================================================


def reset_game():

    global player

    global player_speed

    global health

    global max_health

    global fireballs

    global fireball_damage

    global fireball_radius

    global shoot_delay

    global last_shot

    global multishot

    global enemies

    global xp_gems

    global score

    global level

    global xp

    global xp_needed

    global wave

    global wave_timer

    global boss_waves_spawned

    global last_enemy_spawn

    player = pygame.Vector2(

        WIDTH // 2,

        HEIGHT // 2
    )

    player_speed = 330

    max_health = 100

    health = 100

    fireballs = []

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

    wave_timer = 0.0

    boss_waves_spawned = set()

    last_enemy_spawn = (
        pygame.time.get_ticks()
    )


# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:

    dt = (
        clock.tick(FPS)
        / 1000
    )

    now = pygame.time.get_ticks()

    # =================================================
    # EVENTS
    # =================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state in (

                    "GAME",

                    "GAMEOVER",

                    "SETTINGS",

                    "RULES"
                ):

                    game_state = "MENU"

            if (
                game_state == "MENU"
                and event.key == pygame.K_RETURN
            ):

                reset_game()

                game_state = "GAME"

            elif (
                game_state == "GAMEOVER"
                and event.key == pygame.K_RETURN
            ):

                reset_game()

                game_state = "GAME"

            elif game_state == "LEVELUP":

                if event.key == pygame.K_1:

                    apply_upgrade(0)

                elif event.key == pygame.K_2:

                    apply_upgrade(1)

                elif event.key == pygame.K_3:

                    apply_upgrade(2)

        # =============================================
        # MOUSE CLICK
        # =============================================

        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            # ---------------- MENU ----------------

            if game_state == "MENU":

                if menu_buttons.get(

                    "PLAY",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    reset_game()

                    game_state = "GAME"

                elif menu_buttons.get(

                    "SETTINGS",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    game_state = (
                        "SETTINGS"
                    )

                elif menu_buttons.get(

                    "RULES",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    game_state = (
                        "RULES"
                    )

            # ---------------- SETTINGS ----------------

            elif game_state == "SETTINGS":

                if settings_rects.get(

                    "MONSTER",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    character_choice = (
                        "MONSTER"
                    )

                elif settings_rects.get(

                    "HUMAN",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    character_choice = (
                        "HUMAN"
                    )

                # Themes

                for i in range(
                    len(
                        theme_names
                    )
                ):

                    if settings_rects.get(

                        f"THEME_{i}",

                        pygame.Rect(
                            0,
                            0,
                            0,
                            0
                        )

                    ).collidepoint(
                        event.pos
                    ):

                        selected_theme_index = i

                # Dark / Light

                if settings_rects.get(

                    "DARK",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    display_mode = (
                        "DARK"
                    )

                elif settings_rects.get(

                    "LIGHT",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    display_mode = (
                        "LIGHT"
                    )

                # Difficulty

                for name in (
                    "EASY",
                    "MEDIUM",
                    "HARD"
                ):

                    if settings_rects.get(

                        f"DIFF_{name}",

                        pygame.Rect(
                            0,
                            0,
                            0,
                            0
                        )

                    ).collidepoint(
                        event.pos
                    ):

                        selected_difficulty = name

                if settings_rects.get(

                    "BACK",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    game_state = "MENU"

            # ---------------- RULES ----------------

            elif game_state == "RULES":

                if rule_back_rect.collidepoint(
                    event.pos
                ):

                    game_state = "MENU"

            # ---------------- LEVELUP ----------------

            elif game_state == "LEVELUP":

                for i, card in enumerate(
                    upgrade_card_rects
                ):

                    if card.collidepoint(
                        event.pos
                    ):

                        apply_upgrade(i)

                        break

            # ---------------- GAMEOVER ----------------

            elif game_state == "GAMEOVER":

                if gameover_rects.get(

                    "RESTART",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    reset_game()

                    game_state = "GAME"

                elif gameover_rects.get(

                    "MENU",

                    pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

                ).collidepoint(
                    event.pos
                ):

                    game_state = "MENU"

    # =================================================
    # SLIDERS
    # =================================================

    if (
        game_state == "SETTINGS"
        and pygame.mouse.get_pressed()[0]
    ):

        mx, my = pygame.mouse.get_pos()

        brect = settings_rects.get(
            "BRIGHTNESS"
        )

        if (
            brect
            and brect.y - 18
            <= my
            <= brect.bottom + 18
            and brect.x - 12
            <= mx
            <= brect.right + 12
        ):

            pct = clamp(

                (
                    mx
                    - brect.x
                )

                / brect.width,

                0,

                1
            )

            brightness = int(

                20
                + pct * 80
            )

        vrect = settings_rects.get(
            "VOLUME"
        )

        if (
            vrect
            and vrect.y - 18
            <= my
            <= vrect.bottom + 18
            and vrect.x - 12
            <= mx
            <= vrect.right + 12
        ):

            pct = clamp(

                (
                    mx
                    - vrect.x
                )

                / vrect.width,

                0,

                1
            )

            master_volume = pct

            set_sound_volume()

    # =================================================
    # GAME UPDATE
    # =================================================

    if game_state == "GAME":

        keys = pygame.key.get_pressed()

        movement = pygame.Vector2(
            0,
            0
        )

        if (
            keys[pygame.K_w]
            or keys[pygame.K_UP]
        ):

            movement.y -= 1

        if (
            keys[pygame.K_s]
            or keys[pygame.K_DOWN]
        ):

            movement.y += 1

        if (
            keys[pygame.K_a]
            or keys[pygame.K_LEFT]
        ):

            movement.x -= 1

        if (
            keys[pygame.K_d]
            or keys[pygame.K_RIGHT]
        ):

            movement.x += 1

        if movement.length() > 0:

            player += (

                movement.normalize()

                * player_speed

                * dt
            )

        player.x = clamp(

            player.x,

            player_radius,

            WIDTH - player_radius
        )

        player.y = clamp(

            player.y,

            player_radius,

            HEIGHT - player_radius
        )

        if pygame.mouse.get_pressed()[0]:

            shoot()

        # ---------------- WAVES ----------------

        wave_timer += dt

        if wave_timer >= 20:

            wave_timer = 0

            wave += 1

        # Boss every 5 waves

        if (
            wave % 5 == 0
            and wave
            not in boss_waves_spawned
        ):

            create_enemy(
                "BOSS"
            )

            boss_waves_spawned.add(
                wave
            )

        # Difficulty affects spawn rate

        diff = DIFFICULTIES[
            selected_difficulty
        ]

        spawn_delay = max(

            220,

            (
                base_enemy_spawn_delay

                - (
                    wave - 1
                )
                * 55

                - min(
                    score,
                    3000
                )
                // 20
            )

            * diff[
                "spawn"
            ]
        )

        if (
            now
            - last_enemy_spawn
            >= spawn_delay
        ):

            create_enemy()

            last_enemy_spawn = now

        update_fireballs(dt)

        update_enemies(dt)

        update_xp_gems(dt)

        if health <= 0:

            game_state = (
                "GAMEOVER"
            )

    # =================================================
    # DRAW
    # =================================================

    draw_background(dt)

    if game_state == "MENU":

        draw_menu()

    elif game_state == "SETTINGS":

        draw_settings()

    elif game_state == "RULES":

        draw_rules()

    elif game_state in (
        "GAME",
        "LEVELUP"
    ):

        draw_grid()

        draw_xp_gems()

        draw_fireballs()

        draw_enemies()

        draw_player()

        draw_hud()

        if game_state == "LEVELUP":

            draw_level_up()

    elif game_state == "GAMEOVER":

        draw_game_over()

    pygame.display.flip()


pygame.quit()
