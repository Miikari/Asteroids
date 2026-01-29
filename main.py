import pygame
import sys
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_state, log_event
import sqlite3

DB_FILE = "highscores.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        with open("schema.sql") as s:
            conn.executescript(s.read())

def add_score(player_name: str, score: int):
    if score < 0:
        raise ValueError("Score cannot be negative")

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO highscores (player_name, score) VALUES (?, ?)",
            (player_name, score)
        )


def get_top_scores(limit=10):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("""
            SELECT player_name, score, created_at
            FROM highscores
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

def check_score(player):
    add_score("Miika", player.kc)

def show_leaderboard():
    screen = pygame.display.get_surface()
    font = pygame.font.SysFont(None, 40)

    scores = get_top_scores()

    waiting = True
    while waiting:
        screen.fill("black")

        title = font.render("Leaderboard", True, (255,255,0))
        screen.blit(title, (50, 50))

        for i, (name, score, _) in enumerate(scores):
            line = font.render(f"{i+1}. {name} - {score}", True, (255,255,255))
            screen.blit(line, (50, 120 + i*40))

        hint = font.render("Press ENTER to continue", True, (150,150,150))
        screen.blit(hint, (50, SCREEN_HEIGHT - 80))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

def main():
    pygame.init()
    init_db()

    top = get_top_scores()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    
    Player.containers = (updatable, drawable) 
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)

    player = Player(x, y)
    asteroidfield = AsteroidField()

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    

    thresholds = [
    {"kc": 5, "player_inc": 0.2, "asteroid_inc": (45, 110)},
    {"kc": 10, "player_inc": 0.15, "asteroid_inc": (50, 120)},
    {"kc": 15, "player_inc": 0.1, "asteroid_inc": (55, 130)},
    ]
    #Gameplay looppi
    while True:
        log_state()

        if player.kc > 5:
            player.add_intensity(0.2)
            asteroidfield.add_intensity(45, 110)
        if player.kc > 10:
            player.add_intensity(0.15)
            asteroidfield.add_intensity(50, 120)
        if player.kc > 15:
            player.add_intensity(0.1)
            asteroidfield.add_intensity(55, 130)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
        #Framerate = 140FPS
        dt = clock.tick(140) / 1000
        updatable.update(dt)

        for asteroid in asteroids:
            if asteroid.collides_with(player):
                log_event("player hit")
                print("Game over!")
                check_score(player)
                show_leaderboard()
                pygame.quit()
                main()
                
            
            for shot in shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    asteroid.split()
                    player.kc_add()

        for t in thresholds:
            if player.kc > t["kc"]:
                player.add_intensity(t["player_inc"])
                asteroidfield.add_intensity(*t["asteroid_inc"])
                
        screen.fill("black")
        
        for d in drawable:
            d.draw(screen)
        
        pygame.font.init()
        font = pygame.font.SysFont(pygame.font.get_default_font(), 30)
        kc_text = font.render("Asteroids destroyed: " + str(player.kc), True, (255, 255, 255))
        kc_text_rect = kc_text.get_rect()
        kc_text_rect.topleft = (30,30)

        screen.blit(kc_text, kc_text_rect)
        pygame.display.flip() #NEEDS TO BE LAST!!

if __name__ == "__main__":
    main()