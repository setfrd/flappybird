#from asyncio.windows_utils import pipe
import imghdr
import pygame
from pygame.locals import *
import random

pygame.init() #initializing the game

clock = pygame.time.Clock()
fps = 60


#game window
screen_width = 864
screen_height = 936

#display name
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')  


#define font
font = pygame.font.SysFont('candara', 60)

#define colors
white = (255, 255, 255)


#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


#load images, backround
bg = pygame.image.load('/Users/faridtalibli/Desktop/flappybird/bg.png')
ground_image = pygame.image.load('/Users/faridtalibli/Desktop/flappybird/ground.png')
button_img = pygame.image.load('/Users/faridtalibli/Desktop/flappybird/restart.png')

#TEXT
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0 
        for num in range(1, 4):
            img = pygame.image.load(f'/Users/faridtalibli/Desktop/flappybird/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0  
        self.clicked = False   
    
    def update(self):

        #gravity
        if flying == True :
            self.vel += 0.5
            if self.vel > 8: #limiting
                self.vel = 8
            if self.rect.bottom < 768 :
                self.rect.y += int(self.vel)

        if game_over == False:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True 
                self.vel = -10

            if pygame.mouse.get_pressed()[0] == 0 :
                self.clicked = False

            #handle the animation
            self.counter += 1
            flap_colldown = 5

            if self.counter > flap_colldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]


            #rotare the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


#pipe
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x,y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('/Users/faridtalibli/Desktop/flappybird/pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is from the top -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]


    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0: #stop the pipes after you pass them
            self.kill() 

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self):

        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if the mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action =  True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

#create rester button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


#game loop 
run = True
while run:

    #fixing the fps
    clock.tick(fps)


    #daw backround
    screen.blit(bg, (0,0))
    
    
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
 

    #draw the ground
    screen.blit(ground_image,(ground_scroll, 768))

    #check the score

    
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True and not score_updated_this_frame:
             if bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right:
                score += 1
                score_updated_this_frame = True
                pass_pipe = False


    draw_text(str(score), font, white, int(screen_width / 2), 20)



    #look for collusion
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True


    #check if bird has hit the ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False


    if game_over == False and flying == True:

        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

            score_updated_this_frame = False

        #draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0 

        pipe_group.update()

    #check for game over and reset
    if game_over == True:
       if button.draw() == True:
           game_over = False
           score = reset_game()



    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True


    pygame.display.update() #updates the screen so new things happen

pygame.quit() # closing the window


