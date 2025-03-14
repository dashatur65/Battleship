import pygame
import random

GRID_SIZE = 10
CELL_SIZE = 40
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60
SHIP_SIZES = [5, 4, 3, 3, 2]

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)
LIGHT_RED = (255, 102, 102)
YELLOW = (255, 255, 0)

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.shots = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def place_ship(self, x, y, size, horizontal):
        if horizontal:
            if x + size > GRID_SIZE:
                return False
            for i in range(size):
                if self.grid[x + i][y] != 0:
                    return False
            for i in range(size):
                self.grid[x + i][y] = 1
        else:
            if y + size > GRID_SIZE:
                return False
            for i in range(size):
                if self.grid[x][y + i] != 0:
                    return False
            for i in range(size):
                self.grid[x][y + i] = 1
        return True

    def randomize_ships(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for size in SHIP_SIZES:
            placed = False
            while not placed:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                horizontal = random.choice([True, False])
                placed = self.place_ship(x, y, size, horizontal)

    def shoot(self, x, y):
        if self.shots[x][y]:
            return False
        self.shots[x][y] = True
        return self.grid[x][y] == 1

    def all_ships_sunk(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if self.grid[x][y] == 1 and not self.shots[x][y]:
                    return False
        return True

class Bot:
    def __init__(self):
        self.available_moves = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
        random.shuffle(self.available_moves)

    def shoot(self, board):
        x, y = self.available_moves.pop()
        hit = board.shoot(x, y)
        return x, y, hit

class BattleshipGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Battleship")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.player_board = Board()
        self.bot_board = Board()
        self.bot = Bot()

        self.player_board.randomize_ships()
        self.bot_board.randomize_ships()

        self.player_hits = 0
        self.bot_hits = 0

        self.current_turn = "player"
        self.game_over = False
        self.winner = None

        self.player_move_log = ""
        self.bot_move_log = ""

        self.shuffle_button_rect = pygame.Rect(50, 550, 120, 30)
        self.select_button_rect = pygame.Rect(200, 550, 120, 30)
        self.quit_button_rect = pygame.Rect(400, 550, 120, 30)
        self.restart_button_rect = pygame.Rect(600, 550, 120, 30)
        self.ships_selected = False

        print("Welcome to Battleship!")
        print("Instructions:")
        print("1. Place your ships by clicking 'Shuffle' until you are satisfied.")
        print("2. Click 'Select' to start the game.")
        print("3. Attack the bot's board (right grid) by clicking on cells.")
        print("4. The bot will attack your board (left grid) automatically.")
        print("5. The first to sink all ships wins!")
        print("Good luck!")

    def draw_board(self, board, x_offset, y_offset, show_ships=False):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x_offset + x * CELL_SIZE, y_offset + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                # Draw the base cell colours first
                if board.shots[x][y]:
                    colour = RED if board.grid[x][y] == 1 else BLUE
                    pygame.draw.rect(self.screen, colour, rect)
                else:
                    colour = GRAY
                    pygame.draw.rect(self.screen, colour, rect)

                # Draw ship squares 
                if show_ships and board.grid[x][y] == 1:
                    pygame.draw.rect(self.screen, RED, rect.inflate(-10, -10))

                # Draw the grid border
                pygame.draw.rect(self.screen, BLACK, rect, 1)

                # Draw the "X" on top for hits (only when shots have been fired)
                if board.shots[x][y] and board.grid[x][y] == 1:  # Hit
                    pygame.draw.line(self.screen, YELLOW, rect.topleft, rect.bottomright, 4)
                    pygame.draw.line(self.screen, YELLOW, rect.bottomleft, rect.topright, 4)

    def draw_buttons(self):
        if not self.ships_selected:
            pygame.draw.rect(self.screen, GREEN, self.shuffle_button_rect)
            shuffle_text = self.font.render("Shuffle", True, BLACK)
            self.screen.blit(shuffle_text, (self.shuffle_button_rect.x + 10, self.shuffle_button_rect.y + 5))

            pygame.draw.rect(self.screen, LIGHT_RED, self.select_button_rect)
            select_text = self.font.render("Select", True, BLACK)
            self.screen.blit(select_text, (self.select_button_rect.x + 15, self.select_button_rect.y + 5))
        else:
            pygame.draw.rect(self.screen, LIGHT_RED, self.quit_button_rect)
            quit_text = self.font.render("Quit", True, BLACK)
            self.screen.blit(quit_text, (self.quit_button_rect.x + 15, self.quit_button_rect.y + 5))

            pygame.draw.rect(self.screen, GREEN, self.restart_button_rect)
            restart_text = self.font.render("Restart", True, BLACK)
            self.screen.blit(restart_text, (self.restart_button_rect.x + 15, self.restart_button_rect.y + 5))

    def draw_game(self):
        self.screen.fill(WHITE)

        # Draw Boards
        self.draw_board(self.player_board, 100, 50, show_ships=True)
        self.draw_board(self.bot_board, 540, 50)

        # Draw Buttons
        self.draw_buttons()

        # Draw Information
        text_score = self.font.render(f"Player Hits: {self.player_hits} | Bot Hits: {self.bot_hits}", True, BLACK)
        self.screen.blit(text_score, (50, 10))

        if self.game_over:
            game_over_text = self.font.render(f"Game Over! Winner: {self.winner}", True, BLACK)
            self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 500))

        pygame.display.flip()

    def restart_game(self):
        self.__init__()
        self.run()

    def game_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    if self.shuffle_button_rect.collidepoint(x, y) and not self.ships_selected:
                        self.player_board.randomize_ships()

                    if self.select_button_rect.collidepoint(x, y) and not self.ships_selected:
                        self.ships_selected = True

                    if self.ships_selected and self.quit_button_rect.collidepoint(x, y):
                        pygame.quit()
                        return

                    if self.ships_selected and self.restart_button_rect.collidepoint(x, y):
                        self.restart_game()

                    if self.ships_selected and self.current_turn == "player" and not self.game_over:
                        grid_x, grid_y = (x - 540) // CELL_SIZE, (y - 50) // CELL_SIZE
                        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                            if not self.bot_board.shots[grid_x][grid_y]:
                                hit = self.bot_board.shoot(grid_x, grid_y)
                                self.player_hits += hit
                                if self.bot_board.all_ships_sunk():
                                    self.game_over = True
                                    self.winner = "Player"
                                self.current_turn = "bot"

            if not self.game_over and self.current_turn == "bot":
                bot_x, bot_y, bot_hit = self.bot.shoot(self.player_board)
                self.bot_hits += bot_hit
                if self.player_board.all_ships_sunk():
                    self.game_over = True
                    self.winner = "Bot"
                self.current_turn = "player"

            self.draw_game()
            self.clock.tick(FPS)

    def run(self):
        self.game_loop()

if __name__ == "__main__":
    game = BattleshipGame()
    game.run()
