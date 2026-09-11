import math
import pygame


LEVELS = {
    1: {
        "name": "NEON ESCAPE",
        "tagline": "Learn the route. Reach extraction.",
        "enemy_speed": 1.00,
        "enemy_health": 1.00,
        "enemy_damage": 1.00,
        "spawn_rate": 1.00,
        "zone_speed": 1.00,
        "zone_grace": 12.0,
        "zone_damage": 11.0,
        "camp_bonus": 0,
        "extra_obstacles": 0,
        "auto_run": 120.0,
        "start_armor": 25,
        "effect": "NONE",
        "final_boss": False,
    },
    2: {
        "name": "BARRICADE RUSH",
        "tagline": "The streets close in.",
        "enemy_speed": 1.05,
        "enemy_health": 1.00,
        "enemy_damage": 1.00,
        "spawn_rate": 1.10,
        "zone_speed": 1.05,
        "zone_grace": 11.0,
        "zone_damage": 11.5,
        "camp_bonus": 1,
        "extra_obstacles": 4,
        "auto_run": 125.0,
        "start_armor": 30,
        "effect": "DUST",
        "final_boss": False,
    },
    3: {
        "name": "TOXIC PURSUIT",
        "tagline": "Visibility drops. The zone accelerates.",
        "enemy_speed": 1.08,
        "enemy_health": 1.08,
        "enemy_damage": 1.05,
        "spawn_rate": 1.15,
        "zone_speed": 1.15,
        "zone_grace": 10.0,
        "zone_damage": 13.0,
        "camp_bonus": 1,
        "extra_obstacles": 6,
        "auto_run": 125.0,
        "start_armor": 35,
        "effect": "TOXIC",
        "final_boss": False,
    },
    4: {
        "name": "BLACKOUT CITY",
        "tagline": "Run through darkness.",
        "enemy_speed": 1.12,
        "enemy_health": 1.10,
        "enemy_damage": 1.10,
        "spawn_rate": 1.20,
        "zone_speed": 1.15,
        "zone_grace": 10.0,
        "zone_damage": 13.0,
        "camp_bonus": 2,
        "extra_obstacles": 8,
        "auto_run": 128.0,
        "start_armor": 35,
        "effect": "BLACKOUT",
        "final_boss": False,
    },
    5: {
        "name": "HORDE HIGHWAY",
        "tagline": "There are too many of them.",
        "enemy_speed": 1.15,
        "enemy_health": 1.15,
        "enemy_damage": 1.10,
        "spawn_rate": 1.40,
        "zone_speed": 1.20,
        "zone_grace": 9.0,
        "zone_damage": 14.0,
        "camp_bonus": 2,
        "extra_obstacles": 10,
        "auto_run": 130.0,
        "start_armor": 40,
        "effect": "DUST",
        "final_boss": False,
    },
    6: {
        "name": "RED ALERT",
        "tagline": "The city is now a kill zone.",
        "enemy_speed": 1.18,
        "enemy_health": 1.20,
        "enemy_damage": 1.15,
        "spawn_rate": 1.42,
        "zone_speed": 1.30,
        "zone_grace": 8.0,
        "zone_damage": 15.0,
        "camp_bonus": 2,
        "extra_obstacles": 12,
        "auto_run": 132.0,
        "start_armor": 40,
        "effect": "RED",
        "final_boss": False,
    },
    7: {
        "name": "ARMORED DISTRICT",
        "tagline": "Heavy enemies control the road.",
        "enemy_speed": 1.18,
        "enemy_health": 1.40,
        "enemy_damage": 1.20,
        "spawn_rate": 1.38,
        "zone_speed": 1.35,
        "zone_grace": 8.0,
        "zone_damage": 15.5,
        "camp_bonus": 3,
        "extra_obstacles": 14,
        "auto_run": 134.0,
        "start_armor": 45,
        "effect": "DUST",
        "final_boss": False,
    },
    8: {
        "name": "NIGHT SIEGE",
        "tagline": "Darkness, ambushes and a faster zone.",
        "enemy_speed": 1.22,
        "enemy_health": 1.35,
        "enemy_damage": 1.20,
        "spawn_rate": 1.55,
        "zone_speed": 1.45,
        "zone_grace": 7.0,
        "zone_damage": 16.0,
        "camp_bonus": 3,
        "extra_obstacles": 16,
        "auto_run": 136.0,
        "start_armor": 45,
        "effect": "BLACKOUT",
        "final_boss": False,
    },
    9: {
        "name": "LAST CITY",
        "tagline": "Everything is collapsing.",
        "enemy_speed": 1.28,
        "enemy_health": 1.50,
        "enemy_damage": 1.25,
        "spawn_rate": 1.65,
        "zone_speed": 1.55,
        "zone_grace": 6.0,
        "zone_damage": 18.0,
        "camp_bonus": 4,
        "extra_obstacles": 18,
        "auto_run": 138.0,
        "start_armor": 50,
        "effect": "STORM",
        "final_boss": False,
    },
    10: {
        "name": "FINAL EXTRACTION",
        "tagline": "Five kilometres. One last boss. Get out.",
        "enemy_speed": 1.35,
        "enemy_health": 1.70,
        "enemy_damage": 1.35,
        "spawn_rate": 1.75,
        "zone_speed": 1.70,
        "zone_grace": 5.0,
        "zone_damage": 20.0,
        "camp_bonus": 4,
        "extra_obstacles": 20,
        "auto_run": 142.0,
        "start_armor": 50,
        "effect": "FINAL",
        "final_boss": True,
    },
}


class CampaignLevels:
    def get(self, level):
        level = max(1, min(10, int(level)))
        return LEVELS[level]

    def name(self, level):
        return self.get(level)["name"]

    def tagline(self, level):
        return self.get(level)["tagline"]

    def requires_final_boss(self, level):
        return bool(self.get(level)["final_boss"])

    def draw_effect(self, surface, level, player_screen, time_s):
        config = self.get(level)
        effect = config["effect"]

        if effect == "NONE":
            return

        width, height = surface.get_size()

        if effect == "DUST":
            haze = pygame.Surface((width, height), pygame.SRCALPHA)
            haze.fill((150, 110, 70, 20))
            surface.blit(haze, (0, 0))

            for i in range(22):
                x = int((i * 173 + time_s * (25 + i % 5)) % width)
                y = int((i * 97 + time_s * (10 + i % 4)) % height)
                pygame.draw.circle(surface, (135, 115, 90), (x, y), 2)

        elif effect == "TOXIC":
            haze = pygame.Surface((width, height), pygame.SRCALPHA)
            haze.fill((75, 175, 80, 34))
            surface.blit(haze, (0, 0))

            for i in range(16):
                x = int((i * 211 + time_s * 18) % width)
                y = int((i * 89 + math.sin(time_s + i) * 40) % height)
                pygame.draw.circle(surface, (120, 255, 120), (x, y), 3, 1)

        elif effect == "BLACKOUT":
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))

            px = int(player_screen.x)
            py = int(player_screen.y)

            pygame.draw.circle(
                overlay,
                (0, 0, 0, 65),
                (px, py),
                220,
            )
            pygame.draw.circle(
                overlay,
                (0, 0, 0, 20),
                (px, py),
                135,
            )
            surface.blit(overlay, (0, 0))

        elif effect == "RED":
            pulse = int(28 + 20 * (0.5 + 0.5 * math.sin(time_s * 4)))
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((180, 25, 35, pulse))
            pygame.draw.rect(
                overlay,
                (255, 55, 65, min(130, pulse * 2)),
                overlay.get_rect(),
                22,
            )
            surface.blit(overlay, (0, 0))

        elif effect == "STORM":
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((45, 65, 120, 38))
            surface.blit(overlay, (0, 0))

            for i in range(30):
                x = int((i * 113 + time_s * 240) % (width + 80)) - 40
                y = int((i * 71 + time_s * 360) % (height + 100)) - 50
                pygame.draw.line(
                    surface,
                    (145, 175, 230),
                    (x, y),
                    (x - 10, y + 24),
                    2,
                )

        elif effect == "FINAL":
            pulse = int(35 + 25 * (0.5 + 0.5 * math.sin(time_s * 3)))
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((75, 0, 20, pulse))
            surface.blit(overlay, (0, 0))

            pygame.draw.rect(
                surface,
                (210, 45, 70),
                pygame.Rect(5, 5, width - 10, height - 10),
                4,
            )
