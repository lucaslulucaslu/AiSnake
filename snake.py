import tkinter as tk
import random
import time
import heapq

# Define constants
GRID_WIDTH = 24
GRID_HEIGHT = 36
CELL_SIZE = 15
WIDTH, HEIGHT = GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE
INITIAL_DELAY = 50

# Define directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

def main():
    game = SnakeGame()
    game.run()

class SnakeGame:
    def __init__(self):
        self.running = True
        self.setup_gui()
        self.start_game()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("AI Snake Game")

        self.score_label = tk.Label(self.root, text="Score: 0", font=("Helvetica", 14))
        self.score_label.pack()

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

        # Keyboard bindings for manual control
        self.root.bind("<Up>", lambda e: self.set_direction(UP))
        self.root.bind("<Down>", lambda e: self.set_direction(DOWN))
        self.root.bind("<Left>", lambda e: self.set_direction(LEFT))
        self.root.bind("<Right>", lambda e: self.set_direction(RIGHT))

    def start_game(self):
        self.running = True
        self.snake = [(5, 5), (6, 5), (7, 5)]  # Reset initial snake position
        self.snake_segments_colors = ["green"] * len(self.snake)  # Initial snake segments color
        self.direction = RIGHT
        self.food = self.random_food_position()
        self.food_color = "#%06x" % random.randint(0, 0xFFFFFF)

    def random_food_position(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.snake = [new_head] + self.snake

    def a_star(self, start, goal, avoid_tail=True):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        body_set = set(self.snake[:-1]) if avoid_tail else set(self.snake)

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for direction in DIRECTIONS:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if not (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT):
                    continue
                if neighbor in body_set:
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def flood_fill_area(self, start):
        queue = [start]
        visited = set(queue)
        body_set = set(self.snake)

        count = 0
        while queue:
            current = queue.pop(0)
            count += 1

            for direction in DIRECTIONS:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and
                    neighbor not in visited and neighbor not in body_set):
                    queue.append(neighbor)
                    visited.add(neighbor)

        return count

    def ai_decide_direction(self):
        head = self.snake[0]
        path_to_food = self.a_star(head, self.food)

        if path_to_food:
            next_step = path_to_food[0]
            if self.flood_fill_area(next_step) > len(self.snake):
                self.direction = (next_step[0] - head[0], next_step[1] - head[1])
            else:
                self.move_to_tail()
        else:
            self.move_to_tail()

    def move_to_tail(self):
        tail = self.snake[-1]
        path_to_tail = self.a_star(self.snake[0], tail, avoid_tail=False)
        if path_to_tail:
            next_step = path_to_tail[0]
            self.direction = (next_step[0] - self.snake[0][0], next_step[1] - self.snake[0][1])
        else:
            for direction in DIRECTIONS:
                neighbor = (self.snake[0][0] + direction[0], self.snake[0][1] + direction[1])
                if (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT) and neighbor not in self.snake:
                    self.direction = direction
                    break

    def check_collision(self):
        head = self.snake[0]
        if head in self.snake[1:]:
            return True
        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            return True
        return False

    def draw_board(self):
        self.canvas.delete("all")
        for (x, y), color in zip(self.snake, self.snake_segments_colors):
            self.canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill=color)
        food_x, food_y = self.food
        self.canvas.create_rectangle(food_x * CELL_SIZE, food_y * CELL_SIZE, (food_x + 1) * CELL_SIZE, (food_y + 1) * CELL_SIZE, fill=self.food_color)

        self.score_label.config(text=f"Score: {len(self.snake) - 3}")

    def flash_and_restart(self):
        self.running = False
        for _ in range(5):
            self.canvas.config(bg='red')
            self.root.update()
            time.sleep(0.1)
            self.canvas.config(bg='black')
            self.root.update()
            time.sleep(0.1)
        self.start_game()

    def run(self):
        while True:
            if not self.running:
                break

            self.ai_decide_direction()
            self.move_snake()

            if self.snake[0] == self.food:
                self.snake_segments_colors.insert(0, self.food_color)
                self.food = self.random_food_position()
                self.food_color = "#%06x" % random.randint(0, 0xFFFFFF)
                
            else:
                if len(self.snake) > 1:
                    self.snake.pop()
                    if len(self.snake_segments_colors) > len(self.snake):
                        self.snake_segments_colors.pop()

            if self.check_collision():
                self.flash_and_restart()

            self.draw_board()
            self.root.update()

            time.sleep(INITIAL_DELAY / 1000.0)

    def set_direction(self, direction):
        if (direction[0] != -self.direction[0] or direction[1] != -self.direction[1]):
            self.direction = direction

if __name__ == "__main__":
    main()
