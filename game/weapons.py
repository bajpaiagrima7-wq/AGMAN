import pygame


class WeaponSystem:
    """
    Three-slot run-and-gun weapon system.

    Slot 1: Fire Blaster    - unlimited
    Slot 2: Plasma Rifle    - rapid automatic, ammo
    Slot 3: Flame Shotgun   - spread burst, shells
    """

    def __init__(self, city):
        self.city = city
        self.reset()

    def reset(self):
        self.current = "FIRE BLASTER"
        self.owned = {"FIRE BLASTER"}
        self.ammo = {
            "PLASMA RIFLE": 0,
            "FLAME SHOTGUN": 0,
        }

        # Real wreck-loot points based on the city's abandoned cars.
        rewards = [
            ("PLASMA RIFLE", 90),
            ("RIFLE AMMO", 70),
            ("FLAME SHOTGUN", 22),
            ("SHOTGUN AMMO", 16),
            ("RIFLE AMMO", 90),
            ("SHOTGUN AMMO", 20),
            ("RANDOM SUPPLIES", 0),
            ("RIFLE AMMO", 100),
            ("SHOTGUN AMMO", 24),
            ("RANDOM SUPPLIES", 0),
        ]

        self.wreck_loot = []

        for i, car in enumerate(self.city.abandoned_cars):
            position = car[0].copy()
            reward, amount = rewards[i % len(rewards)]

            self.wreck_loot.append(
                {
                    "position": position,
                    "looted": False,
                    "reward": reward,
                    "amount": amount,
                }
            )

    @property
    def slot_labels(self):
        return [
            ("1", "FIRE BLASTER"),
            ("2", "PLASMA RIFLE"),
            ("3", "FLAME SHOTGUN"),
        ]

    def select_slot(self, slot):
        names = {
            1: "FIRE BLASTER",
            2: "PLASMA RIFLE",
            3: "FLAME SHOTGUN",
        }

        name = names.get(slot)

        if name and name in self.owned:
            self.current = name
            return True

        return False

    def ammo_text(self, name=None):
        name = name or self.current

        if name == "FIRE BLASTER":
            return "∞"

        return str(self.ammo.get(name, 0))

    def has_ammo(self):
        if self.current == "FIRE BLASTER":
            return True

        return self.ammo.get(self.current, 0) > 0

    def consume_ammo(self):
        if self.current == "FIRE BLASTER":
            return

        if self.current in self.ammo:
            self.ammo[self.current] = max(
                0,
                self.ammo[self.current] - 1,
            )

    def fallback_if_empty(self):
        if self.has_ammo():
            return False

        self.current = "FIRE BLASTER"
        return True

    def shot_profile(
        self,
        upgrade_delay,
        fire_damage,
        fire_radius,
        multishot,
    ):
        """
        Returns a dictionary used by main.py's projectile system.
        Existing AGMAN upgrades still influence weapons.
        """
        bonus_damage = max(0, fire_damage - 1)

        if self.current == "PLASMA RIFLE":
            return {
                "angles": [0],
                "delay": max(55, int(upgrade_delay * 0.60)),
                "speed": 1120,
                "life": 1.15,
                "damage": 2 + bonus_damage,
                "radius": 5,
                "colour": (80, 220, 255),
                "trail": (0, 150, 255),
                "particles": 2,
            }

        if self.current == "FLAME SHOTGUN":
            return {
                "angles": [-16, -8, 0, 8, 16],
                "delay": max(320, int(upgrade_delay * 3.0)),
                "speed": 760,
                "life": 0.72,
                "damage": 2 + bonus_damage,
                "radius": max(5, fire_radius - 1),
                "colour": (255, 170, 45),
                "trail": (255, 80, 25),
                "particles": 5,
            }

        if multishot == 1:
            angles = [0]
        elif multishot == 2:
            angles = [-6, 6]
        else:
            angles = [-10, 0, 10]

        return {
            "angles": angles,
            "delay": upgrade_delay,
            "speed": 780,
            "life": 1.25,
            "damage": fire_damage,
            "radius": fire_radius,
            "colour": (255, 220, 70),
            "trail": (255, 135, 40),
            "particles": 3,
        }

    def interact(self, player, inventory, announce):
        for wreck in self.wreck_loot:
            if wreck["looted"]:
                continue

            if wreck["position"].distance_to(player) > 82:
                continue

            wreck["looted"] = True
            reward = wreck["reward"]
            amount = wreck["amount"]

            if reward == "PLASMA RIFLE":
                self.owned.add("PLASMA RIFLE")
                self.ammo["PLASMA RIFLE"] += amount
                self.current = "PLASMA RIFLE"
                announce(
                    f"WRECK LOOT • PLASMA RIFLE + {amount} AMMO",
                    2.1,
                )

            elif reward == "FLAME SHOTGUN":
                self.owned.add("FLAME SHOTGUN")
                self.ammo["FLAME SHOTGUN"] += amount
                self.current = "FLAME SHOTGUN"
                announce(
                    f"WRECK LOOT • FLAME SHOTGUN + {amount} SHELLS",
                    2.1,
                )

            elif reward == "RIFLE AMMO":
                if "PLASMA RIFLE" not in self.owned:
                    self.owned.add("PLASMA RIFLE")

                self.ammo["PLASMA RIFLE"] += amount
                announce(
                    f"WRECK LOOT • RIFLE AMMO +{amount}",
                    1.6,
                )

            elif reward == "SHOTGUN AMMO":
                if "FLAME SHOTGUN" not in self.owned:
                    self.owned.add("FLAME SHOTGUN")

                self.ammo["FLAME SHOTGUN"] += amount
                announce(
                    f"WRECK LOOT • SHOTGUN SHELLS +{amount}",
                    1.6,
                )

            else:
                inventory.add_coins(25)
                inventory.add_armor(20)
                announce(
                    "WRECK LOOT • +25 COINS • ARMOR +20",
                    1.7,
                )

            return True

        return False

    def prompt(self, player):
        for wreck in self.wreck_loot:
            if (
                not wreck["looted"]
                and wreck["position"].distance_to(player) <= 100
            ):
                return "E • SEARCH VEHICLE WRECK"

        return None

    def draw(self, surface, camera, theme):
        font = pygame.font.Font(None, 18)

        for wreck in self.wreck_loot:
            sp = camera.world_to_screen(wreck["position"])

            if not (
                -80 < sp.x < surface.get_width() + 80
                and -80 < sp.y < surface.get_height() + 80
            ):
                continue

            x, y = int(sp.x), int(sp.y)

            if wreck["looted"]:
                marker = font.render("LOOTED", True, (120, 125, 140))
            else:
                pygame.draw.circle(
                    surface,
                    theme["accent"],
                    (x, y - 34),
                    7,
                )
                marker = font.render(
                    "SEARCH",
                    True,
                    theme["accent"],
                )

            surface.blit(
                marker,
                marker.get_rect(center=(x, y - 50)),
            )
