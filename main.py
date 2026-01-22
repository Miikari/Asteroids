import pygame
import sys
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_state, log_event


def main():
    pygame.init()
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
                sys.exit()
            
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