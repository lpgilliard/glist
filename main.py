import math
import sys
from dataclasses import dataclass

import pygame

# --- Configuration ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
TILE = 56
BOARD_OFFSET_Y = 70

BG_TOP = (13, 16, 28)
BG_BOTTOM = (33, 24, 45)
PANEL = (18, 20, 34)
PANEL_BORDER = (67, 82, 126)
TEXT = (230, 235, 255)
MUTED = (141, 154, 196)

WALL = "#"
FLOOR = " "
TARGET = "."
BOX = "$"
BOX_ON_TARGET = "*"
PLAYER = "@"
PLAYER_ON_TARGET = "+"

LEVELS = [
    [
        " #########   ",
        " #   .   #   ",
        " #  $$   #   ",
        " ###  ###    ",
        " #  @   #    ",
        " #   .  #    ",
        " ########    ",
    ],
    [
        "   ##########   ",
        "   #  .  .  #   ",
        " ### $$ $$  #   ",
        " #   ##   ###   ",
        " # @      #     ",
        " #   ######     ",
        " #####          ",
    ],
    [
        "   ###########   ",
        " ###   . .   ### ",
        " #  $$ ### $$  # ",
        " # #   @   #  # ",
        " #  $$ ### $$  # ",
        " ###   . .   ### ",
        "   ###########   ",
    ],
]


@dataclass
class MoveAnim:
    start_px: tuple[float, float]
    end_px: tuple[float, float]
    elapsed: float = 0.0
    duration: float = 0.14


class Sokoban:
    def __init__(self, level_index: int = 0):
        self.level_index = level_index
        self.load_level(level_index)

    def load_level(self, index: int):
        raw = LEVELS[index]
        self.rows = len(raw)
        self.cols = max(len(r) for r in raw)

        self.base = [[FLOOR for _ in range(self.cols)] for _ in range(self.rows)]
        self.boxes: set[tuple[int, int]] = set()
        self.player = (0, 0)

        for y, row in enumerate(raw):
            for x in range(self.cols):
                c = row[x] if x < len(row) else FLOOR
                if c == WALL:
                    self.base[y][x] = WALL
                elif c == TARGET:
                    self.base[y][x] = TARGET
                elif c == BOX:
                    self.boxes.add((x, y))
                elif c == BOX_ON_TARGET:
                    self.base[y][x] = TARGET
                    self.boxes.add((x, y))
                elif c == PLAYER:
                    self.player = (x, y)
                elif c == PLAYER_ON_TARGET:
                    self.base[y][x] = TARGET
                    self.player = (x, y)

        self.moves = 0
        self.pushes = 0
        self.history: list[tuple[tuple[int, int], set[tuple[int, int]], int, int]] = []
        self.win = False

    def restart(self):
        self.load_level(self.level_index)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def tile_blocked(self, x: int, y: int) -> bool:
        return not self.in_bounds(x, y) or self.base[y][x] == WALL

    def try_move(self, dx: int, dy: int) -> tuple[tuple[int, int], tuple[int, int] | None, tuple[int, int] | None] | None:
        if self.win:
            return None

        px, py = self.player
        nx, ny = px + dx, py + dy

        if self.tile_blocked(nx, ny):
            return None

        self.history.append((self.player, set(self.boxes), self.moves, self.pushes))

        moved_box_from = None
        moved_box_to = None

        if (nx, ny) in self.boxes:
            bx, by = nx + dx, ny + dy
            if self.tile_blocked(bx, by) or (bx, by) in self.boxes:
                self.history.pop()
                return None
            self.boxes.remove((nx, ny))
            self.boxes.add((bx, by))
            moved_box_from, moved_box_to = (nx, ny), (bx, by)
            self.pushes += 1

        self.player = (nx, ny)
        self.moves += 1
        self.win = self.is_complete()
        return (px, py), moved_box_from, moved_box_to

    def undo(self):
        if not self.history:
            return
        self.player, self.boxes, self.moves, self.pushes = self.history.pop()
        self.win = self.is_complete()

    def is_complete(self) -> bool:
        for y in range(self.rows):
            for x in range(self.cols):
                if self.base[y][x] == TARGET and (x, y) not in self.boxes:
                    return False
        return True


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sokoban Neo")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("segoeui", 44, bold=True)
        self.font_ui = pygame.font.SysFont("segoeui", 24)
        self.font_small = pygame.font.SysFont("segoeui", 18)

        self.game = Sokoban(0)
        self.player_anim: MoveAnim | None = None
        self.box_anim: MoveAnim | None = None

    def grid_origin(self) -> tuple[int, int]:
        grid_w = self.game.cols * TILE
        grid_h = self.game.rows * TILE
        ox = (WIDTH - grid_w) // 2
        oy = BOARD_OFFSET_Y + (HEIGHT - BOARD_OFFSET_Y - grid_h) // 2
        return ox, oy

    def tile_to_px(self, x: int, y: int) -> tuple[float, float]:
        ox, oy = self.grid_origin()
        return ox + x * TILE + TILE / 2, oy + y * TILE + TILE / 2

    def handle_input(self):
        key_to_dir = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    self.game.restart()
                    self.player_anim = None
                    self.box_anim = None
                elif event.key == pygame.K_z:
                    self.game.undo()
                    self.player_anim = None
                    self.box_anim = None
                elif event.key == pygame.K_n:
                    self.game.level_index = (self.game.level_index + 1) % len(LEVELS)
                    self.game.load_level(self.game.level_index)
                    self.player_anim = None
                    self.box_anim = None
                elif event.key in key_to_dir and self.player_anim is None:
                    dx, dy = key_to_dir[event.key]
                    result = self.game.try_move(dx, dy)
                    if result:
                        (px, py), b_from, b_to = result
                        self.player_anim = MoveAnim(self.tile_to_px(px, py), self.tile_to_px(*self.game.player))
                        if b_from and b_to:
                            self.box_anim = MoveAnim(self.tile_to_px(*b_from), self.tile_to_px(*b_to))

    def update(self, dt: float):
        if self.player_anim:
            self.player_anim.elapsed += dt
            if self.player_anim.elapsed >= self.player_anim.duration:
                self.player_anim = None

        if self.box_anim:
            self.box_anim.elapsed += dt
            if self.box_anim.elapsed >= self.box_anim.duration:
                self.box_anim = None

    def lerp(self, a: float, b: float, t: float) -> float:
        t = max(0.0, min(1.0, t))
        t = 1 - (1 - t) * (1 - t)
        return a + (b - a) * t

    def anim_pos(self, anim: MoveAnim | None, fallback: tuple[float, float]) -> tuple[float, float]:
        if not anim:
            return fallback
        t = anim.elapsed / anim.duration
        return (
            self.lerp(anim.start_px[0], anim.end_px[0], t),
            self.lerp(anim.start_px[1], anim.end_px[1], t),
        )

    def draw_gradient_bg(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = (
                int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t),
                int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t),
                int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t),
            )
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        time = pygame.time.get_ticks() / 1000
        for i in range(8):
            radius = 100 + i * 28
            cx = int(WIDTH * 0.8 + math.sin(time + i) * 20)
            cy = int(HEIGHT * 0.15 + math.cos(time * 1.2 + i) * 20)
            alpha = max(8, 40 - i * 4)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 153, 255, alpha), (radius, radius), radius)
            self.screen.blit(surf, (cx - radius, cy - radius))

    def draw_ui(self):
        title = self.font_title.render("SOKOBAN NEO", True, TEXT)
        self.screen.blit(title, (36, 20))

        panel = pygame.Rect(WIDTH - 360, 20, 320, 120)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel, 2, border_radius=16)

        lines = [
            f"Niveau : {self.game.level_index + 1}/{len(LEVELS)}",
            f"Mouvements : {self.game.moves}",
            f"Poussées : {self.game.pushes}",
        ]
        for i, text in enumerate(lines):
            label = self.font_ui.render(text, True, TEXT)
            self.screen.blit(label, (panel.x + 20, panel.y + 14 + i * 32))

        controls = "Flèches/WASD: bouger   Z: annuler   R: reset   N: niveau"
        ctrl = self.font_small.render(controls, True, MUTED)
        self.screen.blit(ctrl, (36, HEIGHT - 36))

    def draw_board(self):
        ox, oy = self.grid_origin()
        board_rect = pygame.Rect(ox - 12, oy - 12, self.game.cols * TILE + 24, self.game.rows * TILE + 24)
        pygame.draw.rect(self.screen, (16, 22, 38), board_rect, border_radius=18)
        pygame.draw.rect(self.screen, PANEL_BORDER, board_rect, 2, border_radius=18)

        for y in range(self.game.rows):
            for x in range(self.game.cols):
                tile_rect = pygame.Rect(ox + x * TILE, oy + y * TILE, TILE, TILE)

                if self.game.base[y][x] == WALL:
                    pygame.draw.rect(self.screen, (58, 71, 113), tile_rect, border_radius=10)
                    inner = tile_rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, (43, 53, 89), inner, border_radius=8)
                else:
                    pygame.draw.rect(self.screen, (28, 33, 53), tile_rect, border_radius=9)

                    if self.game.base[y][x] == TARGET:
                        c = (86, 208, 255)
                        pygame.draw.circle(self.screen, c, tile_rect.center, TILE // 6)
                        pygame.draw.circle(self.screen, (146, 236, 255), tile_rect.center, TILE // 12)

        # Draw boxes
        for bx, by in self.game.boxes:
            center = self.tile_to_px(bx, by)
            if self.box_anim and (bx, by) == tuple(int(v) for v in ((self.box_anim.end_px[0] - ox - TILE / 2) / TILE, (self.box_anim.end_px[1] - oy - TILE / 2) / TILE)):
                center = self.anim_pos(self.box_anim, center)
            rect = pygame.Rect(0, 0, TILE - 10, TILE - 10)
            rect.center = (int(center[0]), int(center[1]))
            pygame.draw.rect(self.screen, (255, 170, 79), rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 220, 138), rect.inflate(-18, -18), border_radius=7)

        # Draw player
        p_center = self.tile_to_px(*self.game.player)
        p_center = self.anim_pos(self.player_anim, p_center)
        pr = TILE // 2 - 10
        pygame.draw.circle(self.screen, (138, 228, 132), (int(p_center[0]), int(p_center[1])), pr)
        pygame.draw.circle(self.screen, (204, 255, 164), (int(p_center[0]), int(p_center[1] - 5)), pr // 3)

        if self.game.win:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 12, 20, 135))
            self.screen.blit(overlay, (0, 0))
            msg = self.font_title.render("NIVEAU TERMINÉ ✨", True, (177, 248, 167))
            tip = self.font_ui.render("Appuie sur N pour passer au niveau suivant", True, TEXT)
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))
            self.screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 + 12))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_input()
            self.update(dt)
            self.draw_gradient_bg()
            self.draw_ui()
            self.draw_board()
            pygame.display.flip()


if __name__ == "__main__":
    App().run()
