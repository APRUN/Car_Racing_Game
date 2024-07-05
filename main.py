import pygame
from pygame.locals import *
import random
import time
import asyncio

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

pygame.init()

# Creating the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game")

# Colors
gray = (100, 100, 100)
green = (76, 208, 53)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# Game Settings
gameover = False
speed = 2
score = 0

# Game loop
clock = pygame.time.Clock()
fps = 120
running = True

# Marker Size
MARKER_WIDTH = 10
MARKER_HEIGHT = 50

# Road and edge marker
road = (100, 0, 300, SCREEN_HEIGHT)
left_edge_marker = (95, 0, MARKER_WIDTH, SCREEN_HEIGHT)
right_edge_marker = (395, 0, MARKER_WIDTH, SCREEN_HEIGHT)

# x-coordinates of lanes
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# For animating lane movement
lane_marker_move_y = 0

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (int(new_width), int(new_height)))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

# Player Coordinates
player_x = 250
player_y = 400

# Load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# Create player's car
player_group = pygame.sprite.Group()
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# Load other vehicles
image_filenames = ['pickup_truck.png', 'taxi.png', 'semi_trailer.png', 'van.png']
vehicle_images = [pygame.image.load('images/' + name) for name in image_filenames]

# Sprite group for vehicles
vehicle_group = pygame.sprite.Group()

async def main():
    global running, gameover, speed, score, lane_marker_move_y, vehicle_group, player

    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            # Move player's car
            if event.type == KEYDOWN:
                if event.key == K_LEFT and player.rect.center[0] > left_lane:
                    player.rect.x -= 100
                if event.key == K_RIGHT and player.rect.center[0] < right_lane:
                    player.rect.x += 100
                
                # Check if there is a side swipe collision after changing lanes
                for vehicle in vehicle_group:
                    if pygame.sprite.collide_rect(player, vehicle):
                        gameover = True

                        # Place the player's car next to the other vehicle
                        # and determine where to put the crash image
                        if event.key == K_LEFT:   
                            player.rect.left = vehicle.rect.right
                            crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                        if event.key == K_RIGHT:
                            player.rect.right = vehicle.rect.left
                            crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
        
        screen.fill(green)
        
        # Draw Road
        pygame.draw.rect(screen, gray, Rect(road))
        pygame.draw.rect(screen, white, Rect(left_edge_marker))
        pygame.draw.rect(screen, white, Rect(right_edge_marker))
        
        # Movement of lanes
        lane_marker_move_y += speed * 2
        if lane_marker_move_y >= MARKER_HEIGHT * 2:
            lane_marker_move_y = 0
        
        # Draw Lanes
        for y in range(MARKER_HEIGHT * -2, SCREEN_HEIGHT, MARKER_HEIGHT * 2):
            pygame.draw.rect(screen, white, Rect((left_lane + 45, y + lane_marker_move_y, MARKER_WIDTH, MARKER_HEIGHT)))
            pygame.draw.rect(screen, white, Rect((center_lane + 45, y + lane_marker_move_y, MARKER_WIDTH, MARKER_HEIGHT)))
        
        # Add up to 2 vehicles
        if len(vehicle_group) < 2:
            # Ensure that there's enough gap between vehicles
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False

            if add_vehicle:
                vehicle = Vehicle(random.choice(vehicle_images), random.choice(lanes), random.randint(-100, 0))
                vehicle_group.add(vehicle)  

        # Make the vehicle move
        for vehicle in vehicle_group:
            vehicle.rect.y += speed

            # Remove the vehicle once it's out of the screen
            if vehicle.rect.y > SCREEN_HEIGHT:
                vehicle.kill()
                score += 1

                # Speed up game after passing 20 vehicles
                if score % 20 == 0 and score > 0:
                    speed += 1

        # Draw player car
        player_group.draw(screen)
        vehicle_group.draw(screen)

        # Display Score
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Score: ' + str(score), True, white)
        text_rect = text.get_rect(center = (50, 25))
        screen.blit(text, text_rect)

        # Check for head collision
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]
        
        # Display game over
        if gameover:
            screen.blit(crash, crash_rect)

            pygame.draw.rect(screen, red, (0, 50, SCREEN_WIDTH, 100))

            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render('Game Over. Y(Play again), N(QUIT)', True, white)
            text_rect = text.get_rect(center = (SCREEN_WIDTH / 2, 100))
            screen.blit(text, text_rect)

        pygame.display.update()

        while gameover:
            clock.tick(fps)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    gameover = False
                    running = False
                    
                # Get the user's input (y or n)
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        # Reset the game
                        gameover = False
                        speed = 2
                        score = 0
                        vehicle_group.empty()
                        player.rect.center = [player_x, player_y]
                    elif event.key == K_n:
                        # Exit the loops
                        gameover = False
                        running = False

        await asyncio.sleep(0)
    pygame.quit()   

asyncio.run(main())
