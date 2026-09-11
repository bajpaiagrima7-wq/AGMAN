import math
import random
import pygame

WORLD_WIDTH = 21200
WORLD_HEIGHT = 1600

PIXELS_PER_KM = 4000
TRACK_TOP = 250
TRACK_BOTTOM = 1350


class RunnerWorld:
    """
    AGMAN Stage 8: a 3 km run-and-gun course.

    The player must physically reach the finish line while enemies attack
    and solid obstacles force lane changes.
    """

    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT

        self.spawn = pygame.Vector2(350, 800)
        self.finish_x = 20350
        self.goal_position = pygame.Vector2(self.finish_x, 800)

        # Solid course obstacles. Each has a kind used only for drawing.
        self.obstacles = [
            # START SECTOR — hurdles begin immediately
            ("BARRICADE", pygame.Rect(780, 430, 90, 320)),
            ("CONCRETE", pygame.Rect(980, 920, 160, 140)),
            ("WRECK", pygame.Rect(1290, 1020, 220, 95)),
            ("CRATES", pygame.Rect(1560, 520, 150, 170)),
            ("BARRICADE", pygame.Rect(1880, 810, 90, 360)),
            ("WRECK", pygame.Rect(2260, 410, 220, 98)),
            ("CONCRETE", pygame.Rect(2600, 690, 170, 145)),
            ("CRATES", pygame.Rect(2960, 930, 150, 180)),
            ("BARRICADE", pygame.Rect(3340, 500, 95, 370)),
            ("WRECK", pygame.Rect(3720, 1030, 225, 95)),

            # 4 KM sector
            ("CRATES", pygame.Rect(4140, 560, 165, 180)),
            ("CONCRETE", pygame.Rect(4480, 870, 180, 145)),
            ("BARRICADE", pygame.Rect(4860, 400, 90, 360)),
            ("WRECK", pygame.Rect(5260, 960, 230, 100)),
            ("CRATES", pygame.Rect(5660, 560, 170, 185)),
            ("CONCRETE", pygame.Rect(6040, 760, 170, 150)),
            ("BARRICADE", pygame.Rect(6420, 980, 95, 320)),
            ("WRECK", pygame.Rect(6770, 430, 230, 100)),
            ("CRATES", pygame.Rect(7160, 840, 160, 180)),
            ("CONCRETE", pygame.Rect(7520, 520, 185, 150)),

            # 3 KM sector
            ("BARRICADE", pygame.Rect(7920, 420, 90, 380)),
            ("WRECK", pygame.Rect(8310, 980, 235, 100)),
            ("CRATES", pygame.Rect(8680, 600, 170, 190)),
            ("CONCRETE", pygame.Rect(9060, 870, 185, 155)),
            ("BARRICADE", pygame.Rect(9420, 1010, 90, 300)),
            ("WRECK", pygame.Rect(9780, 430, 230, 95)),
            ("CRATES", pygame.Rect(10140, 820, 170, 185)),
            ("CONCRETE", pygame.Rect(10520, 560, 190, 155)),
            ("BARRICADE", pygame.Rect(10920, 430, 95, 360)),
            ("WRECK", pygame.Rect(11300, 990, 235, 100)),

            # 2 KM sector
            ("CRATES", pygame.Rect(11680, 560, 175, 190)),
            ("CONCRETE", pygame.Rect(12060, 920, 190, 150)),
            ("BARRICADE", pygame.Rect(12440, 390, 90, 380)),
            ("WRECK", pygame.Rect(12840, 1020, 235, 100)),
            ("CRATES", pygame.Rect(13240, 620, 175, 195)),
            ("CONCRETE", pygame.Rect(13620, 780, 190, 155)),
            ("BARRICADE", pygame.Rect(13990, 980, 95, 320)),
            ("WRECK", pygame.Rect(14360, 410, 235, 100)),
            ("CRATES", pygame.Rect(14730, 850, 175, 195)),
            ("CONCRETE", pygame.Rect(15120, 560, 195, 155)),

            # 1 KM + final sectors
            ("BARRICADE", pygame.Rect(15490, 420, 95, 380)),
            ("WRECK", pygame.Rect(15860, 980, 235, 100)),
            ("CRATES", pygame.Rect(16250, 600, 180, 195)),
            ("CONCRETE", pygame.Rect(16650, 900, 195, 160)),
            ("BARRICADE", pygame.Rect(17030, 1020, 90, 280)),
            ("WRECK", pygame.Rect(17410, 430, 235, 100)),
            ("CRATES", pygame.Rect(17780, 850, 180, 195)),
            ("CONCRETE", pygame.Rect(18160, 560, 195, 160)),
            ("BARRICADE", pygame.Rect(18540, 410, 95, 380)),
            ("WRECK", pygame.Rect(18930, 980, 235, 100)),
            ("CRATES", pygame.Rect(19310, 620, 180, 195)),
            ("CONCRETE", pygame.Rect(19690, 860, 195, 165)),
        ]

        # Compatibility with older Stage 7 code.
        self.buildings = [(kind, rect) for kind, rect in self.obstacles]

        # Stage 7.5 loot positions are now placed along the route.
        self.crate_positions = [
            pygame.Vector2(850, 1080),
            pygame.Vector2(2350, 560),
            pygame.Vector2(4200, 1080),
            pygame.Vector2(6100, 520),
            pygame.Vector2(8150, 1080),
            pygame.Vector2(10150, 520),
            pygame.Vector2(12350, 1080),
            pygame.Vector2(14550, 520),
            pygame.Vector2(16750, 1080),
            pygame.Vector2(18850, 520),
        ]

        # Safehouses act like checkpoint stores.
        self.safehouse_positions = [
            pygame.Vector2(4100, 800),   # around 4 km
            pygame.Vector2(8100, 800),   # around 3 km
            pygame.Vector2(12100, 800),  # around 2 km
            pygame.Vector2(16100, 800),  # around 1 km
        ]

        self.coin_anchors = [
            pygame.Vector2(700, 640),
            pygame.Vector2(1900, 1050),
            pygame.Vector2(3400, 560),
            pygame.Vector2(5000, 1050),
            pygame.Vector2(6700, 560),
            pygame.Vector2(8400, 1050),
            pygame.Vector2(10000, 560),
            pygame.Vector2(11600, 1050),
            pygame.Vector2(13300, 560),
            pygame.Vector2(14900, 1050),
            pygame.Vector2(16500, 560),
            pygame.Vector2(18200, 1050),
            pygame.Vector2(19750, 620),
        ]

        self.milestones = [
            (self.spawn.x, "5 KM"),
            (self.finish_x - 4 * PIXELS_PER_KM, "4 KM"),
            (self.finish_x - 3 * PIXELS_PER_KM, "3 KM"),
            (self.finish_x - 2 * PIXELS_PER_KM, "2 KM"),
            (self.finish_x - 1 * PIXELS_PER_KM, "1 KM"),
        ]

        self.neon_signs = [
            (pygame.Vector2(1200, 310), "5 KM"),
            (pygame.Vector2(3600, 1290), "KEEP RUNNING"),
            (pygame.Vector2(5600, 310), "4 KM"),
            (pygame.Vector2(8200, 1290), "SURVIVE"),
            (pygame.Vector2(9800, 310), "3 KM"),
            (pygame.Vector2(12400, 1290), "KEEP SHOOTING"),
            (pygame.Vector2(13800, 310), "2 KM"),
            (pygame.Vector2(16600, 1290), "FINAL ZONE"),
            (pygame.Vector2(17800, 310), "1 KM"),
            (pygame.Vector2(19450, 1290), "NO TURNING BACK"),
        ]

        # Survival-city scenery: decorative only, does not affect collision.
        self.side_buildings = [
            pygame.Rect(500, 60, 520, 150), pygame.Rect(1450, 70, 620, 140),
            pygame.Rect(2500, 55, 500, 160), pygame.Rect(3700, 70, 650, 135),
            pygame.Rect(5050, 55, 520, 155), pygame.Rect(6350, 65, 600, 145),
            pygame.Rect(7600, 50, 520, 165), pygame.Rect(8950, 65, 650, 145),
            pygame.Rect(10300, 50, 520, 160), pygame.Rect(11550, 70, 520, 140),
            pygame.Rect(12850, 55, 620, 150), pygame.Rect(14100, 60, 520, 155),
            pygame.Rect(15450, 50, 650, 165), pygame.Rect(16800, 65, 550, 145),
            pygame.Rect(18150, 55, 600, 155), pygame.Rect(19450, 70, 520, 140),

            pygame.Rect(700, 1390, 560, 150), pygame.Rect(1800, 1395, 620, 140),
            pygame.Rect(3100, 1380, 520, 160), pygame.Rect(4400, 1395, 650, 145),
            pygame.Rect(5750, 1385, 560, 155), pygame.Rect(7050, 1390, 620, 150),
            pygame.Rect(8450, 1380, 520, 160), pygame.Rect(9750, 1395, 620, 145),
            pygame.Rect(11050, 1380, 600, 160), pygame.Rect(12350, 1395, 600, 145),
            pygame.Rect(13700, 1380, 620, 160), pygame.Rect(15100, 1395, 590, 145),
            pygame.Rect(16500, 1380, 650, 160), pygame.Rect(17900, 1390, 600, 150),
            pygame.Rect(19250, 1385, 590, 155),
        ]

        self.abandoned_cars = [
            (pygame.Vector2(1500, 670), 0), (pygame.Vector2(3150, 1010), 180),
            (pygame.Vector2(5200, 680), 0), (pygame.Vector2(7150, 990), 180),
            (pygame.Vector2(9200, 650), 0), (pygame.Vector2(11100, 1010), 180),
            (pygame.Vector2(13150, 670), 0), (pygame.Vector2(14950, 1010), 180),
            (pygame.Vector2(17100, 650), 0), (pygame.Vector2(18950, 1000), 180),
        ]

        self.street_props = [
            pygame.Vector2(1000, 300), pygame.Vector2(2600, 1300),
            pygame.Vector2(4300, 300), pygame.Vector2(6000, 1300),
            pygame.Vector2(7800, 300), pygame.Vector2(9500, 1300),
            pygame.Vector2(11500, 300), pygame.Vector2(13400, 1300),
            pygame.Vector2(15300, 300), pygame.Vector2(17200, 1300),
            pygame.Vector2(19100, 300),
        ]

        self._base_obstacles = [
            (kind, rect.copy())
            for kind, rect in self.obstacles
        ]
        self.campaign_level = 1

    def set_campaign_level(self, level, extra_obstacles=0):
        """Rebuild course density for the selected campaign level."""
        self.campaign_level = max(1, min(10, int(level)))
        self.obstacles = [
            (kind, rect.copy())
            for kind, rect in self._base_obstacles
        ]

        rng = random.Random(9000 + self.campaign_level * 101)
        protected = (
            list(self.crate_positions)
            + list(self.safehouse_positions)
            + [position for position, _ in self.abandoned_cars]
        )

        kinds = ["BARRICADE", "CRATES", "CONCRETE", "WRECK"]

        attempts = 0
        added = 0

        while added < int(extra_obstacles) and attempts < 300:
            attempts += 1

            x = rng.randint(900, int(self.finish_x - 700))
            y = rng.choice([390, 500, 630, 780, 920, 1060])

            kind = rng.choice(kinds)

            if kind == "BARRICADE":
                rect = pygame.Rect(x, y, 80, rng.randint(180, 280))
            elif kind == "WRECK":
                rect = pygame.Rect(x, y, rng.randint(150, 205), 80)
            elif kind == "CRATES":
                rect = pygame.Rect(x, y, rng.randint(110, 150), 130)
            else:
                rect = pygame.Rect(x, y, rng.randint(130, 170), 115)

            # Keep important loot/store locations reachable.
            if any(rect.inflate(180, 180).collidepoint(p.x, p.y) for p in protected):
                continue

            # Avoid forming an accidental full-width wall with another obstacle.
            too_close = False
            for _, existing in self.obstacles:
                if abs(existing.centerx - rect.centerx) < 125:
                    if existing.inflate(0, 170).colliderect(rect.inflate(0, 170)):
                        too_close = True
                        break

            if too_close:
                continue

            self.obstacles.append((kind, rect))
            added += 1

        self.buildings = [
            (kind, rect)
            for kind, rect in self.obstacles
        ]

    def _actor_rect(self, position, radius):
        return pygame.Rect(
            int(position.x - radius),
            int(position.y - radius),
            int(radius * 2),
            int(radius * 2),
        )

    def distance_km(self, position):
        remaining_px = max(0, self.finish_x - position.x)
        return remaining_px / PIXELS_PER_KM

    def progress_ratio(self, position):
        total = self.finish_x - self.spawn.x
        done = max(0, min(total, position.x - self.spawn.x))
        return done / total

    def finished(self, position):
        return position.x >= self.finish_x

    def district_at(self, position):
        distance = self.distance_km(position)
        if distance <= 0:
            return "FINISH LINE"
        if distance <= 0.35:
            return "FINAL SPRINT"
        if distance <= 1:
            return "1 KM SECTOR"
        if distance <= 2:
            return "2 KM SECTOR"
        if distance <= 3:
            return "3 KM SECTOR"
        if distance <= 4:
            return "4 KM SECTOR"
        return "5 KM SECTOR"

    def is_blocked_point(self, position, padding=0):
        x, y = position

        if x < padding or x > self.width - padding:
            return True

        if y < TRACK_TOP + padding or y > TRACK_BOTTOM - padding:
            return True

        point_rect = pygame.Rect(
            int(x - padding),
            int(y - padding),
            max(1, int(padding * 2)),
            max(1, int(padding * 2)),
        )

        return any(
            point_rect.colliderect(rect)
            for _, rect in self.obstacles
        )

    def move_actor(self, position, delta, radius):
        """Axis-separated movement so obstacles actually stop the runner."""
        pos = pygame.Vector2(position)

        # X first.
        pos.x += delta.x
        pos.x = max(radius, min(self.width - radius, pos.x))
        actor = self._actor_rect(pos, radius)

        for _, wall in self.obstacles:
            if actor.colliderect(wall):
                if delta.x > 0:
                    pos.x = wall.left - radius
                elif delta.x < 0:
                    pos.x = wall.right + radius
                actor = self._actor_rect(pos, radius)

        # Y second.
        pos.y += delta.y
        pos.y = max(TRACK_TOP + radius, min(TRACK_BOTTOM - radius, pos.y))
        actor = self._actor_rect(pos, radius)

        for _, wall in self.obstacles:
            if actor.colliderect(wall):
                if delta.y > 0:
                    pos.y = wall.top - radius
                elif delta.y < 0:
                    pos.y = wall.bottom + radius
                actor = self._actor_rect(pos, radius)

        return pos

    def spawn_near(self, origin, min_distance=650, max_distance=950, radius=30):
        """
        Enemies mostly appear ahead of the runner, with some from behind/sides.
        """
        origin = pygame.Vector2(origin)

        for _ in range(80):
            ahead = random.random() < 0.72

            if ahead:
                x = origin.x + random.uniform(min_distance, max_distance)
            else:
                x = origin.x - random.uniform(min_distance * 0.55, max_distance * 0.75)

            y = random.uniform(TRACK_TOP + 70, TRACK_BOTTOM - 70)

            candidate = pygame.Vector2(
                max(radius + 20, min(self.finish_x - 60, x)),
                y,
            )

            if not self.is_blocked_point(candidate, radius + 8):
                return candidate

        return pygame.Vector2(
            min(self.finish_x - 100, origin.x + 700),
            800,
        )

    def _draw_skyline(self, surface, camera, theme, display_mode):
        """Parallax silhouettes above and below the race corridor."""
        top_base = TRACK_TOP - camera.offset.y
        bottom_base = TRACK_BOTTOM - camera.offset.y

        sky = (7, 8, 15) if display_mode == "DARK" else (206, 213, 228)
        far = (20, 24, 36) if display_mode == "DARK" else (178, 185, 200)
        near = (29, 34, 49) if display_mode == "DARK" else (155, 163, 180)

        surface.fill(sky)

        # Distant city blocks scroll slower than the course.
        for layer, colour, factor in (
            (0, far, 0.25),
            (1, near, 0.45),
        ):
            spacing = 180 if layer == 0 else 140
            base_shift = int(camera.offset.x * factor)
            start = -(base_shift % spacing) - spacing

            for sx in range(start, surface.get_width() + spacing, spacing):
                seed = (sx + base_shift + layer * 997) // spacing
                height = 70 + abs((seed * 37) % (120 if layer == 0 else 170))
                width = 80 + abs((seed * 53) % 70)

                # top skyline
                rect = pygame.Rect(sx, int(top_base - height), width, height)
                pygame.draw.rect(surface, colour, rect)

                # bottom skyline
                rect2 = pygame.Rect(
                    sx + 55,
                    int(bottom_base),
                    width,
                    height,
                )
                pygame.draw.rect(surface, colour, rect2)

                if display_mode == "DARK":
                    for wy in range(rect.top + 18, rect.bottom - 10, 28):
                        for wx in range(rect.left + 16, rect.right - 10, 26):
                            if (wx + wy + seed) % 3 == 0:
                                pygame.draw.rect(
                                    surface,
                                    theme["accent"],
                                    (wx, wy, 5, 7),
                                    border_radius=1,
                                )

    def draw(self, surface, camera, theme, display_mode):
        self._draw_skyline(surface, camera, theme, display_mode)

        road = (22, 25, 33) if display_mode == "DARK" else (188, 192, 201)
        shoulder = (42, 47, 59) if display_mode == "DARK" else (210, 213, 220)
        lane = (205, 185, 90) if display_mode == "DARK" else (126, 112, 64)
        rail = (90, 96, 115) if display_mode == "DARK" else (120, 126, 140)

        # Road shoulder and running corridor.
        road_rect = pygame.Rect(
            -int(camera.offset.x),
            int(TRACK_TOP - camera.offset.y),
            self.width,
            TRACK_BOTTOM - TRACK_TOP,
        )

        shoulder_rect = road_rect.inflate(0, 34)
        pygame.draw.rect(surface, shoulder, shoulder_rect)
        pygame.draw.rect(surface, road, road_rect)

        # Guard rails.
        y_top = int(TRACK_TOP - camera.offset.y)
        y_bottom = int(TRACK_BOTTOM - camera.offset.y)

        pygame.draw.line(surface, rail, (0, y_top), (surface.get_width(), y_top), 5)
        pygame.draw.line(surface, rail, (0, y_bottom), (surface.get_width(), y_bottom), 5)

        # Dashed lane markings — wide run-and-gun track, not a Pac-Man maze.
        for lane_y_world in (520, 800, 1080):
            y = int(lane_y_world - camera.offset.y)
            start_x = -int(camera.offset.x) % 120 - 120

            for x in range(start_x, surface.get_width() + 120, 120):
                pygame.draw.rect(
                    surface,
                    lane,
                    (x, y - 3, 58, 6),
                    border_radius=3,
                )

        # Kilometre checkpoint arches.
        for world_x, label in self.milestones:
            sx = int(world_x - camera.offset.x)

            if -120 < sx < surface.get_width() + 120:
                top_y = int(TRACK_TOP - camera.offset.y + 25)
                bottom_y = int(TRACK_BOTTOM - camera.offset.y - 25)

                pygame.draw.line(
                    surface,
                    theme["accent_2"],
                    (sx, top_y),
                    (sx, bottom_y),
                    5,
                )

                box = pygame.Rect(sx - 55, top_y + 20, 110, 38)
                pygame.draw.rect(surface, (8, 10, 18), box, border_radius=8)
                pygame.draw.rect(surface, theme["accent"], box, 2, border_radius=8)

                font = pygame.font.Font(None, 29)
                txt = font.render(label, True, theme["accent"])
                surface.blit(txt, txt.get_rect(center=box.center))

        # Survival-city sidewalks bordering the running corridor.
        top_walk = pygame.Rect(
            -int(camera.offset.x),
            int(TRACK_TOP - camera.offset.y - 46),
            self.width,
            42,
        )
        bottom_walk = pygame.Rect(
            -int(camera.offset.x),
            int(TRACK_BOTTOM - camera.offset.y + 4),
            self.width,
            42,
        )

        pygame.draw.rect(surface, shoulder, top_walk)
        pygame.draw.rect(surface, shoulder, bottom_walk)

        # Side buildings make the arena feel like a damaged city street.
        for rect in self.side_buildings:
            if not rect.colliderect(camera.view_rect):
                continue

            sr = camera.apply_rect(rect)
            pygame.draw.rect(surface, (7, 8, 12), sr.move(7, 7), border_radius=7)

            facade = (31, 35, 49) if display_mode == "DARK" else (181, 186, 198)
            pygame.draw.rect(surface, facade, sr, border_radius=7)
            pygame.draw.rect(surface, theme["accent_2"], sr, 2, border_radius=7)

            # broken / glowing windows
            for wx in range(sr.left + 20, sr.right - 15, 48):
                for wy in range(sr.top + 24, sr.bottom - 18, 38):
                    lit = ((wx + wy) // 7) % 4 != 0
                    colour = theme["accent"] if lit else (15, 17, 24)
                    pygame.draw.rect(surface, colour, (wx, wy, 13, 8), border_radius=1)

        # Abandoned cars in open lanes.
        for position, rotation in self.abandoned_cars:
            sp = camera.world_to_screen(position)

            if not (-90 < sp.x < surface.get_width() + 90 and -90 < sp.y < surface.get_height() + 90):
                continue

            car = pygame.Surface((62, 31), pygame.SRCALPHA)
            pygame.draw.rect(car, (76, 82, 94), (5, 6, 52, 20), border_radius=7)
            pygame.draw.rect(car, (18, 21, 29), (17, 8, 29, 10), border_radius=3)
            pygame.draw.line(car, (145, 75, 45), (10, 10), (52, 23), 3)
            pygame.draw.circle(car, (10, 11, 15), (17, 27), 6)
            pygame.draw.circle(car, (10, 11, 15), (47, 27), 6)

            if rotation:
                car = pygame.transform.rotate(car, rotation)

            surface.blit(car, car.get_rect(center=(int(sp.x), int(sp.y))))

        # Bent street lights / posts.
        for position in self.street_props:
            sp = camera.world_to_screen(position)

            if -60 < sp.x < surface.get_width() + 60 and -60 < sp.y < surface.get_height() + 60:
                x, y = int(sp.x), int(sp.y)
                pygame.draw.line(surface, (95, 100, 115), (x, y + 35), (x + 4, y - 10), 4)
                pygame.draw.line(surface, (95, 100, 115), (x + 4, y - 10), (x + 20, y - 14), 3)
                pygame.draw.circle(surface, theme["accent"], (x + 22, y - 14), 5)

        # Obstacles.
        for kind, rect in self.obstacles:
            if not rect.colliderect(camera.view_rect):
                continue

            sr = camera.apply_rect(rect)

            shadow = sr.move(7, 7)
            pygame.draw.rect(surface, (3, 4, 8), shadow, border_radius=7)

            if kind == "BARRICADE":
                pygame.draw.rect(surface, (125, 65, 40), sr, border_radius=6)
                for yy in range(sr.top + 8, sr.bottom - 6, 32):
                    pygame.draw.line(
                        surface,
                        (255, 190, 70),
                        (sr.left + 6, yy),
                        (sr.right - 6, yy + 18),
                        6,
                    )

            elif kind == "WRECK":
                pygame.draw.rect(surface, (70, 76, 88), sr, border_radius=14)
                pygame.draw.rect(
                    surface,
                    (20, 24, 31),
                    (sr.left + 35, sr.top + 16, max(20, sr.width - 70), max(12, sr.height - 34)),
                    border_radius=7,
                )
                pygame.draw.circle(surface, (10, 11, 15), (sr.left + 38, sr.bottom), 14)
                pygame.draw.circle(surface, (10, 11, 15), (sr.right - 38, sr.bottom), 14)

            elif kind == "CRATES":
                pygame.draw.rect(surface, (132, 88, 32), sr, border_radius=4)
                pygame.draw.rect(surface, (230, 178, 66), sr, 3, border_radius=4)
                pygame.draw.line(surface, (230, 178, 66), sr.topleft, sr.bottomright, 4)
                pygame.draw.line(surface, (230, 178, 66), sr.topright, sr.bottomleft, 4)

            else:
                pygame.draw.rect(surface, (98, 102, 110), sr, border_radius=5)
                pygame.draw.rect(surface, (170, 175, 185), sr, 3, border_radius=5)

        # Neon signs.
        sign_font = pygame.font.Font(None, 24)
        for position, label in self.neon_signs:
            sp = camera.world_to_screen(position)

            if -180 < sp.x < surface.get_width() + 180:
                sign = sign_font.render(label, True, theme["accent"])
                box = sign.get_rect(center=(int(sp.x), int(sp.y))).inflate(18, 10)
                pygame.draw.rect(surface, (8, 10, 18), box, border_radius=5)
                pygame.draw.rect(surface, theme["accent"], box, 2, border_radius=5)
                surface.blit(sign, sign.get_rect(center=box.center))

        # Finish-line beam is visible from well before the actual line.
        finish_screen_x = int(self.finish_x - camera.offset.x)

        if finish_screen_x > surface.get_width():
            # Permanent objective arrow + finish beacon text.
            arrow_x = surface.get_width() - 95
            arrow_y = 155

            pygame.draw.polygon(
                surface,
                theme["accent"],
                [
                    (arrow_x, arrow_y),
                    (arrow_x + 42, arrow_y + 21),
                    (arrow_x, arrow_y + 42),
                ],
            )

            beacon_font = pygame.font.Font(None, 28)
            beacon = beacon_font.render("FINISH", True, theme["accent"])
            surface.blit(
                beacon,
                beacon.get_rect(
                    midright=(surface.get_width() - 110, arrow_y + 21)
                ),
            )

        if -100 < finish_screen_x < surface.get_width() + 100:
            top_y = int(TRACK_TOP - camera.offset.y)
            bottom_y = int(TRACK_BOTTOM - camera.offset.y)

            # Beam
            beam = pygame.Surface((120, max(1, bottom_y - top_y)), pygame.SRCALPHA)
            pygame.draw.rect(beam, (*theme["accent"], 28), beam.get_rect())
            surface.blit(beam, (finish_screen_x - 60, top_y))

            # Checkered physical finish line.
            cell = 18
            rows = max(1, (bottom_y - top_y) // cell)

            for row in range(rows):
                for col in range(2):
                    colour = (245, 245, 245) if (row + col) % 2 == 0 else (25, 25, 30)
                    pygame.draw.rect(
                        surface,
                        colour,
                        (
                            finish_screen_x + col * cell - cell,
                            top_y + row * cell,
                            cell,
                            cell,
                        ),
                    )

            banner = pygame.Rect(finish_screen_x - 90, top_y + 25, 180, 50)
            pygame.draw.rect(surface, (8, 10, 18), banner, border_radius=8)
            pygame.draw.rect(surface, theme["accent"], banner, 3, border_radius=8)

            font = pygame.font.Font(None, 36)
            txt = font.render("FINISH", True, theme["accent"])
            surface.blit(txt, txt.get_rect(center=banner.center))

    def draw_minimap(self, surface, player_position, enemy_positions, accent, text_colour):
        # Horizontal course/race map.
        map_w, map_h = 290, 72
        x = surface.get_width() - map_w - 24
        y = surface.get_height() - map_h - 54

        panel = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        panel.fill((5, 7, 14, 205))

        line_y = 39
        start_x = 18
        end_x = map_w - 18

        pygame.draw.line(panel, (95, 100, 120), (start_x, line_y), (end_x, line_y), 5)

        for world_x, label in self.milestones[1:]:
            ratio = (world_x - self.spawn.x) / (self.finish_x - self.spawn.x)
            px = int(start_x + ratio * (end_x - start_x))
            pygame.draw.line(panel, (150, 155, 175), (px, line_y - 10), (px, line_y + 10), 2)

        # Enemies near course.
        for enemy in enemy_positions[:30]:
            ratio = (enemy.x - self.spawn.x) / (self.finish_x - self.spawn.x)
            if 0 <= ratio <= 1:
                px = int(start_x + ratio * (end_x - start_x))
                pygame.draw.circle(panel, (255, 80, 100), (px, line_y), 2)

        player_ratio = self.progress_ratio(player_position)
        player_x = int(start_x + player_ratio * (end_x - start_x))
        pygame.draw.circle(panel, accent, (player_x, line_y), 6)

        pygame.draw.line(panel, (245, 245, 245), (end_x, line_y - 14), (end_x, line_y + 14), 3)

        font = pygame.font.Font(None, 19)
        title = font.render("5 KM BATTLE RUN", True, text_colour)
        panel.blit(title, (8, 6))

        surface.blit(panel, (x, y))
        pygame.draw.rect(surface, accent, (x, y, map_w, map_h), 2, border_radius=7)
