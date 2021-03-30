#!/usr/bin/python3.9

import pygame
import sys
from pygame.locals import *
from acm_game import *
from pathlib import Path
import random
import pygame.freetype
import yaml
from game import Game

pygame.init()

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 600

DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)

# Absolute path of the folder that contains this file.
PATH = str(Path(__file__).parent.absolute()) + "/"

# load image and sound files from filepath strings, also load data
def loadconfig():
    global BG, BLACK, FPS, SCOREBOARD_FONT, BACKGROUND_IMG, TITLE_IMG, GAMEOVER_IMG, LASER_SOUND, hit, music, data

    # Open and close the config file safely.
    with open(PATH + 'config.yaml', 'r') as file:
        config = yaml.safe_load(file)

        # RGB values
        BG = config['bg']
        BLACK = config['black']

        # frames per second
        FPS = config['fps']

        SCOREBOARD_FONT = pygame.freetype.SysFont(config['font']['style'], config['font']['size'], bold=True)

        assets = config['assets']

        BACKGROUND_IMG = pygame.image.load(PATH + assets['background'])
        TITLE_IMG = pygame.image.load(PATH + assets['title'])
        GAMEOVER_IMG = pygame.image.load(PATH + assets['gameover'])
        LASER_SOUND = pygame.mixer.Sound(PATH + assets['laser'])
        #hit = pygame.mixer.Sound(PATH + assets['hit'])
        #music = pygame.mixer.music.load(PATH + assets['music']) TODO: Not added yet

        LASER_SOUND.set_volume(config['volume']/100)

    # Load data file from long term storage
    if Path(PATH + 'data.yaml').is_file():
        with open(PATH + 'data.yaml', 'r') as file:
            data = yaml.safe_load(file)
    else:
        # Default Data:
        data = {}
        data['high_score'] = 0;

# Save all scores in data[] to data.yaml
def save_data():
    with open(PATH + 'data.yaml', 'w') as file:
        yaml.dump(data, file)

# Current TODO:
# - have the player angle impact the distance travelled
# - use the current mouse position to set the player angle

def gameover():
    scroll = 0
    finished = False

    new_highscore = False

    if data['high_score'] < GAME.PLAYER.get_score():
        data['high_score'] = GAME.PLAYER.get_score()
        save_data()
        print(f"New High Score of: {GAME.PLAYER.get_score()}!")
        new_highscore = True

    while (not finished):
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT

        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(GAMEOVER_IMG, (0,0))

        if new_highscore:
            SCOREBOARD_FONT.render_to(DISPLAYSURF, (60, WINDOW_HEIGHT/2), f'New Highscore! {GAME.PLAYER.get_score()}', (255,255,255))

        for event in pygame.event.get():
            if event.type == QUIT: # quit game if user presses close on welcome screen
                pygame.quit()
                sys.exit()
        pygame.display.flip()


def scrollY(screenSurf, offsetY):
    width, height = screenSurf.get_size()
    copySurf = screenSurf.copy()
    screenSurf.blit(copySurf, (0, offsetY))
    if offsetY < 0:
        screenSurf.blit(copySurf, (0, height + offsetY), (0, 0, width, -offsetY))
    else:
        screenSurf.blit(copySurf, (0, 0), (0, height - offsetY, width, offsetY))

def game():
    global GAME
    pygame.init()

    # Create clock object
    FPSCLOCK = pygame.time.Clock()
    # set up window
    pygame.display.set_caption("WASD to move. Space to Shoot")

    GAMESURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    GAME = Game(GAMESURF)
    with open(PATH + 'config.yaml', 'r') as file:
        GAME.configure(yaml.safe_load(file), PATH)
    # create player object with initial location. Size is approximate based on image file
    player = Player(pygame.Rect(.4 * GAME.WIDTH, .66 * GAME.HEIGHT, 100, 130), GAME.SURF, GAME.PLAYER_IMG)
    GAME.set_player(player)
    GAME.set_difficulty(0) # effectively 'easy'

    #showhitboxes = False

    scroll = 0  #scrolling
    # main game loop
    while GAME.PLAYER.isAlive():
        # Current Order:
        # - fill backround
        # - handle scrolling
        # - start a wave if we need to
        # - animate player
        # - animate bullets
        #   - animate enemies
        #       - determine if enimies go off screen; remove if they do
        #       - determine if there are any collisions; remove hp if there are any; also remove enemy
        #       - check if hp is 0; if so, end game
        # - check for user events
        # - update display
        # - update the clock

        # set background color
        GAME.SURF.blit(BACKGROUND_IMG, (0,0))
        scrollY(GAME.SURF, scroll)
        scroll = (scroll + 2)%GAME.HEIGHT
        # create a player surface, and rotate the player image the appropriate number of degrees
        # player_angle = 0
        # PLAYER_SURF = pygame.transform.rotate(player_img, player_angle)
        # display player image at position
        # DISPLAYSURF.blit(PLAYER_SURF, (player_x, player_y))

        # admittedly this line is a bit hacky; when printing out the value of 'FPSCLOCK.get_time()'
        # prints only 16s, so my original thought was wrong in how it worked. So this line is really
        # just a temporary workaround for a real solution in the future.
        if FPSCLOCK.get_time() % 16 == 0:
            # check if we start a wave
            if GAME.is_wave():
                print(f"Spawning Enemy Wave: {GAME.NUM_WAVES}")
                GAME.spawn_enemy_wave()

                if GAME.NUM_WAVES % GAME.HEALTH_FREQUENCY == 0:
                    GAME.spawn_health()


        #if showhitboxes:
        #    pygame.draw.rect(GAME.SURF, (0, 255, 0), GAME.PLAYER.rect)

        GAME.handle_bullet_collisions()

        GAME.handle_health_collisions()

        GAME.handle_enemy_collisions()

        if not GAME.PLAYER.isAlive():
            pass

        GAME.animate()

        # respond to user input events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key == K_SPACE):  # presses mouse button or press space
                mouse_x, mouse_y = pygame.mouse.get_pos()
                GAME.PLAYER.shoot(mouse_x, mouse_y, GAME.BULLETS)
                LASER_SOUND.play()
            elif event.type == KEYDOWN and event.key == K_a:  # presses A
                GAME.PLAYER.is_moving_left = True
            elif event.type == KEYUP and event.key == K_a:  # releases A
                GAME.PLAYER.is_moving_left = False
            elif event.type == KEYDOWN and event.key == K_d:  # presses D
                GAME.PLAYER.is_moving_right = True
            elif event.type == KEYUP and event.key == K_d:  # releases d
                GAME.PLAYER.is_moving_right = False
                # below is to move player forward and backward, same logic as above
            elif event.type == KEYUP and event.key == K_w:
                GAME.PLAYER.is_moving_up = False
            elif event.type == KEYDOWN and event.key == K_w:
                GAME.PLAYER.is_moving_up = True
            elif event.type == KEYUP and event.key == K_s:
                GAME.PLAYER.is_moving_down = False
            elif event.type == KEYDOWN and event.key == K_s:
                GAME.PLAYER.is_moving_down = True
            # temporary testing line
            #elif event.type == KEYDOWN and event.key == K_e:
            #    spawn_enemy()
            #elif event.type == KEYDOWN and event.key == K_h:
            #    spawn_health()
            #elif event.type == KEYDOWN and event.key == K_b:
            #    showhitboxes = not showhitboxes

        SCOREBOARD_FONT.render_to(GAME.SURF, (30, 30), str(GAME.PLAYER.get_score()), (255,255,255))
        SCOREBOARD_FONT.render_to(GAME.SURF, (30, 100), str(GAME.PLAYER.hitpoints), (255, 0, 0))
        SCOREBOARD_FONT.render_to(GAME.SURF, (GAME.WIDTH * .6, 30), "Best: " + str(data['high_score']), (255,255,0))

        # I dont think we need both flip() and update(). I think they do the same thing when you call with no arguments
        pygame.display.flip()
        pygame.display.update()

        # increment clock. Call at very end of game loop, once per iteration
        FPSCLOCK.tick(FPS)


def welcome():
    load_game = False
    scroll = 0
    while (not load_game):
        DISPLAYSURF.blit(BACKGROUND_IMG, (0,0))
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT
        DISPLAYSURF.blit(TITLE_IMG, (0,0))
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                load_game = True

        if event.type == QUIT: # quit game if user presses close on welcome screen
            pygame.quit()
            sys.exit()
        pygame.display.flip()


def main():
    loadconfig()
    welcome()
    game()
    gameover()


if __name__ == "__main__":
    main()
