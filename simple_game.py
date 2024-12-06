import tkinter as tk
import random
import time
import pygame  # To play background music

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Dodge the Falling Blocks")
        self.root.resizable(False, False)

        # Initialize pygame for sound
        pygame.mixer.init()
        self.bg_music = pygame.mixer.Sound("assets/funnysong.mp3")  # Replace with your own file
        self.bg_music.set_volume(0.2)  # Set initial volume (soft background music)
        self.bg_music.play(loops=-1, maxtime=0, fade_ms=3000)  # Play music in loop with fade-in effect

        # Set up the canvas
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='black')
        self.canvas.pack()

        # Create player object (rectangle)
        self.player = self.canvas.create_rectangle(180, 350, 220, 370, fill="blue")

        # Set up the player's speed and other game attributes
        self.player_speed = 20
        self.lives = 3
        self.score = 0
        self.block_speed = 5
        self.block_spawn_rate = 0.05
        self.difficulty_increase_interval = 5
        self.last_difficulty_increase = time.time()

        # High Score
        self.high_score = 0

        # Score and Lives Text
        self.score_text = self.canvas.create_text(10, 10, anchor="nw", text="Score: 0", fill="white", font=('Helvetica', 12))
        self.lives_text = self.canvas.create_text(350, 10, anchor="ne", text="Lives: 3", fill="white", font=('Helvetica', 12))

        # Game Over and Retry button
        self.game_over_text = None
        self.retry_button = None

        # Blocks and power-ups
        self.blocks = []
        self.power_ups = []
        self.shield_active = False  # Whether the player is in shield mode
        self.speed_boost_active = False  # Whether the speed boost is active
        self.score_multiplier_active = False  # Whether score multiplier is active
        self.multiplier_duration = 0  # Duration for the score multiplier

        # Key bindings for movement
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

        # Mouse control
        self.canvas.bind("<Motion>", self.mouse_move)

        # Start the game loop
        self.update()

    def move_left(self, event):
        """Move the player left with keyboard."""
        self.canvas.move(self.player, -self.player_speed, 0)

    def move_right(self, event):
        """Move the player right with keyboard."""
        self.canvas.move(self.player, self.player_speed, 0)

    def mouse_move(self, event):
        """Move the player with the mouse."""
        x = event.x
        if 0 <= x <= 380:  # Keep the player within bounds
            self.canvas.coords(self.player, x - 20, 350, x + 20, 370)

    def create_block(self):
        """Create a new falling block."""
        x_pos = random.randint(0, 380)
        block_width = random.randint(15, 30)  # Randomize block width for variety
        block = self.canvas.create_rectangle(x_pos, 0, x_pos + block_width, 20, fill="red")
        self.blocks.append(block)

    def create_power_up(self):
        """Create a power-up that the player can collect."""
        x_pos = random.randint(0, 380)
        power_up_type = random.choice(["shield", "speed", "multiplier"])  # Randomize power-up type
        if power_up_type == "shield":
            power_up = self.canvas.create_oval(x_pos, 0, x_pos + 15, 15, fill="cyan")
        elif power_up_type == "speed":
            power_up = self.canvas.create_oval(x_pos, 0, x_pos + 15, 15, fill="green")
        elif power_up_type == "multiplier":
            power_up = self.canvas.create_oval(x_pos, 0, x_pos + 15, 15, fill="yellow")
        self.power_ups.append((power_up, power_up_type))

    def update(self):
        """Update the game state and redraw the screen."""
        if self.game_over_text:
            return  # If game over, stop the update loop

        # Check for collisions, move blocks, and spawn new blocks
        self.move_blocks()
        self.check_collisions()
        self.create_block_if_needed()
        self.create_power_up_if_needed()

        # Increase difficulty over time
        self.increase_difficulty()

        # Update the score and lives
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")

        # After 50ms, call the update function again
        self.root.after(50, self.update)

    def move_blocks(self):
        """Move each block down the screen."""
        for block in self.blocks:
            self.canvas.move(block, 0, self.block_speed)

        # Move power-ups
        for power_up, _ in self.power_ups:
            self.canvas.move(power_up, 0, self.block_speed)

    def create_block_if_needed(self):
        """Create new blocks at random intervals."""
        if random.random() < self.block_spawn_rate:
            self.create_block()

    def create_power_up_if_needed(self):
        """Create new power-ups at random intervals."""
        if random.random() < 0.01:  # Power-up spawn rate
            self.create_power_up()

    def check_collisions(self):
        """Check if the player collides with any blocks."""
        player_coords = self.canvas.coords(self.player)

        # Check block collisions
        for block in self.blocks:
            block_coords = self.canvas.coords(block)
            # Check for overlap between the player and the block
            if (player_coords[0] < block_coords[2] and
                    player_coords[2] > block_coords[0] and
                    player_coords[1] < block_coords[3] and
                    player_coords[3] > block_coords[1]):
                if not self.shield_active:  # If shield is not active, lose life
                    self.lives -= 1
                    if self.lives == 0:
                        self.game_over()
                # After collision, delete block
                self.canvas.delete(block)
                self.blocks.remove(block)
                break  # Break after detecting the first collision

        # Check power-up collection
        for power_up, power_up_type in self.power_ups:
            power_up_coords = self.canvas.coords(power_up)
            if (player_coords[0] < power_up_coords[2] and
                    player_coords[2] > power_up_coords[0] and
                    player_coords[1] < power_up_coords[3] and
                    player_coords[3] > power_up_coords[1]):
                if power_up_type == "shield":
                    self.shield_active = True  # Activate shield
                    self.canvas.delete(power_up)
                elif power_up_type == "speed":
                    self.speed_boost_active = True  # Activate speed boost
                    self.player_speed = 30  # Speed up player
                    self.canvas.delete(power_up)
                elif power_up_type == "multiplier":
                    self.score_multiplier_active = True  # Activate score multiplier
                    self.multiplier_duration = 5  # Duration for multiplier
                    self.canvas.delete(power_up)

                self.power_ups.remove((power_up, power_up_type))

        # Apply multiplier effect
        if self.score_multiplier_active:
            self.multiplier_duration -= 1
            if self.multiplier_duration <= 0:
                self.score_multiplier_active = False

        # Increase score if player avoids blocks
        self.score += 1
        if self.score_multiplier_active:
            self.score *= 2  # Double the score if multiplier is active

    def game_over(self):
        """End the game."""
        if self.score > self.high_score:
            self.high_score = self.score  # Update high score

        # Display Game Over message
        self.game_over_text = self.canvas.create_text(200, 200, text="Game Over", fill="white", font=('Helvetica', 24))

        # Display High Score
        self.canvas.create_text(200, 230, text=f"High Score: {self.high_score}", fill="white", font=('Helvetica', 16))

        # Create Retry button
        self.retry_button = tk.Button(self.root, text="Retry", command=self.retry_game)
        self.retry_button.pack()

    def retry_game(self):
        """Reset the game state."""
        self.canvas.delete("all")  # Clear canvas
        self.__init__(self.root)  # Re-initialize the game

    def increase_difficulty(self):
        """Gradually increase the game's difficulty."""
        current_time = time.time()
        if current_time - self.last_difficulty_increase >= self.difficulty_increase_interval:
            # Increase block speed and spawn rate
            self.block_speed += 1
            self.block_spawn_rate += 0.02
            self.last_difficulty_increase = current_time

            # Make the music more intense as the game progresses
            if self.block_speed > 10:
                self.bg_music.set_volume(0.5)  # Increase volume
                self.bg_music.play(loops=-1, maxtime=0, fade_ms=3000)

            # Introduce new block types or effects after reaching certain scores
            if self.score > 500 and self.score <= 1000:
                # Add new block types for the next stage
                pass
            elif self.score > 1000:
                # Even more difficult blocks or power-ups
                pass

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
