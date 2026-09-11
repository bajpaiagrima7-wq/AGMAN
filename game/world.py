import random
import pygame

WORLD_WIDTH = 3200
WORLD_HEIGHT = 2400


class CityWorld:
    """A large scrollable AGMAN city with solid buildings and districts."""

    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT

        # Start on a broad road at City Centre.
        self.spawn = pygame.Vector2(1600, 1260)

        # Each building is a real collision obstacle.
        self.buildings = [
            # Abandoned Hospital district - north west
            ("HOSPITAL A", pygame.Rect(250, 250, 500, 280)),
            ("HOSPITAL B", pygame.Rect(300, 600, 420, 260)),
            ("PHARMACY", pygame.Rect(800, 300, 280, 220)),

            # Neon Market - north / centre
            ("MARKET WEST", pygame.Rect(1180, 250, 350, 260)),
            ("MARKET EAST", pygame.Rect(1650, 250, 390, 260)),
            ("ARCADE", pygame.Rect(1270, 590, 620, 240)),

            # Laboratory district - north east
            ("LAB BLOCK A", pygame.Rect(2270, 240, 650, 300)),
            ("LAB BLOCK B", pygame.Rect(2400, 620, 450, 250)),

            # Central city blocks - leave large cross-shaped roads
            ("CENTRE NW", pygame.Rect(220, 1050, 760, 280)),
            ("CENTRE SW", pygame.Rect(260, 1460, 680, 300)),
            ("CENTRE NE", pygame.Rect(2220, 1040, 720, 300)),
            ("CENTRE SE", pygame.Rect(2260, 1450, 650, 320)),

            # Inner centre blocks
            ("TOWER WEST", pygame.Rect(1080, 1020, 300, 260)),
            ("TOWER EAST", pygame.Rect(1810, 1020, 300, 260)),
            ("CITY HALL", pygame.Rect(1360, 1480, 480, 280)),

            # Metro / south west
            ("METRO TERMINAL", pygame.Rect(450, 1900, 750, 300)),
            ("WAREHOUSE", pygame.Rect(1250, 1920, 420, 260)),

            # Dark zone / south east
            ("DARK BLOCK A", pygame.Rect(2050, 1870, 420, 300)),
            ("DARK BLOCK B", pygame.Rect(2580, 1840, 360, 350)),
        ]

        self.districts = [
            ("ABANDONED HOSPITAL", pygame.Rect(120, 120, 1050, 820)),
            ("NEON MARKET", pygame.Rect(1080, 100, 1050, 800)),
            ("RESEARCH LAB", pygame.Rect(2180, 100, 900, 820)),
            ("CITY CENTRE", pygame.Rect(980, 900, 1240, 950)),
            ("METRO DISTRICT", pygame.Rect(150, 1800, 1650, 500)),
            ("DARK ZONE", pygame.Rect(1850, 1770, 1250, 550)),
        ]

        self.street_lights = [
            pygame.Vector2(1120, 930),
            pygame.Vector2(1600, 920),
            pygame.Vector2(2100, 930),
            pygame.Vector2(1020, 1380),
            pygame.Vector2(1600, 1380),
            pygame.Vector2(2180, 1380),
            pygame.Vector2(1100, 1820),
            pygame.Vector2(1880, 1820),
        ]

    def _actor_rect(self, position, radius):
        return pygame.Rect(
            int(position.x - radius),
            int(position.y - radius),
            int(radius * 2),
            int(radius * 2),
        )

    def is_blocked_point(self, position, padding=0):
        x, y = position
        if x < padding or y < padding or x > self.width - padding or y > self.height - padding:
            return True

        point_rect = pygame.Rect(int(x - padding), int(y - padding), max(1, padding * 2), max(1, padding * 2))
        return any(point_rect.colliderect(rect) for _, rect in self.buildings)

    def move_actor(self, position, delta, radius):
        """Axis-separated collision movement for player and enemies."""
        pos = pygame.Vector2(position)

        # X movement
        pos.x += delta.x
        pos.x = max(radius, min(self.width - radius, pos.x))
        actor = self._actor_rect(pos, radius)

        for _, wall in self.buildings:
            if actor.colliderect(wall):
                if delta.x > 0:
                    pos.x = wall.left - radius
                elif delta.x < 0:
                    pos.x = wall.right + radius
                actor = self._actor_rect(pos, radius)

        # Y movement
        pos.y += delta.y
        pos.y = max(radius, min(self.height - radius, pos.y))
        actor = self._actor_rect(pos, radius)

        for _, wall in self.buildings:
            if actor.colliderect(wall):
                if delta.y > 0:
                    pos.y = wall.top - radius
                elif delta.y < 0:
                    pos.y = wall.bottom + radius
                actor = self._actor_rect(pos, radius)

        return pos

    def spawn_near(self, origin, min_distance=700, max_distance=1000, radius=30):
        """Find an open world position around the player."""
        origin = pygame.Vector2(origin)

        for _ in range(60):
            angle = random.uniform(0, 360)
            distance = random.uniform(min_distance, max_distance)
            candidate = origin + pygame.Vector2(1, 0).rotate(angle) * distance

            candidate.x = max(radius + 10, min(self.width - radius - 10, candidate.x))
            candidate.y = max(radius + 10, min(self.height - radius - 10, candidate.y))

            if not self.is_blocked_point(candidate, radius + 8):
                return candidate

        # Reliable open fallback near City Centre.
        return pygame.Vector2(1600, 1260)

    def district_at(self, position):
        for name, rect in self.districts:
            if rect.collidepoint(position.x, position.y):
                return name
        return "AGMAN CITY"

    def draw(self, surface, camera, theme, display_mode):
        view = camera.view_rect

        # Roads / world floor
        road_colour = (16, 19, 30) if display_mode == "DARK" else (222, 226, 235)
        lane_colour = (50, 58, 78) if display_mode == "DARK" else (180, 185, 198)
        building_fill = (29, 34, 51) if display_mode == "DARK" else (205, 210, 220)
        window_colour = theme["accent"]
        border_colour = theme["accent_2"]

        # Draw a world-space grid only for what the camera can see.
        start_x = max(0, (view.left // 100) * 100)
        end_x = min(self.width, view.right + 100)
        start_y = max(0, (view.top // 100) * 100)
        end_y = min(self.height, view.bottom + 100)

        for x in range(start_x, end_x + 1, 100):
            sx = int(x - camera.offset.x)
            pygame.draw.line(surface, lane_colour, (sx, 0), (sx, camera.screen_height), 1)

        for y in range(start_y, end_y + 1, 100):
            sy = int(y - camera.offset.y)
            pygame.draw.line(surface, lane_colour, (0, sy), (camera.screen_width, sy), 1)

        # Major cross roads.
        roads = [
            pygame.Rect(0, 900, self.width, 120),
            pygame.Rect(0, 1340, self.width, 120),
            pygame.Rect(980, 0, 120, self.height),
            pygame.Rect(2130, 0, 120, self.height),
            pygame.Rect(0, 1780, self.width, 100),
        ]

        for road in roads:
            sr = camera.apply_rect(road)
            if sr.colliderect(surface.get_rect()):
                pygame.draw.rect(surface, road_colour, sr)
                pygame.draw.rect(surface, lane_colour, sr, 2)

        # Buildings
        for label, rect in self.buildings:
            if not rect.colliderect(view):
                continue

            sr = camera.apply_rect(rect)
            pygame.draw.rect(surface, building_fill, sr, border_radius=8)
            pygame.draw.rect(surface, border_colour, sr, 3, border_radius=8)

            # Windows
            for wx in range(sr.left + 24, sr.right - 20, 52):
                for wy in range(sr.top + 26, sr.bottom - 22, 48):
                    if 0 <= wx < camera.screen_width and 0 <= wy < camera.screen_height:
                        pygame.draw.rect(surface, window_colour, (wx, wy, 15, 9), border_radius=2)

            # Building label
            if sr.width > 180 and sr.height > 120:
                font = pygame.font.Font(None, 21)
                text = font.render(label, True, (240, 240, 245) if display_mode == "DARK" else (25, 25, 35))
                tag = text.get_rect(center=(sr.centerx, sr.top + 15))
                surface.blit(text, tag)

        # Street lights
        for light in self.street_lights:
            sp = camera.world_to_screen(light)
            if -50 < sp.x < camera.screen_width + 50 and -50 < sp.y < camera.screen_height + 50:
                pygame.draw.circle(surface, theme["accent"], (int(sp.x), int(sp.y)), 5)
                halo = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(halo, (*theme["accent"], 35), (30, 30), 28)
                surface.blit(halo, (int(sp.x) - 30, int(sp.y) - 30))

        # District names painted onto the city floor.
        font = pygame.font.Font(None, 34)
        for name, rect in self.districts:
            centre = pygame.Vector2(rect.center)
            sp = camera.world_to_screen(centre)
            if -250 < sp.x < camera.screen_width + 250 and -100 < sp.y < camera.screen_height + 100:
                colour = (*theme["accent"],)
                text = font.render(name, True, colour)
                text.set_alpha(85)
                surface.blit(text, text.get_rect(center=(int(sp.x), int(sp.y))))

    def draw_minimap(self, surface, player_position, enemy_positions, accent, text_colour):
        map_w, map_h = 220, 150
        x = surface.get_width() - map_w - 24
        y = surface.get_height() - map_h - 54

        panel = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        panel.fill((5, 7, 14, 195))

        sx = map_w / self.width
        sy = map_h / self.height

        for _, rect in self.buildings:
            r = pygame.Rect(
                int(rect.x * sx),
                int(rect.y * sy),
                max(2, int(rect.width * sx)),
                max(2, int(rect.height * sy)),
            )
            pygame.draw.rect(panel, (75, 80, 100), r)

        for enemy in enemy_positions[:35]:
            pygame.draw.circle(
                panel,
                (255, 80, 100),
                (int(enemy.x * sx), int(enemy.y * sy)),
                2,
            )

        pygame.draw.circle(
            panel,
            accent,
            (int(player_position.x * sx), int(player_position.y * sy)),
            4,
        )

        pygame.draw.rect(panel, accent, panel.get_rect(), 2, border_radius=7)
        surface.blit(panel, (x, y))

        font = pygame.font.Font(None, 19)
        title = font.render("AGMAN CITY MAP", True, text_colour)
        surface.blit(title, (x + 7, y + 6))
