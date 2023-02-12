import pygame, sys
from copy import deepcopy
from random import choice, randrange


WIDTH, HEIGHT = 10, 20
TILE = 30
BOARD_RESOLUTION = WIDTH * TILE, HEIGHT * TILE
RESOLUTION = 550, 640
FPS = 60


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(RESOLUTION)
        self.game_screen = pygame.Surface(BOARD_RESOLUTION)
        self.clock = pygame.time.Clock()

        self.grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(WIDTH) for y in range(HEIGHT)]

        self.figures_coords = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                               [(0, 0), (0, -1), (0, 1), (-1, -1)],
                               [(0, 0), (0, -1), (0, 1), (1, -1)],
                               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        self.figures = [[pygame.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in coords] for coords in self.figures_coords]
        self.figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
        self.field = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

        self.background = pygame.image.load('img/background.jpg').convert()

        self.falling_count, self.falling_speed, self.falling_limit = 0, 60, 2000

        self.main_font = pygame.font.Font('font/font.ttf', 40)
        self.font = pygame.font.Font('font/font.ttf', 30)

        self.title_tetris = self.main_font.render('ТЕТРИС', True, pygame.Color('green'))
        self.title_score = self.font.render('ОЧКИ:', True, pygame.Color('orange'))
        self.title_record = self.font.render('РЕКОРД:', True, pygame.Color('red'))

        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_random_color(), self.get_random_color()

        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}  # cоответсвие кол-во очков за заполненные линии

    def control(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.dx = -1
                elif event.key == pygame.K_RIGHT:
                    self.dx = 1
                elif event.key == pygame.K_DOWN:
                    self.falling_limit = 100
                elif event.key == pygame.K_UP:
                    self.rotate = True

    def move_x(self):
        self.figure_old = deepcopy(self.figure)
        for i in range(4):
            self.figure[i].x += self.dx
            if not self.check_borders(i):
                self.figure = deepcopy(self.figure_old)
                break

    def draw_figure(self):
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * TILE
            self.figure_rect.y = self.figure[i].y * TILE
            pygame.draw.rect(self.game_screen, self.color, self.figure_rect)

    def move_y(self):
        self.falling_count += self.falling_speed
        if self.falling_count > self.falling_limit:
            self.falling_count = 0
            self.figure_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].y += 1
                if not self.check_borders(i):
                    for j in range(4):
                        self.field[self.figure_old[j].y][self.figure_old[j].x] = self.color
                    self.figure, self.color = self.next_figure, self.next_color
                    self.next_figure, self.next_color = deepcopy(choice(self.figures)), self.get_random_color()
                    self.falling_limit = 2000
                    break

    def rotate_figure(self):
        self.center = self.figure[0]
        self.figure_old = deepcopy(self.figure)
        if self.rotate:
            for i in range(4):
                self.x = self.figure[i].y - self.center.y
                self.y = self.figure[i].x - self.center.x
                self.figure[i].x = self.center.x - self.x
                self.figure[i].y = self.center.y + self.y
                if not self.check_borders(i):
                    self.figure = deepcopy(self.figure_old)
                    break

    def check_lines(self):
        self.line, self.lines = HEIGHT - 1, 0
        for row in range(HEIGHT - 1, -1, -1):
            self.count = 0
            for i in range(WIDTH):
                if self.field[row][i]:
                    self.count += 1
                self.field[self.line][i] = self.field[row][i]
            if self.count < WIDTH:
                self.line -= 1
            else:
                self.falling_speed += 3
                self.lines += 1

    def draw_field(self):
        for y, raw in enumerate(self.field):
            for x, col in enumerate(raw):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * TILE, y * TILE
                    pygame.draw.rect(self.game_screen, col, self.figure_rect)

    def draw_next_figure(self):
        for i in range(4):
            self.figure_rect.x = self.next_figure[i].x * TILE + 250
            self.figure_rect.y = self.next_figure[i].y * TILE + 150
            pygame.draw.rect(self.screen, self.next_color, self.figure_rect)

    def draw_titles(self):
        self.screen.blit(self.title_tetris, (350, 20))
        self.screen.blit(self.title_score, (350, 300))
        self.screen.blit(self.font.render(str(self.score), True, pygame.Color('blue')), (350, 350))
        self.screen.blit(self.title_record, (350, 400))
        self.screen.blit(self.font.render(self.record, True, pygame.Color('yellow')), (350, 450))

    def game_end(self):
        for i in range(WIDTH):
            if self.field[0][i]:
                if self.score > int(self.record):
                    self.set_record()
                self.field = [[0 for j in range(WIDTH)] for i in range(HEIGHT)]
                self.falling_count, falling_speed, falling_limit = 0, 60, 2000
                self.score = 0
                for i_rect in self.grid:
                    pygame.draw.rect(self.game_screen, self.get_random_color(), i_rect)
                    self.screen.blit(self.game_screen, (20, 20))
                    pygame.display.flip()
                    self.clock.tick(200)

    def get_random_color(self):
        return randrange(50, 256), randrange(50, 256), randrange(50, 256)

    def get_record(self):
        try:
            with open('record.txt') as f:
                self.record = f.readline().strip()
        except FileNotFoundError:
            with open('record.txt', 'w') as f:
                f.write('0')

    def set_record(self):
        with open('record.txt', 'w') as f:
            f.write(str(self.score))

    def check_borders(self, i):
        if self.figure[i].x < 0 or self.figure[i].x > WIDTH - 1:
            return False
        elif self.figure[i].y > HEIGHT - 1 or self.field[self.figure[i].y][self.figure[i].x]:
            return False
        return True

    def play(self):
        while True:
            self.get_record()
            self.dx, self.rotate = 0, False
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.game_screen, (20, 20))
            self.surf = pygame.Surface((300, 600))
            self.surf.fill((0, 0, 0))
            self.game_screen.blit(self.surf, (0, 0))

            for i in range(self.lines):
                pygame.time.wait(200)

            self.control()
            self.move_x()
            self.move_y()
            self.rotate_figure()
            self.check_lines()

            self.score += self.scores[self.lines]

            [pygame.draw.rect(self.game_screen, (40, 40, 40), i_rect, 1) for i_rect in self.grid]  # рисуем клетки

            self.draw_figure()
            self.draw_field()
            self.draw_next_figure()
            self.draw_titles()
            self.game_end()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.play()
    sys.exit()
