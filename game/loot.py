import math
import random
import pygame


class LootSystem:
    """Stage 7.5 loot/lifelines adapted to the 3 km run-and-gun course."""

    def __init__(self, city):
        self.city = city
        self.crate_positions = [p.copy() for p in city.crate_positions]
        self.safehouses = [p.copy() for p in city.safehouse_positions]
        self.reset()

    def reset(self):
        self.coins = []
        self.pickups = []
        self.crates = [
            {"position": p.copy(), "opened": False}
            for p in self.crate_positions
        ]

        rng = random.Random(91)

        for anchor in self.city.coin_anchors:
            for _ in range(5):
                candidate = anchor + pygame.Vector2(
                    rng.randint(-110, 110),
                    rng.randint(-100, 100),
                )

                if not self.city.is_blocked_point(candidate, 18):
                    self.coins.append(
                        {
                            "position": candidate,
                            "value": rng.choice([2, 2, 3, 5]),
                            "phase": rng.random() * math.tau,
                        }
                    )

    def spawn_enemy_drop(self, position, enemy_type):
        rng = random.random()

        coin_count = 5 if enemy_type == "BOSS" else 2 if enemy_type == "TANK" else 1
        coin_value = 8 if enemy_type == "BOSS" else 3

        for _ in range(coin_count):
            self.coins.append(
                {
                    "position": position.copy()
                    + pygame.Vector2(
                        random.randint(-22, 22),
                        random.randint(-22, 22),
                    ),
                    "value": coin_value,
                    "phase": random.random() * math.tau,
                }
            )

        if enemy_type == "BOSS" or rng < 0.04:
            item_type = "LIFELINE"
        elif rng < 0.13:
            item_type = "MEDKIT"
        elif rng < 0.26:
            item_type = "ARMOR"
        else:
            item_type = None

        if item_type:
            self.pickups.append(
                {
                    "type": item_type,
                    "position": position.copy(),
                    "phase": random.random() * math.tau,
                }
            )

    def update(self, player, dt, inventory, announce):
        for coin in self.coins[:]:
            distance = coin["position"].distance_to(player)

            if 0 < distance < 150:
                coin["position"] += (
                    player - coin["position"]
                ).normalize() * 410 * dt

            if distance < 32:
                inventory.add_coins(coin["value"])
                self.coins.remove(coin)

        for item in self.pickups[:]:
            if item["position"].distance_to(player) >= 34:
                continue

            item_type = item["type"]

            if item_type == "LIFELINE":
                if inventory.add_lifeline():
                    announce("LIFELINE ACQUIRED!", 1.5)
                else:
                    inventory.add_coins(15)
                    announce("LIFELINES FULL • +15 COINS", 1.3)

            elif item_type == "MEDKIT":
                inventory.add_medkit()
                announce("MEDKIT ACQUIRED", 1.2)

            elif item_type == "ARMOR":
                inventory.add_armor(30)
                announce("ARMOR +30", 1.2)

            self.pickups.remove(item)

    def interact(self, player, inventory, announce):
        for crate in self.crates:
            if crate["opened"]:
                continue

            if crate["position"].distance_to(player) <= 72:
                crate["opened"] = True
                inventory.crates_opened += 1

                reward = random.choice(
                    ["COINS", "COINS", "ARMOR", "MEDKIT", "LIFELINE"]
                )

                if reward == "COINS":
                    amount = random.randint(15, 30)
                    inventory.add_coins(amount)
                    announce(f"SUPPLY CRATE • +{amount} COINS", 1.7)

                elif reward == "ARMOR":
                    inventory.add_armor(40)
                    announce("SUPPLY CRATE • ARMOR +40", 1.7)

                elif reward == "MEDKIT":
                    inventory.add_medkit()
                    announce("SUPPLY CRATE • MEDKIT", 1.7)

                elif reward == "LIFELINE":
                    if inventory.add_lifeline():
                        announce("SUPPLY CRATE • EXTRA LIFELINE!", 2.0)
                    else:
                        inventory.add_coins(25)
                        announce("LIFELINES FULL • +25 COINS", 1.7)

                return True

        for safehouse in self.safehouses:
            if safehouse.distance_to(player) <= 90:
                if inventory.buy_lifeline(50):
                    announce("CHECKPOINT STORE • LIFELINE PURCHASED", 1.8)
                elif inventory.lifelines >= inventory.max_lifelines:
                    announce("LIFELINES FULL", 1.4)
                else:
                    announce("NEED 50 COINS FOR LIFELINE", 1.4)
                return True

        return False

    def prompt(self, player):
        for crate in self.crates:
            if not crate["opened"] and crate["position"].distance_to(player) <= 95:
                return "E • OPEN SUPPLY CRATE"

        for safehouse in self.safehouses:
            if safehouse.distance_to(player) <= 110:
                return "E • CHECKPOINT STORE: LIFELINE (50 COINS)"

        return None

    def draw(self, surface, camera, theme, text_colour):
        time_s = pygame.time.get_ticks() / 1000

        for coin in self.coins:
            sp = camera.world_to_screen(coin["position"])

            if not (-30 < sp.x < surface.get_width() + 30 and -30 < sp.y < surface.get_height() + 30):
                continue

            bob = math.sin(time_s * 4 + coin["phase"]) * 4
            cx, cy = int(sp.x), int(sp.y + bob)

            glow = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 70, 45), (20, 20), 18)
            surface.blit(glow, (cx - 20, cy - 20))

            pygame.draw.circle(surface, (255, 220, 70), (cx, cy), 8)
            pygame.draw.circle(surface, (255, 247, 170), (cx, cy), 4)
            pygame.draw.circle(surface, (120, 90, 15), (cx, cy), 8, 2)

        for item in self.pickups:
            sp = camera.world_to_screen(item["position"])

            if not (-40 < sp.x < surface.get_width() + 40 and -40 < sp.y < surface.get_height() + 40):
                continue

            bob = math.sin(time_s * 3.5 + item["phase"]) * 5
            x, y = int(sp.x), int(sp.y + bob)

            if item["type"] == "LIFELINE":
                colour = (255, 80, 120)
                pygame.draw.circle(surface, colour, (x - 6, y - 3), 7)
                pygame.draw.circle(surface, colour, (x + 6, y - 3), 7)
                pygame.draw.polygon(surface, colour, [(x - 13, y), (x + 13, y), (x, y + 17)])

            elif item["type"] == "MEDKIT":
                pygame.draw.rect(surface, (240, 245, 250), (x - 13, y - 13, 26, 26), border_radius=5)
                pygame.draw.rect(surface, (255, 70, 90), (x - 4, y - 10, 8, 20))
                pygame.draw.rect(surface, (255, 70, 90), (x - 10, y - 4, 20, 8))

            else:
                colour = (90, 180, 255)
                pygame.draw.polygon(
                    surface,
                    colour,
                    [
                        (x, y - 15),
                        (x + 13, y - 7),
                        (x + 10, y + 10),
                        (x, y + 17),
                        (x - 10, y + 10),
                        (x - 13, y - 7),
                    ],
                )

        for crate in self.crates:
            sp = camera.world_to_screen(crate["position"])

            if not (-80 < sp.x < surface.get_width() + 80 and -80 < sp.y < surface.get_height() + 80):
                continue

            x, y = int(sp.x), int(sp.y)

            if crate["opened"]:
                pygame.draw.rect(surface, (75, 75, 82), (x - 22, y - 12, 44, 24), border_radius=4)
                pygame.draw.line(surface, (110, 110, 120), (x - 20, y - 10), (x + 15, y - 24), 4)
                continue

            pygame.draw.rect(surface, (155, 105, 30), (x - 24, y - 17, 48, 34), border_radius=6)
            pygame.draw.rect(surface, (255, 205, 70), (x - 24, y - 17, 48, 34), 3, border_radius=6)
            pygame.draw.rect(surface, (255, 205, 70), (x - 5, y - 17, 10, 34))
            pygame.draw.circle(surface, theme["accent"], (x, y), 4)

        for safehouse in self.safehouses:
            sp = camera.world_to_screen(safehouse)

            if -100 < sp.x < surface.get_width() + 100 and -100 < sp.y < surface.get_height() + 100:
                x, y = int(sp.x), int(sp.y)

                pygame.draw.circle(surface, theme["accent"], (x, y), 42, 3)
                pygame.draw.circle(surface, theme["accent_2"], (x, y), 30, 2)
                pygame.draw.rect(surface, (25, 28, 38), (x - 18, y - 16, 36, 32), border_radius=5)
                pygame.draw.rect(surface, theme["accent"], (x - 5, y - 12, 10, 24))
                pygame.draw.rect(surface, theme["accent"], (x - 12, y - 5, 24, 10))

                font = pygame.font.Font(None, 19)
                label = font.render("CHECKPOINT STORE", True, text_colour)
                surface.blit(label, label.get_rect(center=(x, y + 58)))
