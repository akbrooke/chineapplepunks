# coding=utf-8

# imports the Pygame library
import os
import random
import pygame

# variables
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCORE = 0
FPS=60
ALIEN_SPEED = 2

main_dir = os.path.split(os.path.abspath(__file__))[0]

# The basic alien class. Has two animation frames.
# Update function just cycles between these two frames.
class Alien(pygame.sprite.Sprite):
    speed = 5
    destroyed = False
    images = [ None, None ]
    
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images[0] = load_image('alien1_1.png')
        self.images[1] = load_image('alien1_2.png')
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = position)

    def update(self):
        if self.destroyed == True:
            self.kill()
            return
        if self.speed == 0:
            self.speed = 5
            if self.image == self.images[0]:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
        self.speed = self.speed - 1

# Writes out the score.
class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 36)
        self.color = pygame.Color('white')
        self.update()
        self.rect = self.image.get_rect().move(10, 10)

    def update(self):
        msg = "Score: %d" % SCORE
        self.image = self.font.render(msg, 0, self.color)

# This class does all the work regarding the aliens.
class AlienController():
    aliens = []
    bomb_time = 0
    direction = 1
    count = 0
    down_flag = False
    
    def __init__(self):
        self.bomb_time = random.choice([20,60])
        # Create the aliens in a grid arrangement.
        # Basically it's a list of columns.
        for x in range(6):
            col = []
            for y in range(0,8,2):
                alien = Alien([(84*x) + 84, (y*20)+80])
                col.append(alien)
                self.count += 1
            self.aliens.append(col)
    
    # At a random time, randomly select an alien from the bottom row.
    # And make it drop a bomb.
    def create_bomb(self):
        if self.bomb_time == 0:
            col = []
            while not col:
                col = random.choice(self.aliens)
            # Cool python magic. Negative indexes work from back to
            # front in a list. So -1 gets the last element. In this
            # case, the first alien in the column.
            alien = col[-1]
            Bomb(alien.rect.midbottom)
            self.bomb_time = random.choice([20,60])
        self.bomb_time -= 1

    # Advances the aliens toward the player. Power move.
    def move_down(self):
        for x in range(6):
            col = self.aliens[x]
            for y in col:
                alien = y
                alien.rect.move_ip (0,ALIEN_SPEED)

    # Moves all the aliens right.
    def move_right(self):
        for x in range(6):
            col = self.aliens[x]
            for y in col:
                alien = y
                alien.rect.move_ip(ALIEN_SPEED, 0)
                if alien.rect.right > 600:
                    self.down_flag = True
                    self.direction = -1

    # Moves all the aliens left.
    def move_left(self):
        for x in range(6):
            col = self.aliens[x]
            for y in col:
                alien = y
                alien.rect.move_ip(-ALIEN_SPEED, 0)
                if alien.rect.left < 40:
                    self.down_flag = True
                    self.direction = 1

    # Moves the aliens either left, right or down
    # depending on conditions. If the aliens are too far
    # left or right, they will advance down the screen and
    # change direction.
    def update(self):
        if self.down_flag == True:
            self.move_down()
            self.down_flag = False
        if self.direction == 1:
            self.move_right()
        else:
            self.move_left()
        self.create_bomb()

    # Removes an alien from the controller. 
    def remove(self,alien):
        for x in range(6):
            col = self.aliens[x]
            try:
                col.remove(alien)
                self.count -= 1
                break
            except ValueError:
                pass

# The player's bullet.
class Bullet(pygame.sprite.Sprite):
    velocity = -2
    hole = None
    
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image('bullet.png')
        self.rect = self.image.get_rect(midbottom=position)
        self.hole = load_image('hole.png')

    # Make bullet go up.
    def update(self):
        self.rect.move_ip(0, self.velocity)
        if self.rect.top <= 0:
            self.kill()

    # Check to see if the bullet has collided with the shields.
    # If so, delete the bullet and stick a hole in the shield.
    def check_collision(self,surface):
        pix_array = pygame.PixelArray(surface)
        if pix_array[self.rect.center] != surface.map_rgb((0,0,0)):
            pix_array.close()
            surface.blit(self.hole, self.rect)
            self.kill()

# The Alien's bomb. Does the same thing as the Bullet class,
# only they move down the screen.
class Bomb(pygame.sprite.Sprite):
    velocity = 2
    hole = None
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image('bullet.png')
        self.rect = self.image.get_rect(midbottom=position)
        self.hole = load_image('hole.png')
        
    def update(self):
        self.rect.move_ip(0, self.velocity)
        if self.rect.bottom >= 480:
            self.kill()

    def check_collision(self,surface):
        pix_array = pygame.PixelArray(surface)
        if pix_array[self.rect.center] != surface.map_rgb((0,0,0)):
            pix_array.close()
            surface.blit(self.hole, self.rect)
            self.kill()

# The Player's ship. Moves left and right. Exciting.
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('ship.png')
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, 437)
        self.x_vel = 0
        self.reloading = 0;
        
    def update(self):
        self.x_vel = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.x_vel = -1
        if keystate[pygame.K_RIGHT]:
            self.x_vel = 1
        self.rect.x += self.x_vel

# Function that loads an image from a file and magically
# converts it a format our game can use.
def load_image(file):
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %
                        (file, pygame.get_error()))
    return surface.convert_alpha()

# Function draws the shields.
def draw_shields(surface, image):
    for x in range(0,8,2):
        surface.blit(image, ((64*x) + 96, 340))

def main():
    global SCORE
    pygame.init()
    pygame.display.set_caption('Alien Invasion')
    screen = pygame.display.set_mode((SCREEN_WIDTH,
                                      SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    # Create a seperate layer just containing the shields.
    shield_layer = pygame.surface.Surface([640,480])
    shield_layer.fill([0,0,0])
    shield_image = load_image('shield.png')
    draw_shields(shield_layer, shield_image)
    
    pygame.display.flip()
    
    random.seed()

    # Create our sprite groups.
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bombs = pygame.sprite.Group()

    # Associate the Sprite containers with their respective groups.
    Bullet.containers = bullets, all_sprites
    Alien.containers = aliens, all_sprites
    Bomb.containers = bombs, all_sprites
    Score.containers = all_sprites
    
    player = Player()
    
    if pygame.font:
        all_sprites.add(Score())
    ac = AlienController()
    all_sprites.add(player)

    running = True
    while player.alive() and running:
        
        clock.tick(FPS)
        all_sprites.update()
        # Check for collisions between bullets and bombs
        # on the shield layer.
        for bullet in bullets:
            bullet.check_collision(shield_layer)
        for bomb in bombs:
            bomb.check_collision(shield_layer)
        screen.fill([0,0,0])
        # Draw the shield layer, then all the sprites.
        # And flip the display to update it.
        screen.blit(shield_layer,[0,0])
        all_sprites.draw(screen)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keystate = pygame.key.get_pressed()
        # Fire a bullet when we smash the space bar.
        firing = keystate[pygame.K_SPACE]
        if not player.reloading and firing:
            Bullet(player.rect.midtop)
        player.reloading = firing
        ac.update()

        # Check for a collision between the aliens and our bullet.
        # Kill the alien if this happens and increase score.
        for alien in pygame.sprite.groupcollide(aliens, bullets, 1, 1):
            ac.remove(alien)
            alien.kill()
            SCORE += 25

        # Check for a collision between the alien's bomb and the player.
        # Game over if this happens.
        for bomb in pygame.sprite.spritecollide(player, bombs, 1):
            player.kill()

        if ac.count == 0:
            running = False
    pygame.quit()

if __name__ == '__main__':
    main()
