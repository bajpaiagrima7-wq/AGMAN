class Inventory:
    """Small survival inventory used by AGMAN Stage 7.5."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.coins = 0
        self.lifelines = 2
        self.max_lifelines = 3
        self.medkits = 1
        self.armor = 25
        self.max_armor = 100
        self.crates_opened = 0

    def add_coins(self, amount):
        self.coins += max(0, int(amount))

    def add_armor(self, amount):
        self.armor = min(self.max_armor, self.armor + max(0, int(amount)))

    def add_lifeline(self, amount=1):
        before = self.lifelines
        self.lifelines = min(self.max_lifelines, self.lifelines + amount)
        return self.lifelines > before

    def add_medkit(self, amount=1):
        self.medkits += max(0, int(amount))

    def absorb_damage(self, amount):
        amount = max(0, int(amount))
        absorbed = min(self.armor, amount)
        self.armor -= absorbed
        return amount - absorbed

    def use_medkit(self, health, max_health):
        if self.medkits <= 0 or health >= max_health:
            return health, False

        self.medkits -= 1
        return min(max_health, health + 45), True

    def consume_lifeline(self):
        if self.lifelines <= 0:
            return False
        self.lifelines -= 1
        return True

    def buy_lifeline(self, cost=50):
        if self.coins < cost or self.lifelines >= self.max_lifelines:
            return False

        self.coins -= cost
        self.lifelines += 1
        return True
