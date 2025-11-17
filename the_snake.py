from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Все ячейки игрового поля:
ALL_CELLS = set(
    (
        x * GRID_SIZE,
        y * GRID_SIZE,
    )
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

# Стартовая позиция игрового объекта:
CENTRAL_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения змейки:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Возможные повороты змейки при движении:
TURNS = {
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_s): DOWN,
    (RIGHT, pg.K_s): DOWN,
    (LEFT, pg.K_w): UP,
    (RIGHT, pg.K_w): UP,
    (UP, pg.K_a): LEFT,
    (DOWN, pg.K_a): LEFT,
    (UP, pg.K_d): RIGHT,
    (DOWN, pg.K_d): RIGHT,
}

# Константы для скорости движения змейки:
SPEED_START = 15
SPEED_CHANGE = 5
MIN_SPEED = 5
MAX_SPEED = 30

# Цвета элементов интерфейса:
BOARD_BACKGROUND_COLOR = (192, 192, 192)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pg.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self, body_color=None):
        self.position = CENTRAL_POSITION
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки объекта на экране.
        Переопределяется в дочерних классах.
        """
        raise NotImplementedError(
            f'В классе {type(self).__name__} не определен метод draw().'
        )

    def draw_position(self, position, body_color=None):
        """Метод для отрисовки ячейки"""
        body_color = body_color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        if body_color == self.body_color:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, унаследованный от GameObject, описывающий яблоко и
    действия с ним.
    """

    def __init__(
        self,
        employed_positions=None,
        body_color=APPLE_COLOR
    ):
        super().__init__(body_color)
        self.randomize_position(employed_positions)

    def randomize_position(self, employed_positions):
        """Устанавливает случайное положение яблока в пределах игрового поля,
        проверяя, что оно не совпадает с позицией змейки.
        """
        if employed_positions is not None:
            self.position = choice(tuple(ALL_CELLS - set(employed_positions)))

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_position(self.position)


class Snake(GameObject):
    """Класс, унаследованный от GameObject, описывающий змейку и
    её поведение.
    """

    def __init__(self, direction=RIGHT, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset(direction)

    def update_direction(self, new_direction):
        """Метод обновления направления после нажатия на кнопку."""
        self.direction = new_direction

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции)."""
        px, py = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(0, (
            (px + dx * GRID_SIZE) % SCREEN_WIDTH,
            (py + dy * GRID_SIZE) % SCREEN_HEIGHT,
        ))
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else self.positions[-1]
        )

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        # Отрисовка головы змейки.
        self.draw_position(self.get_head_position())

        # Затирание последнего сегмента.
        if self.last:
            self.draw_position(self.last, BOARD_BACKGROUND_COLOR)

    def head_body_collision(self):
        """Возвращает True, если координаты головы и тела змейки совпали."""
        if self.length >= 5 and self.get_head_position() in self.positions[4:]:
            return True
        return False

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self, direction=None):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [CENTRAL_POSITION]
        self.direction = direction or choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(snake, speed):
    """Обрабатывает нажатия клавиш,
    чтобы изменить направление и скорость движения змейки.
    """
    SPEED_CHANGE_KEYS = {
        'Увеличение скорости': [pg.K_KP_PLUS, pg.K_PLUS, pg.K_EQUALS],
        'Уменьшение скорости': [pg.K_KP_MINUS, pg.K_MINUS, pg.K_UNDERSCORE],
        'Скорость по умолчанию': [pg.K_SPACE],
    }
    for event in pg.event.get():
        if (event.type == pg.QUIT) or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key in SPEED_CHANGE_KEYS['Увеличение скорости']:
                return min(speed + SPEED_CHANGE, MAX_SPEED)
            elif event.key in SPEED_CHANGE_KEYS['Уменьшение скорости']:
                return max(speed - SPEED_CHANGE, MIN_SPEED)
            elif event.key in SPEED_CHANGE_KEYS['Скорость по умолчанию']:
                return SPEED_START
            else:
                snake.update_direction(
                    TURNS.get((snake.direction, event.key), snake.direction)
                )
    return speed


def main():
    """Основной цикл игры."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake = Snake()
    apple = Apple(snake.positions)
    speed = SPEED_START
    record_length = 1

    while True:
        clock.tick(speed)

        speed = handle_keys(snake, speed)
        snake.move()
        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            snake.length += 1
            record_length = max(record_length, snake.length)
        elif snake.head_body_collision():
            snake.reset()
            speed = SPEED_START
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        snake.draw()
        apple.draw()
        pg.display.update()
        pg.display.set_caption(
            f'Упр. скоростью({speed}): +, -, пробел. '
            f'Длина: {snake.length}. Рекорд: {record_length}. '
            f'Выход: Esc.'
        )


if __name__ == '__main__':
    main()
