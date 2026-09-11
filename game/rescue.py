import math
import pygame


FRIEND_NAMES = [
    "NOVA",
    "PIXEL",
    "MILO",
    "LUNA",
    "ZED",
]


class RescueSystem:
    """
    Campaign rescue mission.

    Friends are trapped in cages along the 5 km road.
    The player must stop close enough, press E to unlock them,
    and then escort every rescued friend to the finish line.
    """

    def __init__(self, city):
        self.city = city
        self.reset(1)

    def friend_count_for_level(self, campaign_level):
        # Progressively harder without overcrowding the road.
        if campaign_level <= 2:
            return 1
        if campaign_level <= 5:
            return 2
        if campaign_level <= 8:
            return 3
        if campaign_level == 9:
            return 4
        return 5

    def reset(self, campaign_level):
        self.campaign_level = max(1, min(10, int(campaign_level)))
        count = self.friend_count_for_level(self.campaign_level)

        # Spread cages through the route. All are before the final 0.5 km.
        candidate_x = [
            2450,
            5200,
            8400,
            11700,
            15400,
        ]

        lane_y = [
            500,
            1060,
            610,
            1020,
            600,
        ]

        # Lower levels use fewer, but still distribute them across the run.
        if count == 1:
            selected = [2]
        elif count == 2:
            selected = [1, 3]
        elif count == 3:
            selected = [0, 2, 4]
        elif count == 4:
            selected = [0, 1, 3, 4]
        else:
            selected = [0, 1, 2, 3, 4]

        self.friends = []

        for index in selected:
            position = pygame.Vector2(
                candidate_x[index],
                lane_y[index],
            )

            # If a generated campaign obstacle overlaps the cage, shift it.
            for _ in range(10):
                if not self.city.is_blocked_point(position, 45):
                    break

                position.y += 120
                if position.y > 1200:
                    position.y = 400

            self.friends.append(
                {
                    "name": FRIEND_NAMES[index],
                    "position": position,
                    "rescued": False,
                    "follow_position": position.copy(),
                    "phase": index * 1.3,
                }
            )

    @property
    def total(self):
        return len(self.friends)

    @property
    def rescued_count(self):
        return sum(1 for friend in self.friends if friend["rescued"])

    @property
    def all_rescued(self):
        return self.rescued_count >= self.total

    def next_unrescued(self):
        for friend in self.friends:
            if not friend["rescued"]:
                return friend
        return None

    def missed_friends_behind(self, player):
        return [
            friend
            for friend in self.friends
            if not friend["rescued"] and friend["position"].x < player.x - 180
        ]

    def interact(self, player, announce):
        closest = None
        closest_distance = 999999

        for friend in self.friends:
            if friend["rescued"]:
                continue

            distance = friend["position"].distance_to(player)

            if distance <= 115 and distance < closest_distance:
                closest = friend
                closest_distance = distance

        if closest is None:
            return False

        closest["rescued"] = True
        closest["follow_position"] = player.copy()

        announce(
            f"{closest['name']} RESCUED • GET THEM TO THE FINISH!",
            2.2,
        )

        return True

    def prompt(self, player):
        for friend in self.friends:
            if (
                not friend["rescued"]
                and friend["position"].distance_to(player) <= 135
            ):
                return f"E • UNLOCK {friend['name']}"

        return None

    def update(self, player, dt):
        """
        Rescued friends follow behind the player in an escort trail.
        They are visual followers and do not take damage.
        """
        rescued = [
            friend
            for friend in self.friends
            if friend["rescued"]
        ]

        for index, friend in enumerate(rescued):
            target = player - pygame.Vector2(
                72 + index * 54,
                (index % 2) * 42 - 21,
            )

            delta = target - friend["follow_position"]

            if delta.length() > 2:
                speed = min(
                    480,
                    230 + delta.length() * 1.4,
                )
                friend["follow_position"] += (
                    delta.normalize()
                    * speed
                    * dt
                )

    def objective_text(self):
        if self.all_rescued:
            return f"FRIENDS {self.rescued_count}/{self.total} • ESCORT TO FINISH"

        return f"RESCUE FRIENDS {self.rescued_count}/{self.total}"

    def draw(self, surface, camera, theme, player_character):
        time_s = pygame.time.get_ticks() / 1000.0
        font = pygame.font.Font(None, 20)
        small = pygame.font.Font(None, 17)

        for friend in self.friends:
            if friend["rescued"]:
                world_pos = friend["follow_position"]
            else:
                world_pos = friend["position"]

            sp = camera.world_to_screen(world_pos)

            if not (
                -100 < sp.x < surface.get_width() + 100
                and -100 < sp.y < surface.get_height() + 100
            ):
                continue

            x = int(sp.x)
            y = int(sp.y)

            if not friend["rescued"]:
                # Pulsing rescue beacon.
                pulse = int(
                    27
                    + 6
                    * (
                        0.5
                        + 0.5
                        * math.sin(time_s * 4 + friend["phase"])
                    )
                )

                glow = pygame.Surface(
                    (pulse * 4, pulse * 4),
                    pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    glow,
                    (*theme["accent"], 32),
                    (pulse * 2, pulse * 2),
                    pulse,
                )
                surface.blit(
                    glow,
                    (
                        x - pulse * 2,
                        y - pulse * 2,
                    ),
                )

                # Cage.
                cage = pygame.Rect(
                    x - 28,
                    y - 34,
                    56,
                    68,
                )

                pygame.draw.rect(
                    surface,
                    (35, 38, 50),
                    cage,
                    border_radius=6,
                )
                pygame.draw.rect(
                    surface,
                    theme["accent_2"],
                    cage,
                    3,
                    border_radius=6,
                )

                for bar_x in range(
                    cage.left + 10,
                    cage.right - 5,
                    12,
                ):
                    pygame.draw.line(
                        surface,
                        (125, 130, 150),
                        (bar_x, cage.top + 5),
                        (bar_x, cage.bottom - 5),
                        3,
                    )

                # Friend inside cage.
                pygame.draw.circle(
                    surface,
                    (255, 215, 175),
                    (x, y - 8),
                    9,
                )
                pygame.draw.rect(
                    surface,
                    theme["accent"],
                    (x - 9, y + 2, 18, 20),
                    border_radius=6,
                )

                lock = pygame.Rect(
                    x - 6,
                    y + 22,
                    12,
                    10,
                )
                pygame.draw.rect(
                    surface,
                    (255, 205, 70),
                    lock,
                    border_radius=3,
                )

                label = font.render(
                    f"RESCUE {friend['name']}",
                    True,
                    theme["accent"],
                )
                surface.blit(
                    label,
                    label.get_rect(
                        center=(x, y - 54)
                    ),
                )

            else:
                # Rescued follower.
                pygame.draw.circle(
                    surface,
                    (255, 215, 175),
                    (x, y - 9),
                    8,
                )

                body_colour = (
                    theme["accent_2"]
                    if player_character == "MONSTER"
                    else theme["accent"]
                )

                pygame.draw.rect(
                    surface,
                    body_colour,
                    (x - 8, y, 16, 20),
                    border_radius=6,
                )

                pygame.draw.circle(
                    surface,
                    (255, 255, 255),
                    (x - 3, y - 10),
                    2,
                )
                pygame.draw.circle(
                    surface,
                    (255, 255, 255),
                    (x + 3, y - 10),
                    2,
                )

                tag = small.render(
                    friend["name"],
                    True,
                    (235, 235, 245),
                )
                surface.blit(
                    tag,
                    tag.get_rect(
                        center=(x, y - 28)
                    ),
                )
