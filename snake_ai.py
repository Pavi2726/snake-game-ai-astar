import pygame
import random
from enum import Enum
from collections import namedtuple
import sys
import heapq
import os

pygame.init()
font = pygame.font.SysFont('Arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLUE1 = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (170, 215, 81)
DARK_GREEN = (162, 209, 73)

BLOCK_SIZE = 20
INITIAL_SPEED = 15
SPEED_INCREMENT = 1
MAX_SPEED = 30

class SnakeGameAI:
    def __init__(self):
        self.window = pygame.display.set_mode((700, 700), pygame.RESIZABLE)
        pygame.display.set_caption('A* Snake AI')
        self.clock = pygame.time.Clock()
        self.high_score = self._load_high_score()

        try:
            self.restart_icon = pygame.transform.scale(pygame.image.load("restart_icon.png"), (50, 50))
            self.quit_icon = pygame.transform.scale(pygame.image.load("quit_icon.png"), (50, 50))
        except:
            self.restart_icon = pygame.Surface((50, 50))
            self.restart_icon.fill(GREEN)
            self.quit_icon = pygame.Surface((50, 50))
            self.quit_icon.fill(RED)

        self.cols = 30  # Increased from 20
        self.rows = 30  # Increased from 20
        self._update_dimensions()
        self.reset()

    def _update_dimensions(self):
        self.window_width, self.window_height = self.window.get_size()
        self.w = self.cols * BLOCK_SIZE
        self.h = self.rows * BLOCK_SIZE
        self.offset_x = (self.window_width - self.w) // 2
        self.offset_y = (self.window_height - self.h) // 2 + 30  # shift down to make space for score

    def reset(self):
        self._update_dimensions()
        self.direction = Direction.RIGHT
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - 2 * BLOCK_SIZE, self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()

    def _load_high_score(self):
        if os.path.exists("high_score.txt"):
            with open("high_score.txt", "r") as file:
                return int(file.read())
        return 0

    def _save_high_score(self):
        with open("high_score.txt", "w") as file:
            file.write(str(self.high_score))

    def _place_food(self):
        while True:
            x = random.randint(0, self.cols - 1) * BLOCK_SIZE
            y = random.randint(0, self.rows - 1) * BLOCK_SIZE
            self.food = Point(x, y)
            if self.food not in self.snake:
                break

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self._update_dimensions()

        self._move_astar()
        self.snake.insert(0, self.head)

        game_over = False
        if self._is_collision():
            game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            return game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        speed = min(INITIAL_SPEED + self.score * SPEED_INCREMENT, MAX_SPEED)
        self._update_ui()
        self.clock.tick(speed)
        return False, self.score

    def _is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x >= self.w or pt.x < 0 or pt.y >= self.h or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.window.fill(BLACK)

        # Green checkerboard background
        for row in range(self.rows):
            for col in range(self.cols):
                color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
                pygame.draw.rect(
                    self.window, color,
                    pygame.Rect(
                        self.offset_x + col * BLOCK_SIZE,
                        self.offset_y + row * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE
                    )
                )

        for pt in self.snake[1:]:
            pygame.draw.rect(self.window, BLUE1,
                             pygame.Rect(self.offset_x + pt.x, self.offset_y + pt.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.ellipse(self.window, BLUE1,
                            pygame.Rect(self.offset_x + self.snake[0].x, self.offset_y + self.snake[0].y, BLOCK_SIZE, BLOCK_SIZE * 1.2))
        eye_offset = BLOCK_SIZE // 4
        pygame.draw.circle(self.window, WHITE,
                           (self.offset_x + self.snake[0].x + eye_offset, self.offset_y + self.snake[0].y + eye_offset),
                           BLOCK_SIZE // 5)
        pygame.draw.circle(self.window, WHITE,
                           (self.offset_x + self.snake[0].x + BLOCK_SIZE - eye_offset, self.offset_y + self.snake[0].y + eye_offset),
                           BLOCK_SIZE // 5)

        pygame.draw.rect(self.window, RED,
                         pygame.Rect(self.offset_x + self.food.x, self.offset_y + self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw Score on top of game field
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)

        score_x = self.offset_x
        score_y = self.offset_y - 60

        # Optional background for text
        bg_rect = pygame.Rect(score_x - 10, score_y - 10, 260, 70)
        pygame.draw.rect(self.window, BLACK, bg_rect)

        self.window.blit(score_text, (score_x, score_y))
        self.window.blit(high_score_text, (score_x, score_y + 30))

        pygame.display.flip()

    def _move_astar(self):
        path = self._astar_path(self.head, self.food)
        if path and len(path) > 1:
            next_point = path[1]
            self.direction = self._get_direction(self.head, next_point)
            self.head = next_point
        else:
            self.head = self._get_next_point(self.head, self.direction)

    def _get_direction(self, start, end):
        dx = end.x - start.x
        dy = end.y - start.y
        if dx == BLOCK_SIZE:
            return Direction.RIGHT
        elif dx == -BLOCK_SIZE:
            return Direction.LEFT
        elif dy == BLOCK_SIZE:
            return Direction.DOWN
        elif dy == -BLOCK_SIZE:
            return Direction.UP
        return self.direction

    def _get_next_point(self, point, direction):
        x, y = point.x, point.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        return Point(x, y)

    def _astar_path(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}
        visited = set(self.snake[1:])

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                return self._reconstruct_path(came_from, current)

            for direction in Direction:
                neighbor = self._get_next_point(current, direction)
                if (0 <= neighbor.x < self.w and
                    0 <= neighbor.y < self.h and
                    neighbor not in visited):

                    tentative_g = g_score[current] + 1
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def _heuristic(self, p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))

    def _game_over_ui(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._update_dimensions()

            self.window.fill(BLACK)
            window_width, window_height = self.window.get_size()

            game_over_text = font.render("GAME OVER!", True, WHITE)
            final_score_text = font.render(f"Final Score: {self.score}", True, YELLOW)
            high_score_text = font.render(f"High Score: {self.high_score}", True, GREEN)
            restart_text = font.render("Press R to Restart", True, WHITE)
            quit_text = font.render("Press Q to Quit", True, WHITE)

            center_x = window_width // 2
            game_over_y = window_height // 4
            icon_y = window_height // 2

            self.window.blit(game_over_text, game_over_text.get_rect(center=(center_x, game_over_y)))
            self.window.blit(final_score_text, final_score_text.get_rect(center=(center_x, game_over_y + 40)))
            self.window.blit(high_score_text, high_score_text.get_rect(center=(center_x, game_over_y + 80)))

            icon_gap = 100
            restart_icon_x = center_x - icon_gap
            quit_icon_x = center_x + icon_gap

            self.window.blit(self.restart_icon, (restart_icon_x, icon_y))
            self.window.blit(self.quit_icon, (quit_icon_x, icon_y))
            self.window.blit(restart_text, restart_text.get_rect(center=(restart_icon_x + 25, icon_y + 70)))
            self.window.blit(quit_text, quit_text.get_rect(center=(quit_icon_x + 25, icon_y + 70)))

            pygame.display.flip()

if __name__ == '__main__':
    game = SnakeGameAI()
    while True:
        game_over, score = game.play_step()
        if game_over:
            game._game_over_ui()
