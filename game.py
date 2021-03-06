import pygame
from pygame.locals import *
import sys
import random
from game_objects import *

class Game:
    # instance variables
    # On screen game objects
    ENEMIES = []
    PLAYER = None
    HEALTHMODULES = []
    # images to display for each of the different characters
    PLAYER_IMG = None
    ENEMY_IMG = None
    HEALTH_IMG = None

    DIFFICULTY = 0 # 0 for easy/default (to be implemented)
    SURF = None # the pygame surface that the game will be displayed on
    NUM_WAVES = 0 # TODO: implement this in the code!!!
    WIDTH = 0
    HEIGHT = 0

    MAX_HEALTH = 0
    HEALTH_FREQUENCY = 0

    HITBOXES = False

    def __init__(self, display_surface):
        self.SURF = display_surface
        self.WIDTH = self.SURF.get_size()[0]
        self.HEIGHT = self.SURF.get_size()[1]

    def toggle_hitbox_visibility(self):
        self.HITBOXES = not self.HITBOXES

    def set_player(self, player):
        self.PLAYER = player

    def set_difficulty(self, difficutly):
        self.DIFFICULTY = difficutly

    def reset_game(self):
        for enemy in self.ENEMIES:
            enemy.hitpoints = 0 # remove all enemies
        for health in self.HEALTHMODULES:
            health.hitpoints = 0 # remove all health modules
        # removing all enemies from the array removes all pointers to all enemies thus
        # also clearing their bullets if the Python garbage collection works similar to Java
        del self.ENEMIES[:]
        del self.HEALTHMODULES[:] # clear arrays of enemies, health modules, and bullets
        del self.PLAYER.bullets[:]
        self.NUM_WAVES = 0

    def spawn_health(self):
        speed = random.choice(range(4, 8))
        w = 50 + random.choice(range(self.WIDTH - 100)) # spawn the health so it is not partially off screen

        health = HealthModule(pygame.Rect(w, -80, 75, 75), self.SURF, self.HEALTH_IMG, speed) # the rectangle size needs to be adjusted
        health.is_moving_down = True

        self.HEALTHMODULES.append(health)

    # is wave is more accurately described as an 'if_wave' - it determines whether or not
    # a game tick will spawn a wave.
    def is_wave(self):
        if len(self.ENEMIES) < 3:
            return True
        return False

    def spawn_enemy(self):
        direction = random.choice(["diagonal", "down"])
        speed = random.choice(range(2, 8))
        # w is a point along the top of the screen; this is where the enemy will 'spawn' at
        w = random.choice(range(self.SURF.get_size()[0]))
        # the above line should be changed to be more consistent with the rest of the naming scheme

        # enemy spawns just off the top of the screen, so we don't see them pop into existence

        enemy = Enemy(pygame.Rect(w, -80, 100, 105), self.SURF, self.ENEMY_IMG, speed)
        enemy.is_moving_down = True
        # add left/right movement 1/2 of the time
        if direction == "diagonal":
            if w <= self.WIDTH / 2:
                # spawned on left half of screen
                enemy.is_moving_right = True
            else:
                # spawned on right side of screen
                enemy.is_moving_left = True
        self.ENEMIES.append(enemy)

    def spawn_enemy_wave(self):
        # .3 * number of prev waves - we want 1 more enemy for every 3 waves
        # player_score % 3 - this is a way to add randomness to the waves, while not being taxing on resources;
        #                    will spawn between 0 and 2 enemies
        # player_hp * .5 - we subtract this value, because as player health goes down, the number of enemy spawns goes up;
        #                  a penalty for taking damage
        # and lastly the + 3 ; this is so that we meet the 'wave' conditions
        num_of_enemies = int((.3 * self.NUM_WAVES) + (self.PLAYER.get_score() % 3) - (self.PLAYER.get_hitpoints() * .5) + 3)
        for i in range(num_of_enemies):
            self.spawn_enemy()
        self.NUM_WAVES += 1

    def get_all_bullets(self):
        list = self.PLAYER.bullets
        for enemy in self.ENEMIES:
            list += enemy.bullets
        return list

    def handle_bullet_collisions(self):
        for bullet in self.PLAYER.bullets: # player shot the bullet
            if self.handle_all_bullets(bullet):
                self.PLAYER.bullets.remove(bullet)
                continue
            for enemy in self.ENEMIES:
                if bullet.did_collide_with(enemy) and bullet.is_exploding is False:
                    # direct hit!
                    bullet.is_exploding = True
                    enemy.hitpoints -= 1
                    if enemy.hitpoints < 1:
                        self.ENEMIES.remove(enemy)
                        self.PLAYER.score_plus(1)
        for enemy in self.ENEMIES:
            for bullet in enemy.bullets: # enemy shot the bullet
                if self.handle_all_bullets(bullet):
                    enemy.bullets.remove(bullet)
                    continue
                if bullet.did_collide_with(self.PLAYER) and bullet.is_exploding is False:
                    bullet.is_exploding = True
                    self.PLAYER.hitpoints -= 1

    def handle_all_bullets(self, bullet): # return true when bullet needs to be removed
        x = bullet.rect.centerx
        y = bullet.rect.centery
        if y < 0 or y > self.HEIGHT or x < 0 or x > self.WIDTH:
            # remove bullet when it goes off screen
            return True
        for health in self.HEALTHMODULES:
            if bullet.did_collide_with(health) and bullet.is_exploding is False:
                bullet.is_exploding = True
                health.hitpoints -= 1
                self.HEALTHMODULES.remove(health)
        return bullet.is_finished_exploding

    def handle_enemy_collisions(self):
        for enemy in self.ENEMIES:
            if enemy.did_collide_with(self.PLAYER):
                self.PLAYER.hitpoints -= 1
                self.ENEMIES.remove(enemy)
            if enemy.rect.centery > self.HEIGHT:
                # enemy went off bottom of screen
                self.ENEMIES.remove(enemy)
                self.PLAYER.score_minus(1)
            for other_enemy in self.ENEMIES:
                enemy.bounce_off(other_enemy)

    def handle_health_collisions(self):
        for health in self.HEALTHMODULES:
            if health.did_collide_with(self.PLAYER):
                if self.PLAYER.hitpoints < self.MAX_HEALTH:
                    self.PLAYER.hitpoints += 1
                else:
                    self.PLAYER.score_plus(5)
                self.HEALTHMODULES.remove(health)
            if health.rect.centery > self.HEIGHT:
                # health went off bottom of screen
                self.HEALTHMODULES.remove(health)

    def animate(self):
        self.PLAYER.animate()
        for b in self.get_all_bullets():
            b.animate()
        for e in self.ENEMIES:
            e.animate()
        for h in self.HEALTHMODULES:
            h.animate()

    def draw_hitboxes(self):
        self.PLAYER.draw_hitbox(self.SURF)
        for e in self.ENEMIES:
            e.draw_hitbox(self.SURF)
        for h in self.HEALTHMODULES:
            h.draw_hitbox(self.SURF)

    # gets the pertinent info from the config file
    def configure(self, yamlconfig, path):
        self.NUM_WAVES = yamlconfig['waves']
        self.HEALTH_FREQUENCY = yamlconfig['health']
        self.MAX_HEALTH = yamlconfig['maxhealth']
        assets = yamlconfig['assets']

        self.PLAYER_IMG = pygame.image.load(path + assets['player'])
        self.ENEMY_IMG = pygame.image.load(path + assets['enemy'])
        self.HEALTH_IMG = pygame.image.load(path + assets['health'])


if __name__ == "__main__":
    main()
