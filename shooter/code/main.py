import pygame
from os.path import join
from random import randint, uniform 

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)) #placing player
        self.direction = pygame.Vector2()
        self.speed = 300

        #cooldown timer
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        #mask
        self.mask = pygame.mask.from_surface(self.image)
        

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration: #controls laser fire rate
                self.can_shoot =True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])   #control player direction
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction #controls player speed in diagonal movement
        self.rect.center += self.direction * self.speed * dt


        recent_keys = pygame.key.get_just_pressed() 
        if recent_keys[pygame.K_SPACE]:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH),randint (0, WINDOW_HEIGHT)),)

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt): #to make the laser to move
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0: #to kill the laser
            self.kill()
        
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400, 500)
        self.rotation_speed = randint(50, 50)
        self.rotation = 0

       
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime: #to kil the meteor
           self.kill() 
        
        #rotate
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
    
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frames_index += 40 * dt
        if self.frames_index < len(self.frames):
            self.image = self.frames[int(self.frames_index)]
        else:
            self.kill()

def collisions():
    global running
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_score(): 
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, 'white')
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, 'white', text_rect.inflate(20,20).move(0, -5), 5, 10)
    return current_time

def game_over_screen(score):
    game_over_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 60)
    score_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
    
    game_over_surf = game_over_font.render("GAME OVER", True, 'white')
    game_over_rect = game_over_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
    
    score_surf = score_font.render(f"Your Score is: {score}", True, 'white')
    score_rect = score_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
    
    display_surface.fill('#0b1f3a')
    display_surface.blit(game_over_surf, game_over_rect)
    display_surface.blit(score_surf, score_rect)
    pygame.display.update()
    
    pygame.time.wait(3000)  # Wait for 3 seconds before closing the game

#general setup, window setup
pygame.init() 
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Defender')
running = True
clock = pygame.time.Clock()

#imorts
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.1)

explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.1)

damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))

game_sound = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_sound.set_volume(0.1)
game_sound.play(loops= -1)

#sprites   
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

#custom meteor event 
meteor_event = pygame.event.custom_type() #to create an interval timer
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick() / 1000
        #event loop to close the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    #update   
    all_sprites.update(dt)
    collisions()
    
    #draw the game
    display_surface.fill('#0b1f3a')   #fill the window color #3a2e3f 
    all_sprites.draw(display_surface)  
    score = display_score()
    pygame.display.update()

game_over_screen(score)
pygame.quit()
