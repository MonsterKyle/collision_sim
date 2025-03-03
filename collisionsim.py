import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collision sim")

# Colors
LIGHT_GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Keypad codes
KEYPAD_1 = pygame.K_KP_1
KEYPAD_2 = pygame.K_KP_2
KEYPAD_3 = pygame.K_KP_3
KEYPAD_4 = pygame.K_KP_4
KEYPAD_5 = pygame.K_KP_5
KEYPAD_6 = pygame.K_KP_6
KEYPAD_7 = pygame.K_KP_7
KEYPAD_8 = pygame.K_KP_8
KEYPAD_9 = pygame.K_KP_9
KEYPAD_0 = pygame.K_KP_0

# Circle properties
CIRCLE_RADIUS = 20
CIRCLE_SPEED_SLOW = 3
CIRCLE_SPEED_MEDIUM = 4
CIRCLE_SPEED_FAST = 4.5  # Reduced fast speed

# Game variables
circles = []
round_number = 1
collisions = 0
font = pygame.font.Font(None, 36)
round_start_time = 0
collision_pairs = set()
game_over = False
restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
speed_selection = True
slow_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 100, 50)
medium_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 75, 100, 50)
fast_button = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 75, 100, 50)
endless_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50)
custom_speed_mode = False
custom_speed_input = ""
custom_speed = 4
current_circle_speed = CIRCLE_SPEED_SLOW
round_delay = 1  # Default delay
remove_delay = False  # Added variable to track checkbox state
checkbox_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 85, 20, 20)
math_start_time = 0
math_timeout = 5000
endless_mode = False
endless_checkbox_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 20, 20)  # Checkbox position

#mathmode
math_problem = None
math_options = []
math_correct_answer = None
math_bar_height = 80  # Increase the height (adjust as needed)
math_bar_rect = pygame.Rect(0, HEIGHT - math_bar_height, WIDTH, math_bar_height)
correct_math_answers = 0
incorrect_math_answers = 0

def generate_math_problem():
    global math_problem, math_options, math_correct_answer
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(['+', '-', '*'])

    if operator == '+':
        math_problem = f"{num1} + {num2} = ?"
        math_correct_answer = num1 + num2
    elif operator == '-':
        math_problem = f"{num1} - {num2} = ?"
        math_correct_answer = num1 - num2
    else:
        math_problem = f"{num1} * {num2} = ?"
        math_correct_answer = num1 * num2

    math_options = [math_correct_answer]
    while len(math_options) < 4:
        wrong_answer = random.randint(math_correct_answer - 10, math_correct_answer + 10)
        if wrong_answer not in math_options:
            math_options.append(wrong_answer)
    random.shuffle(math_options)

def generate_circle(number):
    while True:
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            y = CIRCLE_RADIUS
            target_x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            target_y = HEIGHT - math_bar_height - CIRCLE_RADIUS #prevent spawning under math bar
        elif side == 1:
            x = WIDTH - CIRCLE_RADIUS
            y = random.randint(CIRCLE_RADIUS, HEIGHT - math_bar_height - CIRCLE_RADIUS) #prevent spawning under math bar
            target_x = CIRCLE_RADIUS
            target_y = random.randint(CIRCLE_RADIUS, HEIGHT - math_bar_height - CIRCLE_RADIUS) #prevent spawning under math bar
        elif side == 2:
            x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            y = HEIGHT - math_bar_height - CIRCLE_RADIUS #prevent spawning under math bar
            target_x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            target_y = CIRCLE_RADIUS
        else:
            x = CIRCLE_RADIUS
            y = random.randint(CIRCLE_RADIUS, HEIGHT - math_bar_height - CIRCLE_RADIUS) #prevent spawning under math bar
            target_x = WIDTH - CIRCLE_RADIUS
            target_y = random.randint(CIRCLE_RADIUS, HEIGHT - math_bar_height - CIRCLE_RADIUS) #prevent spawning under math bar

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance == 0:
            direction_x = 0
            direction_y = 0
        else:
            direction_x = dx / distance
            direction_y = dy / distance

        new_circle = {
            'x': x,
            'y': y,
            'target_x': target_x,
            'target_y': target_y,
            'number': number,
            'dx': direction_x * current_circle_speed,
            'dy': direction_y * current_circle_speed,
            'color': LIGHT_BLUE
        }

        overlap = False
        for existing_circle in circles:
            if check_collision(new_circle, existing_circle):
                overlap = True
                break

        if not overlap:
            circles.append(new_circle)
            return

def check_collision(c1, c2):
    distance = math.sqrt((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)
    return distance < CIRCLE_RADIUS * 2

def draw_circles():
    for circle in circles:
        pygame.draw.circle(screen, BLACK, (int(circle['x']), int(circle['y'])), CIRCLE_RADIUS) #Draw black outline
        pygame.draw.circle(screen, circle['color'], (int(circle['x']), int(circle['y'])), CIRCLE_RADIUS - 2) #Draw the circle inside
        text = font.render(str(circle['number']), True, BLACK)
        text_rect = text.get_rect(center=(int(circle['x']), int(circle['y'])))
        screen.blit(text, text_rect)

def move_circles():
    global collisions, collision_pairs
    for i in range(len(circles)):
        circles[i]['x'] += circles[i]['dx']
        circles[i]['y'] += circles[i]['dy']

        for j in range(i + 1, len(circles)):
            if check_collision(circles[i], circles[j]):
                pair = tuple(sorted((circles[i]['number'], circles[j]['number'])))
                if pair not in collision_pairs:
                    circles[i]['color'] = RED
                    circles[j]['color'] = RED
                    collisions += 1
                    collision_pairs.add(pair)

def remove_offscreen_circles():
    global circles
    circles = [c for c in circles if 0 < c['x'] < WIDTH and 0 < c['y'] < HEIGHT]

def start_new_round():
    global circles, round_number, round_start_time, collision_pairs, math_problem, math_options, math_correct_answer, incorrect_math_answers, math_start_time
    circles.clear()
    collision_pairs.clear()
    for i in range(round_number + 1):
        generate_circle(i + 1)
    round_number += 1
    round_start_time = time.time()
    if math_problem:
        incorrect_math_answers += 1
        math_problem = None
        math_options = []
        math_correct_answer = None
    math_start_time = pygame.time.get_ticks()
    generate_math_problem()
    print("Math problem generated!")  # Add this line

def reset_game():
    global circles, round_number, collisions, collision_pairs, game_over, speed_selection, correct_math_answers, incorrect_math_answers, math_problem, math_options, math_correct_answer
    circles.clear()
    round_number = 1
    collisions = 0
    collision_pairs.clear()
    game_over = False
    speed_selection = True
    correct_math_answers = 0
    incorrect_math_answers = 0
    math_problem = None #clear math problem
    math_options = [] #clear math options
    math_correct_answer = None #clear correct math answer

# Game loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if speed_selection:
                if endless_checkbox_rect.collidepoint(event.pos): #Checkbox click
                    endless_mode = not endless_mode #toggle checkbox.
                if slow_button.collidepoint(event.pos):
                    current_circle_speed = CIRCLE_SPEED_SLOW
                    round_delay = 0 if remove_delay else 1 #if remove_delay is true, no delay, else 1 second.
                    speed_selection = False
                    start_new_round()
                elif medium_button.collidepoint(event.pos):
                    current_circle_speed = CIRCLE_SPEED_MEDIUM
                    round_delay = 0 if remove_delay else 0.75
                    speed_selection = False
                    start_new_round()
                elif fast_button.collidepoint(event.pos):
                    current_circle_speed = CIRCLE_SPEED_FAST
                    round_delay = 0 if remove_delay else 0.5
                    speed_selection = False
                    start_new_round()
                elif checkbox_rect.collidepoint(event.pos): #Checkbox click
                    remove_delay = not remove_delay #toggle checkbox.
            elif game_over:
                if restart_button.collidepoint(event.pos):
                    reset_game()
                #Added speed selection to game over screen.
                elif slow_button.collidepoint(event.pos):
                    current_circle_speed = CIRCLE_SPEED_SLOW
                    round_delay = 1
                    speed_selection = False
                    start_new_round()
                elif medium_button.collidepoint(event.pos):
                    current_circle_speed = CIRCLE_SPEED_MEDIUM
                    round_delay = 0.75
                    speed_selection = False
                    start_new_round()
                elif fast_button.collidepoint(event.pos):
                    current_circle_speed = CIRCLE_SPEED_FAST
                    round_delay = 0.5
                    speed_selection = False
                    start_new_round()

        if event.type == pygame.KEYDOWN and not speed_selection:
            if event.type == pygame.KEYDOWN and not speed_selection:
                if math_options:  # Only run if math_options exists
                    if event.key == pygame.K_q:
                        if math_options[0] == math_correct_answer:
                            print("Correct!")
                            is_correct = True
                        else:
                            print("Incorrect!")
                            is_correct = False
                    elif event.key == pygame.K_w:
                        if math_options[1] == math_correct_answer:
                            print("Correct!")
                            is_correct = True
                        else:
                            print("Incorrect!")
                            is_correct = False
                    elif event.key == pygame.K_e:
                        if math_options[2] == math_correct_answer:
                            print("Correct!")
                            is_correct = True
                        else:
                            print("Incorrect!")
                            is_correct = False
                    elif event.key == pygame.K_r:
                        if math_options[3] == math_correct_answer:
                            print("Correct!")
                            is_correct = True
                        else:
                            print("Incorrect!")
                            is_correct = False

                    if 'is_correct' in locals():  # Only run if a correct answer was selected
                        if is_correct:
                            correct_math_answers += 1
                        else:
                            incorrect_math_answers += 1

                        math_problem = None
                        math_options = []
                        math_correct_answer = None

                        del is_correct  # Delete the variable so it doesn't cause issues later.
            if not game_over:
                pygame.draw.rect(screen, GRAY, math_bar_rect)

                # Draw math problem
                if math_problem:
                    problem_text = font.render(math_problem, True, BLACK)
                    problem_rect = problem_text.get_rect(center=(WIDTH // 2, HEIGHT - math_bar_height // 2))
                    screen.blit(problem_text, problem_rect)

                    # Draw math options
                    option_spacing = WIDTH // 4
                    vertical_spacing = 20
                    for i, option in enumerate(math_options):
                        option_text = font.render(f"{option}", True, BLACK)
                        option_rect = option_text.get_rect(center=(option_spacing * (i + 0.5), HEIGHT - math_bar_height // 4 + vertical_spacing))
                        screen.blit(option_text, option_rect)
                current_time = pygame.time.get_ticks()
                if math_problem and current_time - math_start_time > math_timeout:  # if there is a math problem and it has timed out
                    incorrect_math_answers += 1
                    math_problem = None
                    math_options = []
                    math_correct_answer = None
                if event.key == pygame.K_1 or event.key == KEYPAD_1:
                    number = 1
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_2 or event.key == KEYPAD_2:
                    number = 2
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_3 or event.key == KEYPAD_3:
                    number = 3
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_4 or event.key == KEYPAD_4:
                    number = 4
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_5 or event.key == KEYPAD_5:
                    number = 5
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_6 or event.key == KEYPAD_6:
                    number = 6
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_7 or event.key == KEYPAD_7:
                    number = 7
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_8 or event.key == KEYPAD_8:
                    number = 8
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_9 or event.key == KEYPAD_9:
                    number = 9
                    circles = [c for c in circles if c['number'] != number]
                elif event.key == pygame.K_0 or event.key == KEYPAD_0:
                    number = 0
                    circles = [c for c in circles if c['number'] != number]

    screen.fill(LIGHT_GRAY)

    if speed_selection:
        #Speed selection screen, used for both start and game over.
        slow_rect = pygame.draw.rect(screen, GRAY, slow_button)
        medium_rect = pygame.draw.rect(screen, GRAY, medium_button)
        fast_rect = pygame.draw.rect(screen, GRAY, fast_button)
        slow_text = font.render("Slow", True, BLACK)
        medium_text = font.render("Medium", True, BLACK)
        fast_text = font.render("Fast", True, BLACK)
        screen.blit(slow_text, slow_text.get_rect(center=slow_rect.center))
        screen.blit(medium_text, medium_text.get_rect(center=medium_rect.center))
        screen.blit(fast_text, fast_text.get_rect(center=fast_rect.center))
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2)  # Draw checkbox outline
        if remove_delay:
            pygame.draw.line(screen, BLACK, checkbox_rect.topleft, checkbox_rect.bottomright, 3) #Draw check mark.
            pygame.draw.line(screen, BLACK, checkbox_rect.bottomleft, checkbox_rect.topright, 3)
        pygame.draw.rect(screen, BLACK, endless_checkbox_rect, 2)  # Draw checkbox outline
        if endless_mode:
            pygame.draw.line(screen, BLACK, endless_checkbox_rect.topleft, endless_checkbox_rect.bottomright, 3) #Draw check mark.
            pygame.draw.line(screen, BLACK, endless_checkbox_rect.bottomleft, endless_checkbox_rect.topright, 3)

        # Checkbox label
        endless_text = font.render("Endless Mode", True, BLACK)
        screen.blit(endless_text, (endless_checkbox_rect.right + 5, endless_checkbox_rect.top - 5))

        # Checkbox label
        delay_text = font.render("Remove Start Delay", True, BLACK)
        screen.blit(delay_text, (checkbox_rect.right + 5, checkbox_rect.top - 5))
    elif not game_over:
        if time.time() - round_start_time > round_delay:
            move_circles()
            remove_offscreen_circles()
        draw_circles()

        round_text = font.render(f"Round: {round_number - 1}", True, BLACK)
        collision_text = font.render(f"Collisions: {collisions}", True, BLACK)
        screen.blit(round_text, (10, 10))
        screen.blit(collision_text, (10, 50))

        if not circles:  # Check if all circles are gone (round ended)
            if endless_mode:
                if round_number > 8:
                    round_number = 2  # Loop back to round 2
                else:
                    start_new_round()  # Start the next round
            else:
                if round_number > 8:
                    game_over = True  # End the game
                else:
                    start_new_round()  # Start the next round
    else:
        #Game over screen
        game_over_text = font.render("Game Over", True, BLACK)
        collisions_text = font.render(f"Total Collisions: {collisions}", True, BLACK)
        pygame.draw.rect(screen, GRAY, restart_button)
        restart_text = font.render("Restart", True, BLACK)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        collisions_rect = collisions_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        restart_rect = restart_text.get_rect(center=restart_button.center)

        screen.blit(game_over_text, game_over_rect)
        screen.blit(collisions_text, collisions_rect)
        screen.blit(restart_text, restart_rect)
        
        correct_math_text = font.render(f"Correct Math: {correct_math_answers}", True, BLACK)
        incorrect_math_text = font.render(f"Incorrect Math: {incorrect_math_answers}", True, BLACK)
        correct_math_rect = correct_math_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        incorrect_math_rect = incorrect_math_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(correct_math_text, correct_math_rect)
        screen.blit(incorrect_math_text, incorrect_math_rect)

    # Draw math bar
    pygame.draw.rect(screen, GRAY, math_bar_rect)

    # Draw math problem
    if math_problem:
        problem_text = font.render(math_problem, True, BLACK)
        problem_rect = problem_text.get_rect(center=(WIDTH // 2, HEIGHT - math_bar_height // 1.5))
        screen.blit(problem_text, problem_rect)
        option_spacing = WIDTH // 4
        vertical_spacing = 160

        # Draw math options
        option_spacing = WIDTH // 4
        for i, option in enumerate(math_options):
            option_text = font.render(f"{option}", True, BLACK)
            option_rect = option_text.get_rect(center=(option_spacing * (i + 0.5), HEIGHT - math_bar_height // 4))
            screen.blit(option_text, option_rect)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()