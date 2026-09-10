import pygame
import random
import math

pygame.init()

# =====================================================
# SETTINGS
# =====================================================

WIDTH = 1280
HEIGHT = 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Survivor")

clock = pygame.time.Clock()

# =====================================================
# FONTS
# =====================================================

title_font = pygame.font.Font(None, 110)
button_font = pygame.font.Font(None, 48)
hud_font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 28)
tiny_font = pygame.font.Font(None, 22)

# =====================================================
# COMMON COLOURS
# =====================================================

WHITE = (245, 245, 255)
BLACK = (15, 15, 22)
RED = (255, 70, 90)
YELLOW = (255, 215, 70)
ORANGE = (255, 135, 40)
DEEP_ORANGE = (255, 90, 20)

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
    return THEMES[theme_names[selected_theme_index]]


# =====================================================
# BACKGROUND STARS
# =====================================================

stars = []

for _ in range(120):
    stars.append(
        [
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            random.randint(1, 3),
            random.uniform(10, 40)
        ]
    )

# =====================================================
# PLAYER / MONSTER
# =====================================================

player = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_radius = 24
player_speed = 330

max_health = 100
health = max_health

# =====================================================
# FIREBALLS
# =====================================================

fireballs = []
fireball_speed = 780
fireball_radius = 7

shoot_delay = 140
last_shot = 0

# =====================================================
# ENEMIES
# =====================================================

enemies = []
last_enemy_spawn = 0
base_enemy_spawn_delay = 900

# =====================================================
# SCORE / STATE
# =====================================================

score = 0
game_state = "MENU"

play_button = pygame.Rect(0, 0, 0, 0)
theme_card_rects = []

# =====================================================
# ENEMY TYPES
# =====================================================

ENEMY_TYPES = {
    "BLOB": {
        "radius": 20,
        "speed": 95,
        "health": 1,
        "damage": 10,
        "score": 10,
        "body": (255, 75, 170),
        "belly": (255, 200, 225),
    },
    "BAT": {
        "radius": 16,
        "speed": 145,
        "health": 1,
        "damage": 10,
        "score": 15,
        "body": (170, 110, 255),
        "belly": (220, 205, 255),
    },
    "TANK": {
        "radius": 28,
        "speed": 70,
        "health": 3,
        "damage": 20,
        "score": 25,
        "body": (80, 255, 170),
        "belly": (205, 255, 235),
    }
}

# =====================================================
# DRAW HELPERS
# =====================================================

def draw_glow_circle(surface, colour, position, radius):
    glow_size = radius * 7
    glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

    center = glow_size // 2

    pygame.draw.circle(glow, (*colour, 22), (center, center), radius * 3)
    pygame.draw.circle(glow, (*colour, 55), (center, center), radius * 2)
    pygame.draw.circle(glow, colour, (center, center), radius)

    surface.blit(glow, (position[0] - center, position[1] - center))


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
    grid_size = 50

    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(screen, theme["grid"], (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(screen, theme["grid"], (0, y), (WIDTH, y))


# =====================================================
# MENU
# =====================================================

def draw_menu():
    global theme_card_rects

    theme = get_theme()
    theme_card_rects = []

    title_shadow = title_font.render("NEON SURVIVOR", True, theme["accent_2"])
    title = title_font.render("NEON SURVIVOR", True, theme["accent"])

    screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 5, 170 + 5)))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 170)))

    subtitle = small_font.render("Cute Monster Fire Edition", True, WHITE)
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 240)))

    info = tiny_font.render("Choose a neon theme below, then press PLAY", True, WHITE)
    screen.blit(info, info.get_rect(center=(WIDTH // 2, 285)))

    play_button = pygame.Rect(WIDTH // 2 - 150, 330, 300, 75)
    mouse = pygame.mouse.get_pos()

    fill = theme["panel"]
    if play_button.collidepoint(mouse):
        fill = theme["accent_2"]

    pygame.draw.rect(screen, fill, play_button, border_radius=18)
    pygame.draw.rect(screen, theme["accent"], play_button, 3, border_radius=18)

    play_text = button_font.render("PLAY", True, WHITE)
    screen.blit(play_text, play_text.get_rect(center=play_button.center))

    # Theme cards
    card_y = 460
    start_x = WIDTH // 2 - 360

    for i, name in enumerate(theme_names):
        x = start_x + i * 245
        card = pygame.Rect(x, card_y, 220, 100)
        theme_card_rects.append(card)

        card_theme = THEMES[name]
        border_colour = card_theme["accent"] if i == selected_theme_index else WHITE

        pygame.draw.rect(screen, card_theme["panel"], card, border_radius=16)
        pygame.draw.rect(screen, border_colour, card, 3, border_radius=16)

        # preview circles
        pygame.draw.circle(screen, card_theme["accent"], (x + 40, card_y + 35), 12)
        pygame.draw.circle(screen, card_theme["accent_2"], (x + 70, card_y + 35), 12)
        pygame.draw.circle(screen, card_theme["monster_body"], (x + 100, card_y + 35), 12)

        label = tiny_font.render(name, True, WHITE)
        screen.blit(label, (x + 18, card_y + 62))

    controls = tiny_font.render(
        "Press 1 / 2 / 3 to change theme • ENTER or click PLAY to start",
        True,
        WHITE
    )
    screen.blit(controls, controls.get_rect(center=(WIDTH // 2, HEIGHT - 45)))

    return play_button


# =====================================================
# ENEMIES
# =====================================================

def create_enemy():
    enemy_roll = random.random()

    if enemy_roll < 0.60:
        enemy_kind = "BLOB"
    elif enemy_roll < 0.88:
        enemy_kind = "BAT"
    else:
        enemy_kind = "TANK"

    data = ENEMY_TYPES[enemy_kind]

    side = random.choice(["TOP", "BOTTOM", "LEFT", "RIGHT"])

    if side == "TOP":
        x = random.randint(0, WIDTH)
        y = -50
    elif side == "BOTTOM":
        x = random.randint(0, WIDTH)
        y = HEIGHT + 50
    elif side == "LEFT":
        x = -50
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH + 50
        y = random.randint(0, HEIGHT)

    enemies.append({
        "type": enemy_kind,
        "position": pygame.Vector2(x, y),
        "radius": data["radius"],
        "speed": data["speed"],
        "health": data["health"],
        "damage": data["damage"],
        "score": data["score"],
        "body": data["body"],
        "belly": data["belly"],
    })


def update_enemies(dt):
    global health, score

    for enemy in enemies[:]:
        direction = player - enemy["position"]

        if direction.length() > 0:
            direction = direction.normalize()
            enemy["position"] += direction * enemy["speed"] * dt

        # touch player
        if enemy["position"].distance_to(player) < enemy["radius"] + 20:
            health -= enemy["damage"]
            enemies.remove(enemy)
            continue

        # fireball collision
        for fireball in fireballs[:]:
            if enemy["position"].distance_to(fireball["position"]) < enemy["radius"] + fireball_radius:
                enemy["health"] -= 1

                if fireball in fireballs:
                    fireballs.remove(fireball)

                if enemy["health"] <= 0:
                    if enemy in enemies:
                        enemies.remove(enemy)
                    score += enemy["score"]

                break


def draw_enemy(enemy):
    x = int(enemy["position"].x)
    y = int(enemy["position"].y)
    r = enemy["radius"]

    draw_glow_circle(screen, enemy["body"], (x, y), r)

    pygame.draw.circle(screen, enemy["body"], (x, y), r)
    pygame.draw.circle(screen, enemy["belly"], (x, y + 6), max(8, r // 2))

    # eyes
    eye_y = y - 4
    pygame.draw.circle(screen, WHITE, (x - r // 3, eye_y), 4)
    pygame.draw.circle(screen, WHITE, (x + r // 3, eye_y), 4)
    pygame.draw.circle(screen, BLACK, (x - r // 3, eye_y), 2)
    pygame.draw.circle(screen, BLACK, (x + r // 3, eye_y), 2)

    # mouth
    pygame.draw.arc(screen, BLACK, (x - 10, y + 2, 20, 12), 0, math.pi, 2)


def draw_enemies():
    for enemy in enemies:
        draw_enemy(enemy)


# =====================================================
# PLAYER / CUTE MONSTER
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

    # soft glow
    draw_glow_circle(screen, theme["accent"], (x, y), player_radius + 2)

    # ears / horns
    left_ear = [(x - 14, y - 10), (x - 24, y - 30), (x - 5, y - 18)]
    right_ear = [(x + 14, y - 10), (x + 24, y - 30), (x + 5, y - 18)]

    pygame.draw.polygon(screen, theme["monster_body"], left_ear)
    pygame.draw.polygon(screen, theme["monster_body"], right_ear)

    # body
    pygame.draw.circle(screen, theme["monster_body"], (x, y), player_radius)
    pygame.draw.circle(screen, theme["monster_belly"], (x, y + 8), 12)

    # little feet
    pygame.draw.circle(screen, theme["monster_body"], (x - 10, y + 20), 6)
    pygame.draw.circle(screen, theme["monster_body"], (x + 10, y + 20), 6)

    # eyes with pupils following mouse
    pupil_offset_x = int(aim.x * 2)
    pupil_offset_y = int(aim.y * 2)

    pygame.draw.circle(screen, WHITE, (x - 8, y - 5), 6)
    pygame.draw.circle(screen, WHITE, (x + 8, y - 5), 6)

    pygame.draw.circle(screen, BLACK, (x - 8 + pupil_offset_x, y - 5 + pupil_offset_y), 2)
    pygame.draw.circle(screen, BLACK, (x + 8 + pupil_offset_x, y - 5 + pupil_offset_y), 2)

    # smile
    pygame.draw.arc(screen, BLACK, (x - 10, y + 1, 20, 12), 0, math.pi, 2)

    # fire nozzle / aim line
    muzzle = player + aim * 34
    pygame.draw.line(screen, WHITE, (x, y), (int(muzzle.x), int(muzzle.y)), 4)

    # little flame at mouth / nozzle
    draw_glow_circle(screen, ORANGE, (int(muzzle.x), int(muzzle.y)), 5)


# =====================================================
# FIREBALLS
# =====================================================

def shoot():
    global last_shot

    current_time = pygame.time.get_ticks()

    if current_time - last_shot < shoot_delay:
        return

    mouse = pygame.Vector2(pygame.mouse.get_pos())
    direction = mouse - player

    if direction.length() == 0:
        return

    direction = direction.normalize()

    start_position = player + direction * 35

    fireballs.append({
        "position": start_position.copy(),
        "velocity": direction * fireball_speed,
        "life": 1.2
    })

    last_shot = current_time


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

        draw_glow_circle(screen, ORANGE, (x, y), fireball_radius + 2)
        pygame.draw.circle(screen, ORANGE, (x, y), fireball_radius + 2)
        pygame.draw.circle(screen, YELLOW, (x, y), fireball_radius)
        pygame.draw.circle(screen, WHITE, (x, y), 3)


# =====================================================
# HUD / GAME OVER
# =====================================================

def draw_health_bar():
    theme = get_theme()

    bar_width = 300
    bar_height = 24
    x = 30
    y = 25

    pygame.draw.rect(screen, theme["panel"], (x, y, bar_width, bar_height), border_radius=10)

    health_width = int(bar_width * max(health, 0) / max_health)
    pygame.draw.rect(screen, RED, (x, y, health_width, bar_height), border_radius=10)

    pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2, border_radius=10)

    hp_text = tiny_font.render(f"HP {max(health, 0)} / {max_health}", True, WHITE)
    screen.blit(hp_text, (x, y + 32))


def draw_hud():
    theme = get_theme()

    draw_health_bar()

    score_text = hud_font.render(f"SCORE: {score}", True, theme["accent"])
    screen.blit(score_text, (WIDTH - score_text.get_width() - 30, 25))

    theme_text = tiny_font.render(f"THEME: {theme_names[selected_theme_index]}", True, WHITE)
    screen.blit(theme_text, (WIDTH - theme_text.get_width() - 30, 62))

    info_text = tiny_font.render(
        "WASD / ARROWS MOVE   •   LEFT CLICK FIRE   •   ESC MENU",
        True,
        WHITE
    )
    screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT - 28)))


def draw_game_over():
    theme = get_theme()

    over_text = title_font.render("GAME OVER", True, RED)
    screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, 220)))

    score_text = button_font.render(f"FINAL SCORE: {score}", True, WHITE)
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 320)))

    retry_text = small_font.render("Press ENTER to play again", True, theme["accent"])
    screen.blit(retry_text, retry_text.get_rect(center=(WIDTH // 2, 400)))

    menu_text = tiny_font.render("Press ESC to return to menu", True, WHITE)
    screen.blit(menu_text, menu_text.get_rect(center=(WIDTH // 2, 445)))


# =====================================================
# RESET
# =====================================================

def reset_game():
    global player
    global health
    global score
    global fireballs
    global enemies
    global last_enemy_spawn
    global last_shot

    player = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    health = max_health
    score = 0
    fireballs = []
    enemies = []

    last_enemy_spawn = pygame.time.get_ticks()
    last_shot = 0


# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:
    dt = clock.tick(FPS) / 1000
    current_time = pygame.time.get_ticks()

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "GAME":
                    game_state = "MENU"
                elif game_state == "GAMEOVER":
                    game_state = "MENU"

            if game_state == "MENU":
                if event.key == pygame.K_1:
                    selected_theme_index = 0
                elif event.key == pygame.K_2:
                    selected_theme_index = 1
                elif event.key == pygame.K_3:
                    selected_theme_index = 2

            if event.key == pygame.K_RETURN:
                if game_state in ("MENU", "GAMEOVER"):
                    reset_game()
                    game_state = "GAME"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == "MENU":
                    if play_button.collidepoint(event.pos):
                        reset_game()
                        game_state = "GAME"
                    else:
                        for i, card in enumerate(theme_card_rects):
                            if card.collidepoint(event.pos):
                                selected_theme_index = i

                elif game_state == "GAME":
                    shoot()

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

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
            movement = movement.normalize()
            player += movement * player_speed * dt

        player.x = max(player_radius, min(WIDTH - player_radius, player.x))
        player.y = max(player_radius, min(HEIGHT - player_radius, player.y))

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            shoot()

        # harder over time
        spawn_delay = max(280, base_enemy_spawn_delay - (score * 2))

        if current_time - last_enemy_spawn >= spawn_delay:
            create_enemy()
            last_enemy_spawn = current_time

        update_fireballs(dt)
        update_enemies(dt)

        if health <= 0:
            game_state = "GAMEOVER"

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    draw_background(dt)

    if game_state == "MENU":
        play_button = draw_menu()

    elif game_state == "GAME":
        draw_grid()
        draw_fireballs()
        draw_enemies()
        draw_player()
        draw_hud()

    elif game_state == "GAMEOVER":
        draw_game_over()

    pygame.display.flip()

pygame.quit()
