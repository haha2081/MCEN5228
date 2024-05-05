import pygame
import sys
import time
import math
import arabic_reshaper
from bidi.algorithm import get_display
import subprocess
import threading

pygame.init()

infoObject = pygame.display.Info()
screen_width, screen_height = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


BLUE = (0, 128, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


face_x, face_y = screen_width // 2, screen_height // 2
face_width, face_height = 200, 300
eye_radius = 40
eye_offset_x, eye_offset_y = 100, 100
mouth_width, mouth_height = 100, 20


dot_radius = 20
dot_distance = 80 


# Fade control variables
fade_alpha = 0  # Initial alpha value
fade_in = True  # Start with fade-in animation
fade_out = False  # Fade-out will be triggered after fade-in completes

welcome_screen = True
loading_done = True
face_sliding_in = False
sleep = False
face_position_x = -face_width  # Start off-screen to the left
# Function to draw Zs for sleeping



current_message_length = 0  # Current length of the message to display
message_display_time = 200  # Time in milliseconds between each letter appearing

# Load a robotic font
# If you have a specific .ttf font file, use pygame.font.Font('path_to_your_font.ttf', size)
# For a more robotic look, you might want to choose a font and size that fits
font_size = 40
robotic_font = pygame.font.SysFont(None, font_size)


            
            
def draw_welcome_message(alpha):
    global current_message_length
    y_positions = [screen_height // 4 + i * 100 for i in range(len(welcome_messages))]

    for i, message in enumerate(welcome_messages):
        reshaped_text = arabic_reshaper.reshape(message[:current_message_length])
        bidi_text = get_display(reshaped_text)
        # Render the text onto a temporary surface
        text_surface = welcome_fonts[i].render(bidi_text, True, BLACK)
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, alpha))  # Apply the alpha value here
        alpha_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        text_rect = alpha_surface.get_rect(center=(screen_width // 2, y_positions[i]))
        screen.blit(alpha_surface, text_rect)




    # Update the length of the message to display, if enough time has passed
    if pygame.time.get_ticks() % message_display_time < 60:  # Adjust timing sensitivity as needed
        if current_message_length <= message_length:
            current_message_length += 1

# Define the welcome messages in different languages
welcome_messages = [
    "Welcome to Jarvis",
    "Bienvenue à Jarvis",
    "مرحبا بكم في جارفيس",
     "Bem vindo ao Jarvis",
   "欢迎来到贾维斯"
]
# Load the font using pygame.font.Font for custom font files
custom_font_path = 'Display/Amiri/Amiri-Bold.ttf'
custom_cs = 'Display/Noto_Sans_SC/static/NotoSansSC-Regular.ttf'
welcome_fonts = [pygame.font.Font(custom_font_path, 40) for _ in range(len(welcome_messages)-1)] + [pygame.font.Font(custom_cs, 40)]
message_length = len(welcome_messages[2])

# Function to perform text-to-speech
def perform_tts(message):
    subprocess.run(['python3', 'tts.py', message], text=True)

# Thread function for text-to-speech
def tts_thread(message):
    global text_outloud
    perform_tts(message)
    text_outloud = True

def draw_zs(x, y, base_size=40):
    current_time = pygame.time.get_ticks()
    for i in range(3):
        # Oscillating size effect using a sine function, with different phase offsets
        size = base_size + (math.sin(current_time / 200.0 + i * 0.5) + 1) * 10  # Oscillate size between 10 and 30
        font = pygame.font.SysFont(None, int(size + 7*i))
        z_surface = font.render('Z', True, BLACK)
        screen.blit(z_surface, (x + i * 20, y - i * 20))  # Offset each Z slightly
        
def draw_sleep(mouth_open, x_position):

    local_face_x = x_position

    pygame.draw.circle(screen, BLACK, (local_face_x - eye_offset_x, face_y - eye_offset_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (local_face_x + eye_offset_x, face_y - eye_offset_y), eye_radius)
    pygame.draw.circle(screen, WHITE, (local_face_x - eye_offset_x, face_y - 1.2*eye_offset_y), eye_radius)
    pygame.draw.circle(screen, WHITE, (local_face_x + eye_offset_x, face_y - 1.2*eye_offset_y), eye_radius)
    # Draw mouth
    pygame.draw.ellipse(screen, BLACK, (local_face_x - mouth_width // 2 , face_y + eye_offset_y // 2, 70, 60), 7)


def draw_robot_face(eyelid_height, x_position):

    local_face_x = x_position
    pygame.draw.circle(screen, BLACK, (local_face_x - eye_offset_x, face_y - eye_offset_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (local_face_x + eye_offset_x, face_y - eye_offset_y), eye_radius)
    pygame.draw.rect(screen, WHITE, (local_face_x - eye_offset_x - eye_radius, face_y - eye_offset_y + eyelid_height, 2 * eye_radius, 2 * eye_radius))
    pygame.draw.rect(screen, WHITE, (local_face_x + eye_offset_x - eye_radius, face_y - eye_offset_y + eyelid_height, 2 * eye_radius, 2 * eye_radius))
    pygame.draw.circle(screen, BLACK, (local_face_x - eye_offset_x, face_y - eye_offset_y), eye_radius // 2)
    pygame.draw.circle(screen, BLACK, (local_face_x + eye_offset_x, face_y - eye_offset_y), eye_radius // 2)
    # Draw mouth
    pygame.draw.rect(screen, BLACK, (local_face_x - mouth_width // 2, face_y + eye_offset_y // 2, mouth_width, mouth_height))

def draw_loading_dots(alpha):
    for i in range(3):
        if pygame.time.get_ticks() // 500 % 4 > i:  # Timing for the dots to appear one after another
            pygame.draw.circle(screen, (0, 0, 0, alpha), (screen_width // 2 - dot_distance + (dot_distance * i), screen_height // 2), dot_radius)
            
clock = pygame.time.Clock()



running = True
counter = 0
counter2 = 0
blinking = False
eyelid_height = 0
mouth_open=0
text_outloud = 0
blinking_speed = 3
while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()
  # Fade-in animation logic
    if fade_in:
        fade_alpha += 5  # Increase alpha for fade-in effect
        if fade_alpha >= 255:
            fade_alpha = 255
            fade_in = False
            fade_out = True  # Trigger fade-out after a delay


    # Fade-out animation logic
    elif fade_out:
        fade_alpha -= 10  # Decrease alpha for fade-out effect
        if fade_alpha <= 0:
            fade_alpha = 0
            fade_out = False  # Reset or transition to next screen


    if welcome_screen:
        draw_welcome_message(fade_alpha)
        


        if current_message_length == message_length+1:
            welcome_screen = False
            loading_done = False  
            fade_alpha = 0
            loading_start_time = pygame.time.get_ticks()
          

    elif not loading_done:
        if not text_outloud:
            message = "Hello and welcome to Jarvis! give me a second while I load up my system !"
            threading.Thread(target=tts_thread, args=(message,)).start()
            text_outloud=True
            
        draw_loading_dots(fade_alpha)
        
        if current_time - loading_start_time >= 3000:
            loading_done = True
            face_sliding_in = True
            slide_start_time = current_time
            
    elif face_sliding_in:

        if current_time - slide_start_time < 1000:  
            face_position_x = -face_width + (current_time - slide_start_time) * (screen_width // 2 + face_width) / 1000
        else:
            face_position_x = screen_width // 2
            face_sliding_in = False
            sleep = False
        draw_robot_face(0, int(face_position_x))
        
    elif sleep:
        draw_sleep(mouth_open, int(face_position_x))
        draw_zs(face_x + 100, face_y - 250)

        if counter <=2:
            if blinking:
                if mouth_open<=eye_radius:
                    mouth_open+=1
                else:
                    blinking = False

            else:
                if mouth_open >=0:
                    mouth_open-=1
                else:
                    blinking = True
                    counter +=1
        else:
            counter2+=1
        
        if counter2>=240:
            counter2=0
            counter=0

    else:
        draw_robot_face(eyelid_height, int(face_position_x))
        if counter <=2:
            if blinking:
                if eyelid_height<=eye_radius:
                    eyelid_height+=3
                else:
                    blinking = False

            else:
                if eyelid_height >=0:
                    eyelid_height-=3
                else:
                    blinking = True
                    counter +=1
                    time.sleep(1)
        else:
            counter2+=1
        
        if counter2>=240:
            counter2=0
            counter=0

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    pygame.display.flip()
    clock.tick(60)  

pygame.quit()
sys.exit()
