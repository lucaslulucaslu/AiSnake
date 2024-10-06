import tkinter as tk
import random
import time
import heapq

# Define constants
GRID_WIDTH = 8
GRID_HEIGHT = 8
CELL_SIZE = 15
WIDTH, HEIGHT = GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE
INITIAL_DELAY = 100

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
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

    def start_game(self):
        self.running = True
        self.snake = [(5, 5)]  # Reset initial snake position
        self.direction = RIGHT
        self.food = self.random_food_position()

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
        """A* algorithm to find the shortest path from start to goal."""
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
                    continue  # Ignore out of bounds
                if neighbor in body_set:
                    continue  # Ignore collisions with the snake itself

                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # No path found

    def heuristic(self, a, b):
        """Calculate the Manhattan distance between two points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def ai_decide_direction(self):
        head = self.snake[0]
        path_to_food = self.a_star(head, self.food)

        # Determine if following the path to the food will leave a safe route
        if path_to_food:
            next_step = path_to_food[0]
            self.direction = (next_step[0] - head[0], next_step[1] - head[1])
        else:
            # If no path to food, just continue in current direction
            for direction in DIRECTIONS:
                neighbor = (head[0] + direction[0], head[1] + direction[1])
                if (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT) and neighbor not in self.snake:
                    self.direction = direction
                    break

    def check_collision(self):
        head = self.snake[0]
        if head in self.snake[1:]:
            return True  # Collision with itself
        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            return True  # Collision with walls
        return False

    def draw_board(self):
        self.canvas.delete("all")
        for x, y in self.snake:
            self.canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill="green")
        food_x, food_y = self.food
        self.canvas.create_rectangle(food_x * CELL_SIZE, food_y * CELL_SIZE, (food_x + 1) * CELL_SIZE, (food_y + 1) * CELL_SIZE, fill="red")

    def flash_and_restart(self):
        self.running = False
        # Flash the canvas to indicate game over
        for _ in range(5):
            self.canvas.config(bg='red')
            self.root.update()
            time.sleep(0.1)
            self.canvas.config(bg='black')
            self.root.update()
            time.sleep(0.1)
        # Restart the game
        self.start_game()

    def run(self):
        while True:
            if not self.running:
                break

            self.ai_decide_direction()
            self.move_snake()

            if self.snake[0] == self.food:
                self.food = self.random_food_position()
            else:
                # Remove the tail to keep the snake the same length unless it eats food
                self.snake.pop()

            if self.check_collision():
                self.flash_and_restart()

            self.draw_board()
            self.root.update()
            time.sleep(INITIAL_DELAY / 1000.0)

if __name__ == "__main__":
    main()