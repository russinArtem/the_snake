from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Стартовая позиция игрового объекта:
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения змейки:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Обратные направления движения змейки:
REVERSE_DIRECTIONS = {
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвета элементов интерфейса:
BOARD_BACKGROUND_COLOR = (192, 192, 192)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self, body_color=None):
        self.position = START_POSITION
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки объекта на экране.
        Переопределяется в дочерних классах.
        """
        raise Exception(
            f'Произошла ошибка: '
            f'в классе {type(self).__name__} не определен метод draw().'
        )

    def draw_position(self, position, body_color=None):
        """Метод для отрисовки ячейки"""
        if body_color is None:
            body_color = self.body_color

        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)

        if body_color == self.body_color:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, унаследованный от GameObject, описывающий яблоко и
    действия с ним.
    """

    def __init__(self, body_color=None, employed_position=[]):
        super().__init__(body_color)
        self.randomize_position(employed_position)

    def randomize_position(self, employed_position):
        """Устанавливает случайное положение яблока в пределах игрового поля,
        проверяя, что оно не совпадает с позицией змейки.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in employed_position:
                break


class Snake(GameObject):
    """Класс, унаследованный от GameObject, описывающий змейку и
    её поведение.
    """

    def __init__(self, body_color=None):
        super().__init__(body_color)
        self.reset()
        self.record_length = 1

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции)."""
        px, py = self.get_head_position()
        dx, dy = self.direction
        new_head_position = (
            (px + dx * GRID_SIZE) % SCREEN_WIDTH,
            (py + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_position)
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            self.draw_position(self.positions.pop(), BOARD_BACKGROUND_COLOR)

    def check_queue(self):
        """Возвращает True, если координаты головы и тела змейки совпали."""
        if self.get_head_position() in self.positions[4:]:
            self.reset(True)
            screen.fill(BOARD_BACKGROUND_COLOR)
            return True

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self, casualty=None):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [START_POSITION]
        self.direction = RIGHT
        self.speed = 10
        self.last = None
        self.next_direction = None
        if casualty:
            self.direction = choice([UP, DOWN, LEFT, RIGHT])


def handle_keys(snake):
    """Обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            if event.key == pg.K_KP_PLUS:
                snake.speed += 5
            elif event.key == pg.K_KP_MINUS:
                snake.speed -= 5
            else:
                snake.next_direction = REVERSE_DIRECTIONS.get(
                    (snake.direction, event.key), snake.direction
                )


def main():
    """Основной цикл игры."""
    # Инициализация pg:
    pg.init()
    # Тут нужно создать экземпляры классов.
    apple = Apple(APPLE_COLOR, [START_POSITION])
    apple.draw_position(apple.position)
    snake = Snake(SNAKE_COLOR)

    while True:
        clock.tick(snake.speed)

        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            apple.draw_position(apple.position)
            snake.length += 1
            if snake.record_length < snake.length:
                snake.record_length += 1
        elif snake.length >= 5:
            if snake.check_queue():
                apple.randomize_position(snake.positions)
                apple.draw_position(apple.position)
        snake.draw_position(snake.get_head_position())
        pg.display.update()
        pg.display.set_caption(
            f'Скорость: {snake.speed}. '
            f'Изм. скорости: клавиши +/-. '
            f'Тек. длина: {snake.length}. '
            f'Рекорд: {snake.record_length}. '
            f'Для выхода - Esc.'
        )


if __name__ == '__main__':
    main()
