import pygame
from pygame.locals import *
from config import config 
from random import randint



class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            pygame.image.load("Assets/Game Objects/yellowbird-upflap.png").convert_alpha(),
            pygame.image.load("Assets/Game Objects/yellowbird-midflap.png").convert_alpha(),
            pygame.image.load("Assets/Game Objects/yellowbird-downflap.png").convert_alpha()
        ]

        self.images = [pygame.transform.scale(image, (50, 38)) for image in self.images]

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0
        self.velocity = 0
        self.gravity = config.BIRD_GRAVITY
        self.jump_strength = config.BIRD_JUMP
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.counter += 1
        if self.counter > 5:  # Change image every 5 frames
            self.counter = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]
            self.mask = pygame.mask.from_surface(self.image)

        self.velocity += self.gravity
        self.rect.y += self.velocity

        # Rotate bird
        self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        self.mask = pygame.mask.from_surface(self.image)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, gap):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Assets/Game Objects/pipe2.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pipe_gap = gap

        # Position 1 = pipe on top, -1 = on the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(self.pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(self.pipe_gap / 2)]

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0:
            self.kill()



class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Sounds
        pygame.mixer.music.load("Assets/Sound Efects/kevin-macleod blippy-trance.mp3")

        self.fly_sfx = pygame.mixer.Sound("Assets/Sound Efects/wing.wav")
        self.fall_sfx = pygame.mixer.Sound("Assets/Sound Efects/die.wav")
        self.score_sfx = pygame.mixer.Sound("Assets/Sound Efects/tap.wav")
        self.restart_sfx = pygame.mixer.Sound("Assets/Sound Efects/restart.mp3")
        self.played_fall_sfx = False

        # Set screen & icon
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        icon = pygame.image.load("Assets/Game Objects/yellowbird-midflap.png")
        pygame.display.set_icon(icon)

        # Set background
        self.background = pygame.image.load("Assets/Game Objects/background2.jpg")
        self.background_width = self.background.get_width()
        self.background_pos1 = 0
        self.background_pos2 = self.background_width

        self.ground = pygame.image.load("Assets/Game Objects/ground.png")

        # Initialize positions of all ground objects
        self.ground_positions = [g_num * self.ground.get_width() for g_num in range(6)]

        # Numbers
        self.numbers = [
            pygame.image.load("Assets/UI/Numbers/0.png"),
            pygame.image.load("Assets/UI/Numbers/1.png"),
            pygame.image.load("Assets/UI/Numbers/2.png"),
            pygame.image.load("Assets/UI/Numbers/3.png"),
            pygame.image.load("Assets/UI/Numbers/4.png"),
            pygame.image.load("Assets/UI/Numbers/5.png"),
            pygame.image.load("Assets/UI/Numbers/6.png"),
            pygame.image.load("Assets/UI/Numbers/7.png"),
            pygame.image.load("Assets/UI/Numbers/8.png"),
            pygame.image.load("Assets/UI/Numbers/9.png")
        ]

        # Bird
        self.bird_group = pygame.sprite.Group()
        self.flappy = Bird(100, int(config.SCREEN_HEIGHT / 2))
        self.bird_group.add(self.flappy)

        # Pipes
        self.pipe_group = pygame.sprite.Group()
        self.pipe_distance = config.PIPE_DISTANCE  
        self.last_pipe = pygame.time.get_ticks() - self.pipe_distance

        # Restart button
        self.restart_button = pygame.image.load("Assets/UI/restart.png")
        self.restart_rect = self.restart_button.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))

        # Game over
        self.game_over_image = pygame.image.load("Assets/UI/gameover.png")
        self.game_over_image = pygame.transform.scale(self.game_over_image, (350, 100))
        self.game_over_rect = self.game_over_image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4))

        # Get started
        self.waiting_for_start_image = pygame.image.load("Assets/UI/message.png")
        self.waiting_for_start_rect = self.waiting_for_start_image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.waiting_for_start = True

        # Game 
        self.running = True
        self.game_over = False
        self.game_speed = config.GAME_SPEED
        self.last_speed_increase = pygame.time.get_ticks()
        self.score = 0
        self.pass_pipe = False 
        self.clock = pygame.time.Clock()

    def draw_ground(self):
        for pos in self.ground_positions:
            self.screen.blit(self.ground, (pos, 690))

    def move_ground(self):
        if not self.waiting_for_start and not self.game_over:
            for i in range(len(self.ground_positions)):
                self.ground_positions[i] -= self.game_speed
                if self.ground_positions[i] < -self.ground.get_width():
                    self.ground_positions[i] += 4 * self.ground.get_width()

    def move_background(self):
        if not self.waiting_for_start and not self.game_over:
            self.background_pos1 -= config.BACKGROUND_SPEED
            self.background_pos2 -= config.BACKGROUND_SPEED

            if self.background_pos1 <= -self.background_width:
                self.background_pos1 = self.background_pos2 + self.background_width
            if self.background_pos2 <= -self.background_width:
                self.background_pos2 = self.background_pos1 + self.background_width

    def move_pipes(self):
        if not self.game_over and not self.waiting_for_start:
            if self.pipe_group:
                last_pipe = self.pipe_group.sprites()[-1]
                distance_since_last_pipe = config.SCREEN_WIDTH - last_pipe.rect.x
            else:
                distance_since_last_pipe = config.SCREEN_WIDTH

            if distance_since_last_pipe >= self.pipe_distance:
                pipe_height = randint(-200, 100)
                pipe_gap = randint(135, 350)
                self.btm_pipe = Pipe(config.SCREEN_WIDTH, int(config.SCREEN_HEIGHT / 2) + pipe_height, -1, pipe_gap)
                self.top_pipe = Pipe(config.SCREEN_WIDTH, int(config.SCREEN_HEIGHT / 2) + pipe_height, 1, pipe_gap)
                self.pipe_group.add(self.btm_pipe, self.top_pipe)

    def check_collision(self):
        # Check pipes collision 
        if pygame.sprite.spritecollide(self.flappy, self.pipe_group, False, pygame.sprite.collide_mask):
            self.game_over = True

        # Check ground collision 
        if self.flappy.rect.bottom >= 680:
            # self.flappy.rect.bottom = 680
            self.game_over = True

        # Check screen collision
        if self.flappy.rect.top <= 0:
            self.flappy.rect.top = 0
            self.game_over = True

    def check_score(self):
        if len(self.pipe_group) > 0:
            if self.bird_group.sprites()[0].rect.left > self.pipe_group.sprites()[0].rect.left\
                and self.bird_group.sprites()[0].rect.right < self.pipe_group.sprites()[0].rect.right\
                and self.pass_pipe == False:
                self.pass_pipe = True
            
            if self.pass_pipe == True:
                if self.bird_group.sprites()[0].rect.left > self.pipe_group.sprites()[0].rect.right:
                    self.score_sfx.play()
                    self.score += 1
                    self.pass_pipe = False 

    def draw_score(self):
        score_str = str(self.score)
        total_width = 0
        for digit in score_str:
            total_width += self.numbers[int(digit)].get_width()

        x_offset = (config.SCREEN_WIDTH - total_width) // 2

        for digit in score_str:
            self.screen.blit(self.numbers[int(digit)], (x_offset, 10))
            x_offset += self.numbers[int(digit)].get_width()

    def reset_game(self):
        self.flappy.rect.center = (100, int(config.SCREEN_HEIGHT / 2))
        self.flappy.velocity = 0
        self.pipe_group.empty()
        self.ground_positions = [g_num * self.ground.get_width() for g_num in range(4)]
        self.background_pos1 = 0
        self.background_pos2 = self.background_width
        self.game_over = False
        self.played_fall_sfx = False
        self.score = 0
        self.start_music()  # Запуск музыки при перезапуске игры

    def start_music(self):
        pygame.mixer.music.play(-1)  # Запуск фоновой музыки

    def stop_music(self):
        pygame.mixer.music.stop()  # Остановка фоновой музыки

    def update(self):
        # Move background
        self.move_background()

        # Draw background
        self.screen.blit(self.background, (self.background_pos1, 0))
        self.screen.blit(self.background, (self.background_pos2, 0))

        if self.waiting_for_start:
            self.screen.blit(self.waiting_for_start_image, self.waiting_for_start_rect)
            self.draw_ground()
        else:
            # Update game speed every second
            if not self.game_over:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_speed_increase > 1000:
                    self.game_speed += config.GAME_SPEED_INCREMENT_RATE
                    self.last_speed_increase = current_time

                self.bird_group.update()
                for pipe in self.pipe_group:
                    # Apply game_speed on every pipes
                    pipe.update(self.game_speed)
                self.move_pipes()

            # Draw pipes
            self.pipe_group.draw(self.screen)
            self.bird_group.draw(self.screen)

            # Move and draw ground
            self.move_ground()
            self.draw_ground()

            self.check_collision()
            self.check_score()  # Check the score
            self.draw_score()   # Draw the score

            # Game over & restart
            if self.game_over:
                self.game_speed = config.GAME_SPEED
                self.screen.blit(self.game_over_image, self.game_over_rect)
                self.screen.blit(self.restart_button, self.restart_rect)

                if not self.played_fall_sfx:
                    self.fall_sfx.play()
                    self.played_fall_sfx = True
                
                self.stop_music()  # Остановка музыки при завершении игры

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if self.waiting_for_start:
                        self.waiting_for_start = False
                        self.start_music()  # Запуск музыки при старте игры
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not self.game_over:
                            self.fly_sfx.play()
                            self.flappy.velocity = self.flappy.jump_strength
                        elif event.key == pygame.K_SPACE and self.game_over:
                            self.restart_sfx.play()
                            self.reset_game()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and not self.game_over:
                            self.fly_sfx.play()
                            self.flappy.velocity = self.flappy.jump_strength
                        elif event.button == 1 and self.game_over:
                            mouse_pos = pygame.mouse.get_pos()
                            if self.restart_rect.collidepoint(mouse_pos):
                                self.restart_sfx.play()
                                self.reset_game()

            self.update()
            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

# class Game:
#     def __init__(self):
#         pygame.init()
#         pygame.mixer.init()

#         # Sounds
#         pygame.mixer.music.load("Assets/Sound Efects/kevin-macleod-blippy-trance.mp3")

#         self.fly_sfx = pygame.mixer.Sound("Assets/Sound Efects/wing.wav")
#         self.fall_sfx = pygame.mixer.Sound("Assets/Sound Efects/die.wav")
#         self.score_sfx = pygame.mixer.Sound("Assets/Sound Efects/tap.wav")
#         self.restart_sfx = pygame.mixer.Sound("Assets/Sound Efects/restart.mp3")
#         self.played_fall_sfx = False

#         # Set screen & icon
#         self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
#         pygame.display.set_caption("Flappy Bird")
#         icon = pygame.image.load("Assets/Game Objects/yellowbird-midflap.png")
#         pygame.display.set_icon(icon)

#         # Set background
#         self.background = pygame.image.load("Assets/Game Objects/background2.jpg")
#         self.background_width = self.background.get_width()
#         self.background_pos1 = 0
#         self.background_pos2 = self.background_width

#         self.ground = pygame.image.load("Assets/Game Objects/ground.png")

#         # Initialize positions of all ground objects
#         self.ground_positions = [g_num * self.ground.get_width() for g_num in range(6)]

#         # Numbers
#         self.numbers = [
#             pygame.image.load("Assets/UI/Numbers/0.png"),
#             pygame.image.load("Assets/UI/Numbers/1.png"),
#             pygame.image.load("Assets/UI/Numbers/2.png"),
#             pygame.image.load("Assets/UI/Numbers/3.png"),
#             pygame.image.load("Assets/UI/Numbers/4.png"),
#             pygame.image.load("Assets/UI/Numbers/5.png"),
#             pygame.image.load("Assets/UI/Numbers/6.png"),
#             pygame.image.load("Assets/UI/Numbers/7.png"),
#             pygame.image.load("Assets/UI/Numbers/8.png"),
#             pygame.image.load("Assets/UI/Numbers/9.png")
#         ]

#         # Bird
#         self.bird_group = pygame.sprite.Group()
#         self.flappy = Bird(100, int(config.SCREEN_HEIGHT / 2))
#         self.bird_group.add(self.flappy)

#         # Pipes
#         self.pipe_group = pygame.sprite.Group()
#         self.pipe_distance = config.PIPE_DISTANCE  
#         self.last_pipe = pygame.time.get_ticks() - self.pipe_distance

#         # Restart button
#         self.restart_button = pygame.image.load("Assets/UI/restart.png")
#         self.restart_rect = self.restart_button.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))

#         # Game over
#         self.game_over_image = pygame.image.load("Assets/UI/gameover.png")
#         self.game_over_rect = self.game_over_image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4))

#         # Get started
#         self.waiting_for_start_image = pygame.image.load("Assets/UI/message.png")
#         self.waiting_for_start_rect = self.waiting_for_start_image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
#         self.waiting_for_start = True

#         # Game 
#         self.running = True
#         self.game_over = False
#         self.game_speed = config.GAME_SPEED
#         self.last_speed_increase = pygame.time.get_ticks()
#         self.score = 0
#         self.pass_pipe = False 
#         self.clock = pygame.time.Clock()

#     def draw_ground(self):
#         for pos in self.ground_positions:
#             self.screen.blit(self.ground, (pos, 694))

#     def move_ground(self):
#         if not self.waiting_for_start and not self.game_over:
#             for i in range(len(self.ground_positions)):
#                 self.ground_positions[i] -= self.game_speed
#                 if self.ground_positions[i] < -self.ground.get_width():
#                     self.ground_positions[i] += 4 * self.ground.get_width()

#     def move_background(self):
#         if not self.waiting_for_start and not self.game_over:
#             self.background_pos1 -= config.BACKGROUND_SPEED
#             self.background_pos2 -= config.BACKGROUND_SPEED

#             if self.background_pos1 <= -self.background_width:
#                 self.background_pos1 = self.background_pos2 + self.background_width
#             if self.background_pos2 <= -self.background_width:
#                 self.background_pos2 = self.background_pos1 + self.background_width

#     def move_pipes(self):
#         if not self.game_over and not self.waiting_for_start:
#             if self.pipe_group:
#                 last_pipe = self.pipe_group.sprites()[-1]
#                 distance_since_last_pipe = config.SCREEN_WIDTH - last_pipe.rect.x
#             else:
#                 distance_since_last_pipe = config.SCREEN_WIDTH

#             if distance_since_last_pipe >= self.pipe_distance:
#                 pipe_height = randint(-240, 140)
#                 pipe_gap = randint(140, 300)
#                 self.btm_pipe = Pipe(config.SCREEN_WIDTH, int(config.SCREEN_HEIGHT / 2) + pipe_height, -1, pipe_gap)
#                 self.top_pipe = Pipe(config.SCREEN_WIDTH, int(config.SCREEN_HEIGHT / 2) + pipe_height, 1, pipe_gap)
#                 self.pipe_group.add(self.btm_pipe, self.top_pipe)

#     def check_collision(self):
#         # Проверка коллизии с трубами
#         if pygame.sprite.spritecollide(self.flappy, self.pipe_group, False, pygame.sprite.collide_mask):
#             self.game_over = True

#         # Проверка коллизии с землей
#         if self.flappy.rect.bottom >= 680:
#             self.flappy.rect.bottom = 680
#             self.game_over = True

#         # Проверка коллизии с верхней границей экрана
#         if self.flappy.rect.top <= 0:
#             self.flappy.rect.top = 0
#             self.game_over = True

#     def check_score(self):
#         if len(self.pipe_group) > 0:
#             if self.bird_group.sprites()[0].rect.left > self.pipe_group.sprites()[0].rect.left\
#                 and self.bird_group.sprites()[0].rect.right < self.pipe_group.sprites()[0].rect.right\
#                 and self.pass_pipe == False:
#                 self.pass_pipe = True
            
#             if self.pass_pipe == True:
#                 if self.bird_group.sprites()[0].rect.left > self.pipe_group.sprites()[0].rect.right:
#                     self.score_sfx.play()
#                     self.score += 1
#                     self.pass_pipe = False 

#     def draw_score(self):
#         score_str = str(self.score)
#         total_width = 0
#         for digit in score_str:
#             total_width += self.numbers[int(digit)].get_width()

#         x_offset = (config.SCREEN_WIDTH - total_width) // 2

#         for digit in score_str:
#             self.screen.blit(self.numbers[int(digit)], (x_offset, 10))
#             x_offset += self.numbers[int(digit)].get_width()
    
#     def reset_game(self):
#         self.flappy.rect.center = (100, int(config.SCREEN_HEIGHT / 2))
#         self.flappy.velocity = 0
#         self.pipe_group.empty()
#         self.ground_positions = [g_num * self.ground.get_width() for g_num in range(4)]
#         self.background_pos1 = 0
#         self.background_pos2 = self.background_width
#         self.game_over = False
#         self.played_fall_sfx = False
#         self.score = 0
#         pygame.mixer.music.play(-1)  # Restart background music

#     def update(self):
#         # Move background
#         self.move_background()

#         # Draw background
#         self.screen.blit(self.background, (self.background_pos1, 0))
#         self.screen.blit(self.background, (self.background_pos2, 0))

#         if self.waiting_for_start:
#             self.screen.blit(self.waiting_for_start_image, self.waiting_for_start_rect)
#             self.draw_ground()
#         else:
#             # Update game speed every second
#             if not self.game_over:
#                 current_time = pygame.time.get_ticks()
#                 if current_time - self.last_speed_increase > 1000:
#                     self.game_speed += config.GAME_SPEED_INCREMENT_RATE
#                     self.last_speed_increase = current_time

#                 self.bird_group.update()
#                 for pipe in self.pipe_group:
#                     # Apply game_speed on every pipes
#                     pipe.update(self.game_speed)
#                 self.move_pipes()

#             # Draw pipes
#             self.pipe_group.draw(self.screen)
#             self.bird_group.draw(self.screen)

#             # Move and draw ground
#             self.move_ground()
#             self.draw_ground()

#             self.check_collision()
#             self.check_score()  # Check the score
#             self.draw_score()   # Draw the score

#             # Game over & restart
#             if self.game_over:
#                 self.game_speed = config.GAME_SPEED
#                 self.screen.blit(self.game_over_image, self.game_over_rect)
#                 self.screen.blit(self.restart_button, self.restart_rect)

#                 if not self.played_fall_sfx:
#                     self.fall_sfx.play()
#                     self.played_fall_sfx = True
                
#                 pygame.mixer.music.stop()  # Stop background music

#     def run(self):
#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False
#                 elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
#                     if self.waiting_for_start: 
#                         self.waiting_for_start = False
#                     elif event.type == pygame.KEYDOWN:
#                         if event.key == pygame.K_SPACE and not self.game_over:
#                             self.fly_sfx.play()
#                             self.flappy.velocity = self.flappy.jump_strength
#                         elif event.key == pygame.K_SPACE and self.game_over:
#                             self.restart_sfx.play()
#                             self.reset_game()

#                     elif event.type == pygame.MOUSEBUTTONDOWN:
#                         if event.button == 1 and not self.game_over:
#                             self.fly_sfx.play()
#                             self.flappy.velocity = self.flappy.jump_strength
#                         elif event.button == 1 and self.game_over:
#                             mouse_pos = pygame.mouse.get_pos()
#                             if self.restart_rect.collidepoint(mouse_pos):
#                                 self.restart_sfx.play()
#                                 self.reset_game()

#                 if self.game_over == False:
#                     if not pygame.mixer.music.get_busy():
#                         pygame.mixer.music.play(-1)

#                 else:
#                     pygame.mixer.music.stop()

#             self.update()
#             pygame.display.flip()
#             self.clock.tick(config.FPS)

#         pygame.quit()

# if __name__ == "__main__":
#     game = Game()
#     game.run()
