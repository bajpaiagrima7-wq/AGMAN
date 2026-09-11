import pygame


class CollapsingZone:
    """
    A battle-royale-inspired danger zone that closes from behind.

    It does not copy a specific game's map/circle system. In AGMAN's linear
    5 km course it behaves like an advancing storm wall.
    """

    def __init__(self, city):
        self.city = city
        self.speed_multiplier = 1.0
        self.grace_period = 12.0
        self.damage_per_second = 11.0
        self.reset()

    def configure(self, speed_multiplier=1.0, grace_period=12.0, damage_per_second=11.0):
        self.speed_multiplier = float(speed_multiplier)
        self.grace_period = float(grace_period)
        self.damage_per_second = float(damage_per_second)

    def reset(self):
        self.boundary_x = self.city.spawn.x - 900
        self.elapsed = 0.0
        self.damage_buffer = 0.0
        self.warning_stage = 0

    def update(self, dt, player, progress):
        self.elapsed += dt

        # Grace period lets the player settle into the run.
        if self.elapsed < self.grace_period:
            return 0

        # The zone accelerates as the run advances.
        speed = (62 + progress * 92) * self.speed_multiplier
        self.boundary_x += speed * dt
        self.boundary_x = min(
            self.boundary_x,
            self.city.finish_x - 150,
        )

        if player.x < self.boundary_x + 70:
            self.damage_buffer += self.damage_per_second * dt

        damage = int(self.damage_buffer)

        if damage > 0:
            self.damage_buffer -= damage

        return damage

    def distance_behind(self, player):
        return max(0, player.x - self.boundary_x)

    def danger_level(self, player):
        distance = self.distance_behind(player)

        if player.x <= self.boundary_x + 70:
            return 3
        if distance < 350:
            return 2
        if distance < 800:
            return 1

        return 0

    def draw(self, surface, camera, player, theme):
        sx = int(self.boundary_x - camera.offset.x)
        level = self.danger_level(player)

        # Storm wall if visible.
        if -200 < sx < surface.get_width() + 100:
            width = max(0, sx)

            if width > 0:
                storm = pygame.Surface(
                    (width, surface.get_height()),
                    pygame.SRCALPHA,
                )
                storm.fill((125, 35, 190, 72))
                surface.blit(storm, (0, 0))

            pygame.draw.line(
                surface,
                (220, 90, 255),
                (sx, 0),
                (sx, surface.get_height()),
                7,
            )

            for y in range(20, surface.get_height(), 48):
                pygame.draw.line(
                    surface,
                    (255, 150, 255),
                    (sx - 9, y),
                    (sx + 9, y + 20),
                    3,
                )

        # Danger vignette when the zone is close.
        if level >= 1:
            alpha = 35 if level == 1 else 75 if level == 2 else 125
            vignette = pygame.Surface(
                surface.get_size(),
                pygame.SRCALPHA,
            )
            pygame.draw.rect(
                vignette,
                (170, 30, 210, alpha),
                vignette.get_rect(),
                20,
            )
            surface.blit(vignette, (0, 0))

    def hud_text(self, player):
        distance = self.distance_behind(player)

        if self.elapsed < self.grace_period:
            return f"ZONE OPENS IN {max(0, self.grace_period - self.elapsed):.0f}s"

        # Approximate display metres: four world pixels = one metre.
        metres = int(distance / 4)

        if self.danger_level(player) == 3:
            return "IN DANGER ZONE • MOVE!"

        return f"ZONE {metres}m BEHIND"
