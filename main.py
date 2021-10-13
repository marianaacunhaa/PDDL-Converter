import os
import pygame, sys
import numpy as np
from copy import deepcopy

pygame.init()

BOARD_WIDTH = 600
BOARD_HEIGHT = 600
MENU_HEIGHT = 80
LINE_WIDTH = 2
BOARD_ROWS = 5
BOARD_COLS = 5

# Colors (rgb format)
BACKGROUND_COLOR = (192,192,192)
LINE_COLOR = (128,128,128)
BLACK = (0,0,0)
WHITE = (255,255,255)
ROBOT_COLOR = (255,153,153)
MODULE_COLOR_SOFT = (0,128,255)
MODULE_COLOR_DARK = (0,0,204)
LOCATION_COLOR = (160,160,160)

# Button
BUTTON_X_COORDINATES = [int(BOARD_WIDTH*0.75), int(BOARD_WIDTH*0.75) + int(BOARD_WIDTH*0.25)]
BUTTON_Y_COORDINATES = [int(BOARD_HEIGHT + MENU_HEIGHT*0.25), int(BOARD_HEIGHT + MENU_HEIGHT*0.25) + int(MENU_HEIGHT*0.5)]


def float_range(start: float, stop: float, step: float):
    float_range_array = np.arange(start, stop, step)
    return list(float_range_array)


def draw_instructions(step: int = 1):
    # Instructions
    if step == 1:
        step_title = "STEP 1:"
        instructions = "Please mark the initial position of all modules"
        click = "(Click OK after marking all the modules)"
    elif step == 2:
        step_title = "STEP 2:"
        instructions = "Please mark the initial position of the robot"
        click = "(Then click OK to continue)"
    elif step == 3:
        step_title = "STEP 3:"
        instructions = "Please mark the goal position of all modules"
        click = "(Click OK after marking all final positions)"
    else:
        step_title = ""
        instructions = "PDDL files have been generated!"
        click = ""

    # Draw menu area on the bottom of screen
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, BOARD_HEIGHT, BOARD_WIDTH, MENU_HEIGHT))

    # Display instructions
    instructions_font = pygame.font.SysFont("Times New Roman", int(MENU_HEIGHT*0.25))

    step_label = instructions_font.render(step_title, 1, WHITE)
    screen.blit(step_label, (int(BOARD_WIDTH*0.05), int(BOARD_HEIGHT + MENU_HEIGHT*0.1)))

    instructions_label = instructions_font.render(instructions, 1, WHITE)
    screen.blit(instructions_label, (int(BOARD_WIDTH*0.05), int(BOARD_HEIGHT + MENU_HEIGHT*0.35)))

    click_label = instructions_font.render(click, 1, WHITE)
    screen.blit(click_label, (int(BOARD_WIDTH*0.05), int(BOARD_HEIGHT + MENU_HEIGHT*0.65)))
    
    #  Draw button
    pygame.draw.rect(screen, WHITE, pygame.Rect(int(BOARD_WIDTH*0.75), int(BOARD_HEIGHT + MENU_HEIGHT*0.25), int(BOARD_WIDTH*0.2), int(MENU_HEIGHT*0.5)), 2)

    # Display OK button on the menu area
    button_font = pygame.font.SysFont("Times New Roman", int(MENU_HEIGHT*0.4))
    button_label = button_font.render("OK", 1, WHITE)
    screen.blit(button_label, (int(BOARD_WIDTH*0.815), int(BOARD_HEIGHT + MENU_HEIGHT*0.3)))


def label_board():
    # Display location labels
    loc = 1
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            font = pygame.font.SysFont("Times New Roman", int(vertical_interval*0.2))
            location_label = font.render(f"L{loc}", 1, LOCATION_COLOR)
            screen.blit(location_label, (int(col * horizontal_interval + horizontal_interval*0.4), int(row * vertical_interval + vertical_interval*0.35)))
            
            loc += 1


def draw_lines(width: int = 3, height: int = 3):
    # Vertical lines
    vertical_interval = BOARD_WIDTH / width

    for n in float_range(vertical_interval, BOARD_WIDTH, vertical_interval):
        pygame.draw.line(screen, LINE_COLOR, (n, 0), (n, BOARD_HEIGHT), LINE_WIDTH)

    # Horizontal lines
    horizontal_interval = BOARD_HEIGHT / height
    
    for n in float_range(horizontal_interval, BOARD_HEIGHT, horizontal_interval):
        pygame.draw.line(screen, LINE_COLOR, (0, n), (BOARD_WIDTH, n), LINE_WIDTH)

    return vertical_interval, horizontal_interval


def draw_figures():
    loc = 1
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            # If module 1 marked this square
            if board[row][col] == module:
                # Draw robot
                if step == 2:
                    pygame.draw.circle(screen, ROBOT_COLOR, (int(col * horizontal_interval + horizontal_interval / 2), int(row * vertical_interval + vertical_interval / 2)), int(vertical_interval/2 - vertical_interval*0.1), int(vertical_interval/2 - vertical_interval*0.1))
                    
                    # Display module number
                    font = pygame.font.SysFont("Times New Roman", int(vertical_interval*0.3))
                    module_label = font.render(str(module), 1, WHITE)
                    screen.blit(module_label, (int(col * horizontal_interval + horizontal_interval*0.4), int(row * vertical_interval + vertical_interval*0.35)))

                # Draw modules
                else:
                    pygame.draw.rect(screen, MODULE_COLOR_DARK if step == 1 else MODULE_COLOR_SOFT, pygame.Rect(col * horizontal_interval + LINE_WIDTH, row * vertical_interval + LINE_WIDTH, horizontal_interval - LINE_WIDTH, vertical_interval - LINE_WIDTH))
                    
                    # Display module number
                    font = pygame.font.SysFont("Times New Roman", int(vertical_interval*0.3))
                    module_label = font.render(str(module), 1, WHITE)
                    screen.blit(module_label, (int(col * horizontal_interval + horizontal_interval*0.4), int(row * vertical_interval + vertical_interval*0.35)))
                
                # Display location label at the bottom of module
                font = pygame.font.SysFont("Times New Roman", int(vertical_interval*0.15))
                location_label = font.render(f"L{loc}", 1, LOCATION_COLOR)
                screen.blit(location_label, (int(col * horizontal_interval + horizontal_interval*0.7), int(row * vertical_interval + vertical_interval*0.75)))
            
            loc += 1


def mark_square(row, col, module):
    # In step 3: do not allow placing more modules than were placed in the beginning
    if step == 3 and module > modules_total:
        return

    board[row][col] = module


def available_square(row, col):
    # If square is empty returns True
    return board[row][col] == 0


def board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if available_square(row, col): 
                return False

    return True


def reset_board():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0


def create_location_matrix():
    location = 1
    location_matrix = np.zeros((BOARD_ROWS, BOARD_COLS))

    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            location_matrix[row][col] = location
            location += 1

    return location_matrix


def translate_output():
    print(module_init_pos)
    print("============================")
    print(robot_init_pos)
    print("============================")
    print(module_goal_pos)
    print("============================")
    print(modules_total)
    print("============================")
    print(robots_total)

    robots = "r1"
    modules = "m1"
    locations = "l1"
    empty_robots = "(empty r1)\n\t\t\t"

    for n in range(2, robots_total+1):
        robots += f" r{n}"
        empty_robots += f"(empty r{n})\n\t\t\t"

    for n in range(2, modules_total+1):
        modules += f" m{n}"

    for n in range(2, BOARD_ROWS*BOARD_COLS + 1):
        locations += f" l{n}"

    # Initial and goal module location
    location = 1
    init_module_location = ""
    goal_module_location = ""
    init_robot_location = ""
    clear_location = ""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            # Initial position of modules
            if module_init_pos[row][col] != 0:
                init_module_location += f"(on m{int(module_init_pos[row][col])} l{location})\n\t\t\t"
            
            # Clear locations
            else:
                clear_location += f"(clear l{location})\n\t\t\t"

            # Initial position of robots
            if robot_init_pos[row][col] != 0:
                # Find one of all 4 possible adjacent locations
                adj_row = row
                adj_col = col
                if row != 0:
                    adj_row = row - 1
                elif row != BOARD_ROWS - 1:
                    adj_row = row + 1
                elif col != 0:
                    adj_col = col - 1
                elif col != BOARD_COLS - 1:
                    adj_col = col + 1

                init_robot_location += f"(near r{int(robot_init_pos[row][col])} l{int(location_matrix[adj_row][adj_col])})\n\t\t\t"

            # Goal position of modules
            if module_goal_pos[row][col] != 0:
                goal_module_location += f"(on m{int(module_goal_pos[row][col])} l{location})\n\t\t\t"
            location += 1

    # Location adjacency
    location_adjacency = ""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            loc = location_matrix[row][col]
            
            # All 4 possible adjacent locations
            if row != 0:
                adj_loc1 = location_matrix[row-1][col]
                location_adjacency += f"(adjacent l{int(loc)} l{int(adj_loc1)})\n\t\t\t"
            if row != BOARD_ROWS - 1:
                adj_loc2 = location_matrix[row+1][col]
                location_adjacency += f"(adjacent l{int(loc)} l{int(adj_loc2)})\n\t\t\t"
            if col != 0:
                adj_loc3 = location_matrix[row][col-1]
                location_adjacency += f"(adjacent l{int(loc)} l{int(adj_loc3)})\n\t\t\t"
            if col != BOARD_COLS - 1:
                adj_loc4 = location_matrix[row][col+1]
                location_adjacency += f"(adjacent l{int(loc)} l{int(adj_loc4)})\n\t\t\t"


    return robots, modules, locations, init_module_location, goal_module_location, location_adjacency, clear_location, init_robot_location, empty_robots


def generate_output():
    print("Generate output file")

    if os.path.isfile('./problem.pddl'):
        f = open("problem.pddl", "w")
    else:
        f = open("problem.pddl", "x")

    robots, modules, locations, init_module_location, goal_module_location, location_adjacency, clear_location, init_robot_location, empty_robots = translate_output()

    txt_to_output = f"""
    (define (problem prob)
        (:domain space_assembly)
        (:objects {robots} - robot
                  {modules} - module
                  {locations} - location
        )
        (:init
            {empty_robots}
            {init_robot_location}
            {clear_location}
            (= (act-cost) 0)
            (= (extern) 0)

            ; MODULE LOCATION
            {init_module_location}
            ; LOCATION ADJACENCY
            {location_adjacency}
        )
        (:goal
        (and
            {goal_module_location}
            {empty_robots}
            (>= (act-cost) 0) 
        ))
    )

    """

    f.write(txt_to_output)
    f.close()


# MAIN CODE
screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT + MENU_HEIGHT))
pygame.display.set_caption('PDDL Problem Converter')
screen.fill(BACKGROUND_COLOR)

# Board
draw_instructions(step=1)
vertical_interval, horizontal_interval = draw_lines(BOARD_ROWS, BOARD_COLS)
label_board()

board = np.zeros((BOARD_ROWS, BOARD_COLS))
print(board)
module_init_pos = np.zeros((BOARD_ROWS, BOARD_COLS))
module_goal_pos = np.zeros((BOARD_ROWS, BOARD_COLS))
robot_init_pos = np.zeros((BOARD_ROWS, BOARD_COLS))
location_matrix = create_location_matrix()

# Starting module
module = 1
modules_total = 0
robots_total = 0

# Steps:
# 1 - mark initial position of modules
# 2 - mark initial position of robot
# 3 - mark goal position of modules
step = 1

# Mainloop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x = event.pos[0] # get x coordinate
            mouse_y = event.pos[1] # get y coordinate

            # Clicking "OK"
            if mouse_y > BOARD_HEIGHT:
                if mouse_x > BUTTON_X_COORDINATES[0] and mouse_x < BUTTON_X_COORDINATES[1] and mouse_y > BUTTON_Y_COORDINATES[0] and mouse_y < BUTTON_Y_COORDINATES[1]:
                    print("Clicked OK")
                    # Save position coordinates for each step
                    if step == 1:
                        if module <= 2:
                            print(f"Mark at least 2 modules! Missing {2 - (module - 1)} modules")
                            break

                        module_init_pos = deepcopy(board)

                        # Save total amount of placed modules and reset module variable
                        modules_total = module - 1
                        print(f"modules_total: {modules_total}")
                        module = 1

                    elif step == 2:
                        robot_init_pos = deepcopy(board)

                        # Save total amount of robots and reset module variable
                        robots_total = module - 1
                        print(f"robots_total: {robots_total}")
                        module = 1

                    elif step == 3:
                        # Verify if all modules have their goal positions inidcated
                        if module <= modules_total:
                            print(f"Still missing goal postition of {modules_total - (module - 1)} modules")
                            break
                        
                        module_goal_pos = deepcopy(board)
                    
                        # TO DO: visualy clear all modules and robots from the board

                        print(f"step: {step}")
                        generate_output()

                    else:
                        pygame.quit()
                        sys.exit()
                        
                    reset_board()
                    step += 1
                    draw_instructions(step=step)
                else:
                    print("Clicked menu area")

            # Clicking on the board
            else: 
                clicked_row = int(mouse_y // vertical_interval)
                clicked_col = int(mouse_x // horizontal_interval)

                print(f"x: {clicked_row}")
                print(f"y: {clicked_col}")

                if available_square(clicked_row, clicked_col):
                    mark_square(clicked_row, clicked_col, module)
                    draw_figures()
                    module += 1
                    print(board)
             
    
    pygame.display.update()


# TO DO:
# 1 - imperdir que os robots possam ser escolhidos em cima de módulos
# 2 - [DONE] obrigar a escolher pelo menos 1 robot e pelo menos 2 módulos
# 3 - [DONE] adicionar legenda da location aos módulos
# 4 - fazer um segundo script que mostra uma simulação do plano (?)

# TO DO IN PDDL:
# problem.pddl:
# 1 - mudar o (near r l1) para (on r l1) e na action tem de se verificar as condições (on r l1) and (on m1 l2) and (adjacent l1 l2) para o robot poder pegar no módulo m1
# 2 - TENS DE CRIAR UMA ACTION "unload"