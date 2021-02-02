import pygame
import sys
from pygame.locals import *

# RGB values
BG = (255, 255, 255)
BLACK = (0, 0, 0)

# how many pixels the character or bullet can move per frame
MOVEMENT_SPEED = 5
BULLET_SPEED = 10

# frames per second
FPS = 60

HEIGHT = 600
WIDTH = 800



def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()

    # Create clock object
    FPSCLOCK = pygame.time.Clock()
    # set up window
    DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
    pygame.display.set_caption("WASD to move. Space to Shoot")

    # load image and sound files from filepath strings
    player_img = pygame.image.load('player.png')
    laser_sound = pygame.mixer.Sound('laser-gun-19sf.mp3')

    # set initial position of player
    player_x = 10
    player_y = (.8 * HEIGHT)

    is_moving_left = False
    is_moving_right = False
    is_moving_up = False
    is_moving_down = False
    bullets = []

    # main game loop
    while True:
        DISPLAYSURF.fill(BG)

        # display player image at position
        DISPLAYSURF.blit(player_img, (player_x, player_y))

        if len(bullets) != 0:
            animate_bullets(bullets)

        # adjust player's position
        if is_moving_left:
            player_x -= MOVEMENT_SPEED
            if player_x <= 10:
                player_x = 10
        elif is_moving_right:
            player_x += MOVEMENT_SPEED
            if player_x >= WIDTH:
                player_x = WIDTH
        elif is_moving_up:
            player_y -= MOVEMENT_SPEED
            if player_y <= 10:
                player_y = 10
        elif is_moving_down:
            player_y += MOVEMENT_SPEED
            if player_y >= HEIGHT:
                player_y = HEIGHT


        # respond to user input events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_SPACE: # user presses spacebar
                create_bullet(player_x + 40, player_y - 15, bullets)
                # laser_sound.play()
            elif event.type == KEYDOWN and event.key == K_a: # presses A
                is_moving_left = True
            elif event.type == KEYUP and event.key == K_a: # releases A
                is_moving_left = False
            elif event.type == KEYDOWN and event.key == K_d: # presses D
                is_moving_right = True
            elif event.type == KEYUP and event.key == K_d: # releases d
                is_moving_right = False

            elif event.type == KEYUP and event.key == K_w:
                is_moving_up = False
            elif event.type == KEYDOWN and event.key == K_w:
                is_moving_up = True
            elif event.type == KEYUP and event.key == K_s:
                is_moving_down = False
            elif event.type == KEYDOWN and event.key == K_s:
                is_moving_down = True

            # add in ability to move up and down
        pygame.display.update()

        # increment clock. Call at very end of game loop, once per iteration
        FPSCLOCK.tick(FPS)


def create_bullet(x_position, y_position, bullets_list):
    # add bullet rectangle to the bullets list
    bullets_list.append(pygame.Rect(x_position, y_position, 10, 10))


def animate_bullets(bullets_list):
    # draw bullets and advance their position.
    for bullet in bullets_list:
        pygame.draw.rect(DISPLAYSURF, BLACK, bullet)
        bullet.centery -= BULLET_SPEED
        if bullet.centery <= 0:
            # remove bullet when it reaches the top of the screen
            del bullet


if __name__ == '__main__':
    main()
