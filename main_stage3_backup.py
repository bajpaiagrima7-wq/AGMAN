import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Survivor")
clock = pygame.time.Clock()

# -------------------- FONTS --------------------
title_font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 44)
hud_font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 27)
tiny_font = pygame.font.Font(None, 22)

# -------------------- COMMON COLOURS --------------------
WHITE = (245, 245, 255)
BLACK = (12, 12, 18)
RED = (255, 70, 90)
YELLOW = (255, 220, 70)
ORANGE = (255, 135, 40)
XP_COLOUR = (120, 255, 220)

# -------------------- THEMES --------------------
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
    return THEMES[theme_names[selected_theme_index]]

# -------------------- BACKGROUND --------------------
stars = [
    [random.randint(0, WIDTH), random.randint(0, HEIGHT),
     random.randint(1, 3), random.uniform(10, 40)]
    for _ in range(120)
]

# -------------------- PLAYER --------------------
player = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_radius = 24
player_speed = 330

max_health = 100
health = 100

# -------------------- FIRE --------------------
fireballs = []
fireball_speed = 780
fireball_radius = 7
fireball_damage = 1
shoot_delay = 150
last_shot = 0
multishot = 1

# -------------------- XP / LEVEL --------------------
xp_gems = []
xp = 0
level = 1
xp_needed = 50

upgrade_options = []
upgrade_card_rects = []

# -------------------- ENEMIES --------------------
enemies = []
last_enemy_spawn = 0
base_enemy_spawn_delay = 900

ENEMY_TYPES = {
    "BLOB": {
        "radius": 20, "speed": 95, "health": 2,
        "damage": 10, "score": 10, "xp": 10,
        "body": (255, 75, 170), "belly": (255, 200, 225)
    },
    "BAT": {
        "radius": 16, "speed": 150, "health": 1,
        "damage": 10, "score": 15, "xp": 12,
        "body": (170, 110, 255), "belly": (220, 205, 255)
    },
    "TANK": {
        "radius": 28, "speed": 72, "health": 5,
        "damage": 20, "score": 30, "xp": 20,
        "body": (80, 255, 170), "belly": (205, 255, 235)
    },
    "BOSS": {
        "radius": 52, "speed": 64, "health": 40,
        "damage": 30, "score": 250, "xp": 70,
        "body": (255, 95, 55), "belly": (255, 220, 120)
    }
}

# -------------------- GAME STATE --------------------
score = 0
wave = 1
wave_timer = 0.0
boss_waves_spawned = set()

game_state = "MENU"
play_button = pygame.Rect(0, 0, 0, 0)
theme_card_rects = []

# -------------------- UPGRADES --------------------
UPGRADES = [
    ("RAPID FIRE", "Shoot 18% faster"),
    ("FIRE POWER", "+1 fireball damage"),
    ("SWIFT PAWS", "+45 movement speed"),
    ("BIG HEART", "+25 max HP and heal"),
    ("TRIPLE FLAME", "Shoot extra fireballs"),
    ("GIANT FLAME", "Bigger fireballs")
]

# =====================================================
# DRAW HELPERS
# =====================================================

def draw_glow_circle(surface, colour, position, radius):
    radius = max(1, int(radius))
    glow_size = radius * 7
    glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    center = glow_size // 2

    pygame.draw.circle(glow, (*colour, 22), (center, center), radius * 3)
    pygame.draw.circle(glow, (*colour, 55), (center, center), radius * 2)
    pygame.draw.circle(glow, colour, (center, center), radius)

    surface.blit(
        glow,
        (int(position[0] - center), int(position[1] - center))
    )


def draw_background(dt):
    theme = get_theme()
    screen.fill(theme["background"])

    for star in stars:
        star[1] += star[3] * dt

        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

        pygame.draw.circle(
            screen,
            theme["star"],
            (int(star[0]), int(star[1])),
            star[2]
        )


def draw_grid():
    theme = get_theme()

    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, theme["grid"], (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, theme["grid"], (0, y), (WIDTH, y))

# =====================================================
# MENU
# =====================================================

def draw_menu():
    global theme_card_rects

    theme = get_theme()
    theme_card_rects = []

    shadow = title_font.render("NEON SURVIVOR", True, theme["accent_2"])
    title = title_font.render("NEON SURVIVOR", True, theme["accent"])

    screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 5, 155)))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

    subtitle = small_font.render(
        "Cute Monster • Fire • XP • Boss Battles",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(center=(WIDTH // 2, 225))
    )

    play = pygame.Rect(WIDTH // 2 - 150, 285, 300, 75)
    mouse = pygame.mouse.get_pos()

    fill = theme["accent_2"] if play.collidepoint(mouse) else theme["panel"]

    pygame.draw.rect(screen, fill, play, border_radius=18)
    pygame.draw.rect(screen, theme["accent"], play, 3, border_radius=18)

    text = button_font.render("PLAY", True, WHITE)
    screen.blit(text, text.get_rect(center=play.center))

    label = tiny_font.render("CHOOSE YOUR NEON WORLD", True, WHITE)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 415)))

    card_y = 455
    start_x = WIDTH // 2 - 360

    for i, name in enumerate(theme_names):
        x = start_x + i * 245

        card = pygame.Rect(x, card_y, 220, 100)
        theme_card_rects.append(card)

        t = THEMES[name]

        border = t["accent"] if i == selected_theme_index else WHITE

        pygame.draw.rect(screen, t["panel"], card, border_radius=16)
        pygame.draw.rect(screen, border, card, 3, border_radius=16)

        pygame.draw.circle(screen, t["accent"], (x + 40, card_y + 35), 11)
        pygame.draw.circle(screen, t["accent_2"], (x + 70, card_y + 35), 11)
        pygame.draw.circle(screen, t["monster_body"], (x + 100, card_y + 35), 11)

        name_text = tiny_font.render(name, True, WHITE)
        screen.blit(name_text, (x + 18, card_y + 62))

    controls = tiny_font.render(
        "1 / 2 / 3 = theme   •   ENTER = play   •   Mouse = choose",
        True,
        WHITE
    )

    screen.blit(
        controls,
        controls.get_rect(center=(WIDTH // 2, HEIGHT - 45))
    )

    return play

# =====================================================
# PLAYER
# =====================================================

def draw_player():
    theme = get_theme()

    x = int(player.x)
    y = int(player.y)

    mouse = pygame.Vector2(pygame.mouse.get_pos())
    aim = mouse - player

    if aim.length() == 0:
        aim = pygame.Vector2(1, 0)
    else:
        aim = aim.normalize()

    draw_glow_circle(screen, theme["accent"], (x, y), player_radius + 2)

    left_ear = [
        (x - 14, y - 10),
        (x - 24, y - 30),
        (x - 5, y - 18)
    ]

    right_ear = [
        (x + 14, y - 10),
        (x + 24, y - 30),
        (x + 5, y - 18)
    ]

    pygame.draw.polygon(screen, theme["monster_body"], left_ear)
    pygame.draw.polygon(screen, theme["monster_body"], right_ear)

    pygame.draw.circle(
        screen,
        theme["monster_body"],
        (x, y),
        player_radius
    )

    pygame.draw.circle(
        screen,
        theme["monster_belly"],
        (x, y + 8),
        12
    )

    pygame.draw.circle(
        screen,
        theme["monster_body"],
        (x - 10, y + 20),
        6
    )

    pygame.draw.circle(
        screen,
        theme["monster_body"],
        (x + 10, y + 20),
        6
    )

    pupil_x = int(aim.x * 2)
    pupil_y = int(aim.y * 2)

    pygame.draw.circle(screen, WHITE, (x - 8, y - 5), 6)
    pygame.draw.circle(screen, WHITE, (x + 8, y - 5), 6)

    pygame.draw.circle(
        screen,
        BLACK,
        (x - 8 + pupil_x, y - 5 + pupil_y),
        2
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x + 8 + pupil_x, y - 5 + pupil_y),
        2
    )

    pygame.draw.arc(
        screen,
        BLACK,
        (x - 10, y + 1, 20, 12),
        0,
        math.pi,
        2
    )

    muzzle = player + aim * 34

    draw_glow_circle(
        screen,
        ORANGE,
        (int(muzzle.x), int(muzzle.y)),
        5
    )

# =====================================================
# FIRE
# =====================================================

def shoot():
    global last_shot

    now = pygame.time.get_ticks()

    if now - last_shot < shoot_delay:
        return

    mouse = pygame.Vector2(pygame.mouse.get_pos())
    direction = mouse - player

    if direction.length() == 0:
        return

    direction = direction.normalize()

    if multishot == 1:
        angles = [0]

    elif multishot == 2:
        angles = [-6, 6]

    else:
        angles = [-10, 0, 10]

    for angle in angles:

        shot_dir = direction.rotate(angle)
        start = player + shot_dir * 35

        fireballs.append({
            "position": start.copy(),
            "velocity": shot_dir * fireball_speed,
            "life": 1.25,
            "damage": fireball_damage
        })

    last_shot = now


def update_fireballs(dt):

    for fireball in fireballs[:]:

        fireball["position"] += fireball["velocity"] * dt
        fireball["life"] -= dt

        x = fireball["position"].x
        y = fireball["position"].y

        if (
            x < -60
            or x > WIDTH + 60
            or y < -60
            or y > HEIGHT + 60
            or fireball["life"] <= 0
        ):
            fireballs.remove(fireball)


def draw_fireballs():

    for fireball in fireballs:

        x = int(fireball["position"].x)
        y = int(fireball["position"].y)

        vel = fireball["velocity"]

        if vel.length() > 0:

            tail_dir = -vel.normalize()
            tail = pygame.Vector2(x, y) + tail_dir * 16

            pygame.draw.line(
                screen,
                ORANGE,
                (x, y),
                (int(tail.x), int(tail.y)),
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
# ENEMIES
# =====================================================

def spawn_position():

    side = random.choice(
        ["TOP", "BOTTOM", "LEFT", "RIGHT"]
    )

    if side == "TOP":
        return pygame.Vector2(
            random.randint(0, WIDTH),
            -70
        )

    if side == "BOTTOM":
        return pygame.Vector2(
            random.randint(0, WIDTH),
            HEIGHT + 70
        )

    if side == "LEFT":
        return pygame.Vector2(
            -70,
            random.randint(0, HEIGHT)
        )

    return pygame.Vector2(
        WIDTH + 70,
        random.randint(0, HEIGHT)
    )


def create_enemy(kind=None):

    if kind is None:

        roll = random.random()

        if wave < 3:

            kind = "BLOB" if roll < 0.78 else "BAT"

        elif wave < 5:

            kind = (
                "BLOB"
                if roll < 0.52
                else "BAT"
                if roll < 0.82
                else "TANK"
            )

        else:

            kind = (
                "BLOB"
                if roll < 0.40
                else "BAT"
                if roll < 0.72
                else "TANK"
            )

    data = ENEMY_TYPES[kind]
    pos = spawn_position()

    health_scale = (
        1.0
        if kind == "BOSS"
        else 1 + (wave - 1) * 0.10
    )

    enemy_health = max(
        1,
        int(data["health"] * health_scale)
    )

    enemies.append({
        "type": kind,
        "position": pos,
        "radius": data["radius"],
        "speed": data["speed"] + (wave - 1) * 2,
        "health": enemy_health,
        "max_health": enemy_health,
        "damage": data["damage"],
        "score": data["score"],
        "xp": data["xp"],
        "body": data["body"],
        "belly": data["belly"]
    })


def draw_enemy(enemy):

    x = int(enemy["position"].x)
    y = int(enemy["position"].y)
    r = enemy["radius"]

    draw_glow_circle(
        screen,
        enemy["body"],
        (x, y),
        r
    )

    pygame.draw.circle(
        screen,
        enemy["body"],
        (x, y),
        r
    )

    pygame.draw.circle(
        screen,
        enemy["belly"],
        (x, y + r // 4),
        max(8, r // 2)
    )

    if enemy["type"] == "BOSS":

        pygame.draw.polygon(
            screen,
            enemy["body"],
            [
                (x - 30, y - 28),
                (x - 45, y - 60),
                (x - 10, y - 40)
            ]
        )

        pygame.draw.polygon(
            screen,
            enemy["body"],
            [
                (x + 30, y - 28),
                (x + 45, y - 60),
                (x + 10, y - 40)
            ]
        )

    eye_spacing = max(6, r // 3)

    eye_radius = (
        6 if enemy["type"] == "BOSS"
        else 4
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (x - eye_spacing, y - 5),
        eye_radius
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (x + eye_spacing, y - 5),
        eye_radius
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x - eye_spacing, y - 5),
        max(2, eye_radius // 2)
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x + eye_spacing, y - 5),
        max(2, eye_radius // 2)
    )

    if enemy["type"] in ("TANK", "BOSS"):

        bar_w = r * 2
        pct = max(0, enemy["health"]) / enemy["max_health"]

        pygame.draw.rect(
            screen,
            BLACK,
            (x - r, y - r - 14, bar_w, 6)
        )

        pygame.draw.rect(
            screen,
            RED,
            (
                x - r,
                y - r - 14,
                int(bar_w * pct),
                6
            )
        )


def update_enemies(dt):

    global health
    global score

    for enemy in enemies[:]:

        direction = player - enemy["position"]

        if direction.length() > 0:

            direction = direction.normalize()

            enemy["position"] += (
                direction
                * enemy["speed"]
                * dt
            )

        if (
            enemy["position"].distance_to(player)
            < enemy["radius"] + player_radius
        ):

            health -= enemy["damage"]

            if enemy["type"] == "BOSS":

                enemy["position"] -= direction * 100

            else:

                if enemy in enemies:
                    enemies.remove(enemy)

            continue

        for fireball in fireballs[:]:

            if (
                enemy["position"].distance_to(
                    fireball["position"]
                )
                < enemy["radius"] + fireball_radius
            ):

                enemy["health"] -= fireball["damage"]

                if fireball in fireballs:
                    fireballs.remove(fireball)

                if enemy["health"] <= 0:

                    if enemy in enemies:
                        enemies.remove(enemy)

                    score += enemy["score"]

                    drop_xp(
                        enemy["position"],
                        enemy["xp"]
                    )

                break


def draw_enemies():

    for enemy in enemies:
        draw_enemy(enemy)

# =====================================================
# XP SYSTEM
# =====================================================

def drop_xp(position, amount):

    pieces = 1

    if amount >= 20:
        pieces = 2

    if amount >= 60:
        pieces = 5

    base_value = max(
        1,
        amount // pieces
    )

    for _ in range(pieces):

        offset = pygame.Vector2(
            random.randint(-16, 16),
            random.randint(-16, 16)
        )

        xp_gems.append({
            "position": position.copy() + offset,
            "value": base_value
        })


def update_xp_gems(dt):

    global xp
    global level
    global xp_needed
    global game_state
    global upgrade_options

    for gem in xp_gems[:]:

        distance = gem["position"].distance_to(player)

        if distance < 150 and distance > 0:

            direction = (
                player - gem["position"]
            ).normalize()

            gem["position"] += (
                direction * 330 * dt
            )

        if distance < player_radius + 12:

            xp += gem["value"]
            xp_gems.remove(gem)

    if xp >= xp_needed and game_state == "GAME":

        xp -= xp_needed

        level += 1

        xp_needed = int(
            xp_needed * 1.32
        )

        upgrade_options = random.sample(
            UPGRADES,
            3
        )

        game_state = "LEVELUP"


def draw_xp_gems():

    for gem in xp_gems:

        x = int(gem["position"].x)
        y = int(gem["position"].y)

        points = [
            (x, y - 8),
            (x + 7, y),
            (x, y + 8),
            (x - 7, y)
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

    x = WIDTH // 2 - bar_w // 2
    y = 20

    pygame.draw.rect(
        screen,
        theme["panel"],
        (x, y, bar_w, bar_h),
        border_radius=8
    )

    pct = min(
        1,
        xp / xp_needed
    )

    pygame.draw.rect(
        screen,
        theme["accent"],
        (
            x,
            y,
            int(bar_w * pct),
            bar_h
        ),
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (x, y, bar_w, bar_h),
        2,
        border_radius=8
    )

    txt = tiny_font.render(
        f"LEVEL {level}   XP {xp}/{xp_needed}",
        True,
        WHITE
    )

    screen.blit(
        txt,
        txt.get_rect(
            center=(WIDTH // 2, y + 30)
        )
    )

# =====================================================
# LEVEL UP
# =====================================================

def draw_level_up():

    global upgrade_card_rects

    theme = get_theme()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 185)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    heading = title_font.render(
        f"LEVEL {level}!",
        True,
        theme["accent"]
    )

    screen.blit(
        heading,
        heading.get_rect(
            center=(WIDTH // 2, 130)
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
            center=(WIDTH // 2, 205)
        )
    )

    upgrade_card_rects = []

    start_x = WIDTH // 2 - 480

    for i, (name, desc) in enumerate(upgrade_options):

        card = pygame.Rect(
            start_x + i * 330,
            285,
            300,
            220
        )

        upgrade_card_rects.append(card)

        mouse = pygame.mouse.get_pos()

        fill = (
            theme["accent_2"]
            if card.collidepoint(mouse)
            else theme["panel"]
        )

        pygame.draw.rect(
            screen,
            fill,
            card,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            theme["accent"],
            card,
            3,
            border_radius=20
        )

        num = button_font.render(
            str(i + 1),
            True,
            theme["accent"]
        )

        screen.blit(
            num,
            num.get_rect(
                center=(card.centerx, card.y + 42)
            )
        )

        name_text = small_font.render(
            name,
            True,
            WHITE
        )

        screen.blit(
            name_text,
            name_text.get_rect(
                center=(card.centerx, card.y + 100)
            )
        )

        desc_text = tiny_font.render(
            desc,
            True,
            WHITE
        )

        screen.blit(
            desc_text,
            desc_text.get_rect(
                center=(card.centerx, card.y + 145)
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
            center=(WIDTH // 2, 570)
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

    if index < 0 or index >= len(upgrade_options):
        return

    name = upgrade_options[index][0]

    if name == "RAPID FIRE":

        shoot_delay = max(
            65,
            int(shoot_delay * 0.82)
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

    theme = get_theme()

    bar_w = 290
    bar_h = 22

    x = 25
    y = 25

    pygame.draw.rect(
        screen,
        theme["panel"],
        (x, y, bar_w, bar_h),
        border_radius=10
    )

    hp_w = int(
        bar_w
        * max(0, health)
        / max_health
    )

    pygame.draw.rect(
        screen,
        RED,
        (x, y, hp_w, bar_h),
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (x, y, bar_w, bar_h),
        2,
        border_radius=10
    )

    text = tiny_font.render(
        f"HP {max(0, health)} / {max_health}",
        True,
        WHITE
    )

    screen.blit(
        text,
        (x, y + 30)
    )


def draw_boss_bar():

    bosses = [
        e for e in enemies
        if e["type"] == "BOSS"
    ]

    if not bosses:
        return

    boss = bosses[0]
    theme = get_theme()

    bar_w = 500
    bar_h = 20

    x = WIDTH // 2 - bar_w // 2
    y = 72

    pygame.draw.rect(
        screen,
        theme["panel"],
        (x, y, bar_w, bar_h),
        border_radius=8
    )

    pct = (
        max(0, boss["health"])
        / boss["max_health"]
    )

    pygame.draw.rect(
        screen,
        ORANGE,
        (
            x,
            y,
            int(bar_w * pct),
            bar_h
        ),
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (x, y, bar_w, bar_h),
        2,
        border_radius=8
    )

    boss_text = tiny_font.render(
        "BOSS",
        True,
        WHITE
    )

    screen.blit(
        boss_text,
        boss_text.get_rect(
            center=(WIDTH // 2, y - 13)
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
        theme["accent"]
    )

    screen.blit(
        score_text,
        (
            WIDTH - score_text.get_width() - 25,
            22
        )
    )

    wave_text = small_font.render(
        f"WAVE {wave}",
        True,
        WHITE
    )

    screen.blit(
        wave_text,
        (
            WIDTH - wave_text.get_width() - 25,
            58
        )
    )

    info = tiny_font.render(
        "WASD MOVE • HOLD LEFT CLICK FIRE • COLLECT XP • ESC MENU",
        True,
        WHITE
    )

    screen.blit(
        info,
        info.get_rect(
            center=(WIDTH // 2, HEIGHT - 25)
        )
    )


def draw_game_over():

    theme = get_theme()

    over = title_font.render(
        "GAME OVER",
        True,
        RED
    )

    screen.blit(
        over,
        over.get_rect(
            center=(WIDTH // 2, 200)
        )
    )

    score_text = button_font.render(
        f"FINAL SCORE: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        score_text.get_rect(
            center=(WIDTH // 2, 305)
        )
    )

    level_text = small_font.render(
        f"LEVEL {level}  •  WAVE {wave}",
        True,
        theme["accent"]
    )

    screen.blit(
        level_text,
        level_text.get_rect(
            center=(WIDTH // 2, 360)
        )
    )

    retry = small_font.render(
        "Press ENTER to restart",
        True,
        WHITE
    )

    screen.blit(
        retry,
        retry.get_rect(
            center=(WIDTH // 2, 430)
        )
    )

# =====================================================
# RESET
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

    last_enemy_spawn = pygame.time.get_ticks()

# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:

    dt = clock.tick(FPS) / 1000
    now = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state in (
                    "GAME",
                    "GAMEOVER"
                ):
                    game_state = "MENU"

            if game_state == "MENU":

                if event.key == pygame.K_1:
                    selected_theme_index = 0

                elif event.key == pygame.K_2:
                    selected_theme_index = 1

                elif event.key == pygame.K_3:
                    selected_theme_index = 2

                elif event.key == pygame.K_RETURN:

                    reset_game()
                    game_state = "GAME"

            elif game_state == "GAMEOVER":

                if event.key == pygame.K_RETURN:

                    reset_game()
                    game_state = "GAME"

            elif game_state == "LEVELUP":

                if event.key == pygame.K_1:
                    apply_upgrade(0)

                elif event.key == pygame.K_2:
                    apply_upgrade(1)

                elif event.key == pygame.K_3:
                    apply_upgrade(2)

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            if game_state == "MENU":

                if play_button.collidepoint(
                    event.pos
                ):

                    reset_game()
                    game_state = "GAME"

                else:

                    for i, card in enumerate(
                        theme_card_rects
                    ):

                        if card.collidepoint(
                            event.pos
                        ):

                            selected_theme_index = i

            elif game_state == "LEVELUP":

                for i, card in enumerate(
                    upgrade_card_rects
                ):

                    if card.collidepoint(
                        event.pos
                    ):

                        apply_upgrade(i)
                        break

    if game_state == "GAME":

        keys = pygame.key.get_pressed()

        movement = pygame.Vector2(
            0,
            0
        )

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            movement.y -= 1

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            movement.y += 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1

        if movement.length() > 0:

            movement = movement.normalize()

            player += (
                movement
                * player_speed
                * dt
            )

        player.x = max(
            player_radius,
            min(
                WIDTH - player_radius,
                player.x
            )
        )

        player.y = max(
            player_radius,
            min(
                HEIGHT - player_radius,
                player.y
            )
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
            and wave not in boss_waves_spawned
        ):

            create_enemy("BOSS")

            boss_waves_spawned.add(
                wave
            )

        # Normal enemies

        spawn_delay = max(
            250,
            base_enemy_spawn_delay
            - (wave - 1) * 55
            - min(score, 3000) // 20
        )

        if (
            now - last_enemy_spawn
            >= spawn_delay
        ):

            create_enemy()

            last_enemy_spawn = now

        update_fireballs(dt)
        update_enemies(dt)
        update_xp_gems(dt)

        if health <= 0:
            game_state = "GAMEOVER"

    # ---------------- DRAW ----------------

    draw_background(dt)

    if game_state == "MENU":

        play_button = draw_menu()

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
