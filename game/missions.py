class MissionSystem:
    """Run-and-gun objectives built around reaching the finish line."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.stage = 0
        self.completed = False

    @property
    def title(self):
        if self.completed:
            return "FINISH LINE REACHED"

        return [
            "OPEN 2 SUPPLY CRATES",
            "COLLECT 30 COINS",
            "REACH THE 4 KM CHECKPOINT",
            "REACH THE 3 KM CHECKPOINT",
            "REACH THE 2 KM CHECKPOINT",
            "REACH THE 1 KM CHECKPOINT",
            "CROSS THE FINISH LINE",
        ][self.stage]

    def progress_text(self, inventory, distance_km, finished):
        if self.completed:
            return "AGMAN RUN COMPLETE"

        if self.stage == 0:
            return f"{min(inventory.crates_opened, 2)}/2 crates"
        if self.stage == 1:
            return f"{min(inventory.coins, 30)}/30 coins"
        if self.stage == 2:
            return f"{distance_km:.2f} km remaining"
        if self.stage == 3:
            return f"{distance_km:.2f} km remaining"
        return "TOUCH THE FINISH LINE" if not finished else "COMPLETE"

    def update(self, inventory, distance_km, finished):
        if self.completed:
            return None

        passed = False

        if self.stage == 0 and inventory.crates_opened >= 2:
            passed = True
        elif self.stage == 1 and inventory.coins >= 30:
            passed = True
        elif self.stage == 2 and distance_km <= 4.0:
            passed = True
        elif self.stage == 3 and distance_km <= 3.0:
            passed = True
        elif self.stage == 4 and distance_km <= 2.0:
            passed = True
        elif self.stage == 5 and distance_km <= 1.0:
            passed = True
        elif self.stage == 6 and finished:
            passed = True

        if not passed:
            return None

        self.stage += 1

        if self.stage >= 7:
            self.completed = True
            return "TARGET COMPLETE • FINISH LINE REACHED!"

        return f"NEW OBJECTIVE: {self.title}"
