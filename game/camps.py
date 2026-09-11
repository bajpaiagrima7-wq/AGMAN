import random
import pygame


class CampSystem:
    """Enemy ambush checkpoints placed across the 5 km course."""

    def __init__(self, city):
        self.city = city
        self.bonus_count = 0

        self.camps = [
            {"x": 2400, "label": "RAIDER CAMP", "count": 3},
            {"x": 5900, "label": "AMBUSH POINT", "count": 4},
            {"x": 9300, "label": "HOSTILE CHECKPOINT", "count": 4},
            {"x": 13200, "label": "RAIDER CAMP", "count": 5},
            {"x": 16900, "label": "FINAL AMBUSH", "count": 6},
        ]

        self.reset()

    def configure(self, bonus_count=0):
        self.bonus_count = max(0, int(bonus_count))

    def reset(self):
        self.triggered = set()

    def update(self, player):
        spawns = []
        message = None

        for index, camp in enumerate(self.camps):
            if index in self.triggered:
                continue

            if player.x < camp["x"] - 180:
                continue

            self.triggered.add(index)
            message = f"AMBUSH! {camp['label']}"

            for i in range(camp["count"] + self.bonus_count):
                if i % 4 == 0 and index >= 2:
                    kind = "TANK"
                elif i % 3 == 0:
                    kind = "BAT"
                else:
                    kind = "BLOB"

                x = camp["x"] + random.randint(-120, 280)
                lane_y = random.choice(
                    [430, 560, 720, 880, 1040, 1180]
                )

                candidate = pygame.Vector2(x, lane_y)

                # Nudge if a course obstacle occupies that point.
                for _ in range(8):
                    if not self.city.is_blocked_point(candidate, 35):
                        break
                    candidate.y += random.choice([-85, 85])
                    candidate.y = max(320, min(1280, candidate.y))

                spawns.append((kind, candidate))

        return spawns, message

    def draw(self, surface, camera, theme):
        font = pygame.font.Font(None, 19)

        for index, camp in enumerate(self.camps):
            x = int(camp["x"] - camera.offset.x)

            if not (-150 < x < surface.get_width() + 150):
                continue

            y = int(320 - camera.offset.y)

            # Sandbag/checkpoint style marker.
            pygame.draw.rect(
                surface,
                (95, 70, 45),
                (x - 60, y, 120, 22),
                border_radius=8,
            )
            pygame.draw.rect(
                surface,
                (145, 110, 65),
                (x - 48, y - 18, 42, 20),
                border_radius=6,
            )
            pygame.draw.rect(
                surface,
                (145, 110, 65),
                (x + 8, y - 18, 42, 20),
                border_radius=6,
            )

            colour = (
                (120, 125, 140)
                if index in self.triggered
                else (255, 80, 95)
            )

            label = font.render(
                camp["label"],
                True,
                colour,
            )

            surface.blit(
                label,
                label.get_rect(center=(x, y - 34)),
            )
