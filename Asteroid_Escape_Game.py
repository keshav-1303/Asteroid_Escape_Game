import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 40
ASTEROID_SIZE = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
FPS = 60

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Dodge")
clock = pygame.time.Clock()

# Initialize font
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 8
        self.color = BLUE
        
    def draw(self):
        # Draw spaceship triangle
        ship_points = [
            (self.x + self.width // 2, self.y),  # top
            (self.x, self.y + self.height),  # bottom left
            (self.x + self.width, self.y + self.height)  # bottom right
        ]
        pygame.draw.polygon(screen, self.color, ship_points)
        
        # Draw thruster flame
        flame_points = [
            (self.x + self.width // 2 - 10, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height + 15),
            (self.x + self.width // 2 + 10, self.y + self.height)
        ]
        pygame.draw.polygon(screen, YELLOW, flame_points)
        
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed
        if direction == "up" and self.y > 0:
            self.y -= self.speed
        if direction == "down" and self.y < HEIGHT - self.height:
            self.y += self.speed
            
    def get_rect(self):
        # Create a smaller hitbox for better gameplay
        hitbox_reduction = 10
        return pygame.Rect(
            self.x + hitbox_reduction, 
            self.y + hitbox_reduction, 
            self.width - 2 * hitbox_reduction, 
            self.height - 2 * hitbox_reduction
        )

class Asteroid:
    def __init__(self):
        self.width = ASTEROID_SIZE
        self.height = ASTEROID_SIZE
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.speed = random.uniform(3, 7)
        self.color = RED
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)
        
    def draw(self):
        # Draw asteroid as irregular polygon
        asteroid_points = []
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        for i in range(8):
            angle = self.rotation + i * (360 / 8)
            radius = random.uniform(self.width // 2 - 5, self.width // 2 + 5)
            x = center_x + radius * pygame.math.Vector2(1, 0).rotate(angle).x
            y = center_y + radius * pygame.math.Vector2(1, 0).rotate(angle).y
            asteroid_points.append((x, y))
            
        pygame.draw.polygon(screen, self.color, asteroid_points)
        
    def move(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        
    def is_off_screen(self):
        return self.y > HEIGHT
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def game_over_screen(score):
    screen.fill(BLACK)
    
    game_over_text = font.render("GAME OVER", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to play again", True, WHITE)
    quit_text = font.render("Press ESC to quit", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 80))
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)
    
    return False

def draw_stars(stars):
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])

def main():
    # Create player
    player = Player()
    
    # Create asteroids list
    asteroids = []
    
    # Create stars for background
    stars = []
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        stars.append((x, y, size))
    
    # Game variables
    score = 0
    asteroid_spawn_timer = 0
    asteroid_spawn_delay = 50  # Lower values = more asteroids
    running = True
    
    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Get key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")
        if keys[pygame.K_UP]:
            player.move("up")
        if keys[pygame.K_DOWN]:
            player.move("down")
        if keys[pygame.K_ESCAPE]:
            running = False
            
        # Update game state
        # Spawn asteroids
        asteroid_spawn_timer += 1
        if asteroid_spawn_timer >= asteroid_spawn_delay:
            asteroids.append(Asteroid())
            asteroid_spawn_timer = 0
            # Make game harder over time
            if asteroid_spawn_delay > 20:
                asteroid_spawn_delay -= 0.2
                
        # Move asteroids
        for asteroid in asteroids[:]:
            asteroid.move()
            if asteroid.is_off_screen():
                asteroids.remove(asteroid)
                score += 1
                
        # Check for collisions
        player_rect = player.get_rect()
        for asteroid in asteroids:
            if player_rect.colliderect(asteroid.get_rect()):
                # Game over!
                if game_over_screen(score):
                    # Restart game
                    return main()
                else:
                    running = False
                    break
                
        # Draw everything
        screen.fill(BLACK)
        
        # Draw stars
        draw_stars(stars)
        
        # Draw player
        player.draw()
        
        # Draw asteroids
        for asteroid in asteroids:
            asteroid.draw()
            
        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Update display
        pygame.display.update()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    