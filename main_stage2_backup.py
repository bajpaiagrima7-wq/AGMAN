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
# COLOURS
# =====================================================

BACKGROUND = (7, 8, 20)
WHITE = (245, 245, 255)

CYAN = (0, 240, 255)
PURPLE = (170, 70, 255)
PINK = (255, 40, 150)
RED = (255, 60, 80)
GREEN = (50, 255, 150)
YELLOW = (255, 220, 70)

DARK = (20, 22, 40)
GRID = (20, 25, 45)

# =====================================================
# FONTS
# =====================================================

title_font = pygame.font.Font(None, 110)
button_font = pygame.font.Font(None, 48)
hud_font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 26)

# =====================================================
# BACKGROUND STARS
# =====================================================

stars = []

for i in range(120):

    stars.append(
        [
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            random.randint(1, 3),
            random.uniform(10, 40)
        ]
    )

# =====================================================
# PLAYER
# =====================================================

player = pygame.Vector2(
    WIDTH // 2,
    HEIGHT // 2
)

player_radius = 22
player_speed = 330

max_health = 100
health = max_health

# =====================================================
# BULLETS
# =====================================================

bullets = []

bullet_speed = 750
bullet_radius = 5

shoot_delay = 180
last_shot = 0

# =====================================================
# ENEMIES
# =====================================================

enemies = []

enemy_spawn_delay = 900
last_enemy_spawn = 0

score = 0

# =====================================================
# GAME STATE
# =====================================================

game_state = "MENU"

# =====================================================
# FUNCTIONS
# =====================================================


def draw_glow_circle(surface, colour, position, radius):

    glow_size = radius * 7

    glow = pygame.Surface(
        (glow_size, glow_size),
        pygame.SRCALPHA
    )

    center = glow_size // 2

    pygame.draw.circle(
        glow,
        (*colour, 20),
        (center, center),
        radius * 3
    )

    pygame.draw.circle(
        glow,
        (*colour, 45),
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
            position[0] - center,
            position[1] - center
        )
    )


def draw_background(dt):

    screen.fill(BACKGROUND)

    # Moving stars

    for star in stars:

        star[1] += star[3] * dt

        if star[1] > HEIGHT:

            star[1] = 0
            star[0] = random.randint(0, WIDTH)

        pygame.draw.circle(
            screen,
            (90, 100, 165),
            (int(star[0]), int(star[1])),
            star[2]
        )


def draw_grid():

    grid_size = 50

    for x in range(0, WIDTH, grid_size):

        pygame.draw.line(
            screen,
            GRID,
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(0, HEIGHT, grid_size):

        pygame.draw.line(
            screen,
            GRID,
            (0, y),
            (WIDTH, y)
        )


def create_enemy():

    side = random.choice(
        ["TOP", "BOTTOM", "LEFT", "RIGHT"]
    )

    if side == "TOP":

        x = random.randint(0, WIDTH)
        y = -40

    elif side == "BOTTOM":

        x = random.randint(0, WIDTH)
        y = HEIGHT + 40

    elif side == "LEFT":

        x = -40
        y = random.randint(0, HEIGHT)

    else:

        x = WIDTH + 40
        y = random.randint(0, HEIGHT)

    enemy = {

        "position": pygame.Vector2(x, y),

        "radius": random.randint(16, 24),

        "speed": random.randint(90, 150),

        "health": 1
    }

    enemies.append(enemy)


def shoot():

    global last_shot

    current_time = pygame.time.get_ticks()

    if current_time - last_shot < shoot_delay:
        return

    mouse_position = pygame.Vector2(
        pygame.mouse.get_pos()
    )

    direction = mouse_position - player

    if direction.length() == 0:
        return

    direction = direction.normalize()

    bullets.append(
        {
            "position": player.copy(),
            "velocity": direction * bullet_speed
        }
    )

    last_shot = current_time


def update_bullets(dt):

    for bullet in bullets[:]:

        bullet["position"] += (
            bullet["velocity"] * dt
        )

        x = bullet["position"].x
        y = bullet["position"].y

        if (
            x < -50
            or x > WIDTH + 50
            or y < -50
            or y > HEIGHT + 50
        ):

            bullets.remove(bullet)


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

        distance = enemy["position"].distance_to(
            player
        )

        # Enemy touches player

        if distance < enemy["radius"] + player_radius:

            health -= 10

            enemies.remove(enemy)

            continue

        # Bullet collision

        for bullet in bullets[:]:

            bullet_distance = (
                enemy["position"].distance_to(
                    bullet["position"]
                )
            )

            if (
                bullet_distance
                < enemy["radius"] + bullet_radius
            ):

                enemy["health"] -= 1

                if bullet in bullets:
                    bullets.remove(bullet)

                if enemy["health"] <= 0:

                    if enemy in enemies:

                        enemies.remove(enemy)

                    score += 10

                break


def draw_player():

    draw_glow_circle(
        screen,
        CYAN,
        (
            int(player.x),
            int(player.y)
        ),
        player_radius
    )

    # Gun / aiming direction

    mouse = pygame.Vector2(
        pygame.mouse.get_pos()
    )

    direction = mouse - player

    if direction.length() > 0:

        direction = direction.normalize()

        gun_end = (
            player
            + direction * 38
        )

        pygame.draw.line(
            screen,
            WHITE,
            player,
            gun_end,
            6
        )


def draw_bullets():

    for bullet in bullets:

        draw_glow_circle(
            screen,
            YELLOW,
            (
                int(bullet["position"].x),
                int(bullet["position"].y)
            ),
            bullet_radius
        )


def draw_enemies():

    for enemy in enemies:

        draw_glow_circle(
            screen,
            PINK,
            (
                int(enemy["position"].x),
                int(enemy["position"].y)
            ),
            enemy["radius"]
        )


def draw_health_bar():

    bar_width = 300
    bar_height = 24

    x = 30
    y = 30

    pygame.draw.rect(
        screen,
        DARK,
        (
            x,
            y,
            bar_width,
            bar_height
        ),
        border_radius=10
    )

    health_width = int(
        bar_width
        * max(health, 0)
        / max_health
    )

    pygame.draw.rect(
        screen,
        RED,
        (
            x,
            y,
            health_width,
            bar_height
        ),
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (
            x,
            y,
            bar_width,
            bar_height
        ),
        2,
        border_radius=10
    )

    health_text = small_font.render(
        f"HP {max(health, 0)} / {max_health}",
        True,
        WHITE
    )

    screen.blit(
        health_text,
        (
            x,
            y + 32
        )
    )


def draw_hud():

    draw_health_bar()

    score_text = hud_font.render(
        f"SCORE: {score}",
        True,
        CYAN
    )

    screen.blit(
        score_text,
        (
            WIDTH - score_text.get_width() - 30,
            30
        )
    )

    info = small_font.render(
        "WASD MOVE   •   LEFT CLICK SHOOT   •   ESC MENU",
        True,
        WHITE
    )

    screen.blit(
        info,
        (
            WIDTH // 2
            - info.get_width() // 2,
            HEIGHT - 40
        )
    )


def draw_menu():

    title_shadow = title_font.render(
        "NEON SURVIVOR",
        True,
        PURPLE
    )

    title = title_font.render(
        "NEON SURVIVOR",
        True,
        CYAN
    )

    screen.blit(
        title_shadow,
        title_shadow.get_rect(
            center=(
                WIDTH // 2 + 5,
                190 + 5
            )
        )
    )

    screen.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                190
            )
        )
    )

    subtitle = small_font.render(
        "SURVIVE  •  EVOLVE  •  DOMINATE",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(
            center=(
                WIDTH // 2,
                270
            )
        )
    )

    play_button = pygame.Rect(
        WIDTH // 2 - 160,
        360,
        320,
        80
    )

    mouse = pygame.mouse.get_pos()

    button_colour = DARK

    if play_button.collidepoint(mouse):
        button_colour = PURPLE

    pygame.draw.rect(
        screen,
        button_colour,
        play_button,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        CYAN,
        play_button,
        3,
        border_radius=18
    )

    play_text = button_font.render(
        "PLAY",
        True,
        WHITE
    )

    screen.blit(
        play_text,
        play_text.get_rect(
            center=play_button.center
        )
    )

    instruction = small_font.render(
        "Move • Aim • Shoot • Survive",
        True,
        (160, 160, 190)
    )

    screen.blit(
        instruction,
        instruction.get_rect(
            center=(
                WIDTH // 2,
                510
            )
        )
    )

    return play_button


def draw_game_over():

    title = title_font.render(
        "GAME OVER",
        True,
        RED
    )

    screen.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                240
            )
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
            center=(
                WIDTH // 2,
                350
            )
        )
    )

    restart = small_font.render(
        "Press ENTER to play again",
        True,
        CYAN
    )

    screen.blit(
        restart,
        restart.get_rect(
            center=(
                WIDTH // 2,
                430
            )
        )
    )


def reset_game():

    global player
    global health
    global score
    global bullets
    global enemies
    global last_enemy_spawn

    player = pygame.Vector2(
        WIDTH // 2,
        HEIGHT // 2
    )

    health = max_health

    score = 0

    bullets = []

    enemies = []

    last_enemy_spawn = pygame.time.get_ticks()


# =====================================================
# MAIN LOOP
# =====================================================

running = True

play_button = pygame.Rect(0, 0, 0, 0)

while running:

    dt = clock.tick(FPS) / 1000

    current_time = pygame.time.get_ticks()

    # =================================================
    # EVENTS
    # =================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state == "GAME":

                    game_state = "MENU"

            if event.key == pygame.K_RETURN:

                if game_state in (
                    "MENU",
                    "GAMEOVER"
                ):

                    reset_game()

                    game_state = "GAME"

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if game_state == "MENU":

                    if play_button.collidepoint(
                        event.pos
                    ):

                        reset_game()

                        game_state = "GAME"

                elif game_state == "GAME":

                    shoot()

    # =================================================
    # UPDATE GAME
    # =================================================

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

        # Hold mouse button to continuously shoot

        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0]:
            shoot()

        # Enemy spawning

        if (
            current_time - last_enemy_spawn
            >= enemy_spawn_delay
        ):

            create_enemy()

            last_enemy_spawn = current_time

        update_bullets(dt)

        update_enemies(dt)

        if health <= 0:

            game_state = "GAMEOVER"

    # =================================================
    # DRAW
    # =================================================

    draw_background(dt)

    if game_state == "MENU":

        play_button = draw_menu()

    elif game_state == "GAME":

        draw_grid()

        draw_bullets()

        draw_enemies()

        draw_player()

        draw_hud()

    elif game_state == "GAMEOVER":

        draw_game_over()

    pygame.display.flip()


pygame.quit()
