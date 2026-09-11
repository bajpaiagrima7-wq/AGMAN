import pygame


class Camera:
    """Smooth side-scrolling camera with forward look-ahead for a run-and-gun game."""

    def __init__(
        self,
        screen_width,
        screen_height,
        world_width,
        world_height,
        look_ahead_x=260,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        self.look_ahead_x = look_ahead_x
        self.offset = pygame.Vector2(0, 0)

    def _clamp_offset(self, value):
        value.x = max(0, min(self.world_width - self.screen_width, value.x))
        value.y = max(0, min(self.world_height - self.screen_height, value.y))
        return value

    def snap(self, target):
        desired = pygame.Vector2(
            target.x - self.screen_width / 2 + self.look_ahead_x,
            target.y - self.screen_height / 2,
        )
        self.offset = self._clamp_offset(desired)

    def update(self, target, dt):
        desired = pygame.Vector2(
            target.x - self.screen_width / 2 + self.look_ahead_x,
            target.y - self.screen_height / 2,
        )
        desired = self._clamp_offset(desired)

        follow = min(1.0, dt * 7.5)
        self.offset += (desired - self.offset) * follow
        self.offset = self._clamp_offset(self.offset)

    def world_to_screen(self, point):
        return pygame.Vector2(point) - self.offset

    def screen_to_world(self, point):
        return pygame.Vector2(point) + self.offset

    def apply_rect(self, rect):
        return pygame.Rect(
            int(rect.x - self.offset.x),
            int(rect.y - self.offset.y),
            rect.width,
            rect.height,
        )

    @property
    def view_rect(self):
        return pygame.Rect(
            int(self.offset.x),
            int(self.offset.y),
            self.screen_width,
            self.screen_height,
        )
