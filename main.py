import math
import time
import random
import pygame

from pygame.math import Vector2

SCREEN_WIDTH = 600; SCREEN_LENGTH = 700

class obstacle: #series of rectangles
    def __init__(self, x, y, width, length):
        self.position = Vector2(x, y)
        self.width = width; self.length = length

class environment:
    def __init__(self, width = SCREEN_WIDTH, length = SCREEN_LENGTH, obstacles = [], start_area = (50, 50, 50, 50), end_area = (SCREEN_WIDTH-50, SCREEN_LENGTH-50, 50, 50)):
        #passed variables
        self.width = width; self.length = length
        self.obstacles = obstacles
        self.start_x, self.start_y, self.start_width, self.start_length =  start_area #starting and ending areas
        self.end_x, self.end_y, self.end_width, self.end_length =  end_area #starting and ending areas


        #reset variables
        self.width_init = width; self.length_init = length
        self.obstacles_init = obstacles
    def reset(self):
        self.width = self.width_init; self.length = self.length_init

    def add_obstacles(self, obstacles):
        self.obstacles = self.obstacles.extend(obstacles)

    def point_on_obstacle(self, x, y):
        if not (0 < x < self.width and 0 < y < self.length):
            return True
        for ob in self.obstacles:
            if ob.position.x - ob.width/2 < x < ob.position.x + ob.width/2 and ob.position.y - ob.length/2 < y < ob.position.y + ob.length/2:
                return True
        else:
            return False

    def line_on_obstacle(self, x1, y1, x2, y2):
        distance = ((x2-x1)**2 + (y2-y1)**2)**.5
        for i in range(int(distance)+1):
            if self.point_on_obstacle(x1+i*(x2-x1)/distance, y1+i*(y2-y1)/distance):
                return True
        else:
            return False

    def point_on_end_area(self, x, y):
        if self.end_x - self.end_width/2 < x < self.end_x + self.end_width/2 and self.end_y - self.end_length/2 < y < self.end_y + self.end_length/2:
            return True
        else:
            return False

    def line_on_end_area(self, x1, x2, y1, y2):
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5
        for i in range(int(distance) + 1):
            if self.point_on_end_area(x1 + i * (x2 - x1) / distance, y1 + i * (y2 - y1) / distance):
                return True
        else:
            return False




class agent:
    def __init__(self, x = 50, y = 50, car_width = 20, car_length = 40, max_acc = 2, min_acc = -2, max_steering = 30, max_velocity = 100, friction = 0.08):
        #passed variables
        self.car_width = car_width; self.car_length = car_length
        self.max_acc = max_acc; self.min_acc = min_acc #accelerator and brake
        self.max_steering = max_steering
        self.max_velocity = max_velocity


        #state variables
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.orientation = 90
        self.acceleration = 0.0
        self.steering = 0.0

        #reset variables

        self.car_width_init = self.car_width + 0; self.car_length_init = self.car_length + 0
        self.max_acc_init = self.max_acc + 0; self.min_acc_init = self.min_acc + 0
        self.max_steering_init = self.max_steering + 0
        self.max_velocity_init = self.max_velocity + 0

        self.position_init = self.position + (0, 0)
        self.velocity_init = self.velocity + (0, 0)
        self.orientation_init = self.orientation + 0
        self.acceleration_init = self.acceleration + 0
        self.steering_init = self.steering + 0

    def reset(self):
        self.position = self.position_init + (0, 0)
        self.velocity = self.velocity_init + (0, 0)
        self.orientation = self.orientation_init + 0
        self.acceleration = self.acceleration_init + 0
        self.steering = self.steering_init + 0

        self.car_width = self.car_width_init + 0; self.car_length = self.car_length_init + 0
        self.max_acc = self.max_acc_init + 0; self.min_acc = self.min_acc_init + 0
        self.max_steering = self.max_steering_init + 0
        self.max_velocity = self.max_velocity_init + 0



    def get_input(self, environment): #will have depth sensors in 8 directions surrounding the car
        distances = [0, 0, 0, 0, 0, 0, 0, 0] #0, 45, 90, 135, 180, 225, 270, 315
        degrees = [0, 45, 90, 135, 180, 225, 270, 315]
        for i in range(8):
            eval_pos_x, eval_pos_y = self.position.x, self.position.y
            while not environment.point_on_obstacle(eval_pos_x, eval_pos_y):
                eval_pos_x += 1*math.cos(math.radians(self.orientation + degrees[i])); eval_pos_y += 1*math.sin(math.radians(self.orientation + degrees[i]))

            distances[i] = ((eval_pos_x-self.position.x)**2 + (eval_pos_y-self.position.y)**2)**.5

        return [int(num) for num in distances]

    def is_collision(self, environment):

        #get the 4 corners that make up the rectangel of the car
        car_c1 = (self.position.x + self.car_width/2*math.cos(self.orientation), self.position.y + self.car_length/2*math.sin(self.orientation))
        car_c2 = (self.position.x + self.car_width/2*math.cos(self.orientation), self.position.y - self.car_length/2*math.sin(self.orientation))
        car_c3 = (self.position.x - self.car_width/2*math.cos(self.orientation), self.position.y + self.car_length/2*math.sin(self.orientation))
        car_c4 = (self.position.x - self.car_width/2*math.cos(self.orientation), self.position.y - self.car_length/2*math.sin(self.orientation))

        if environment.line_on_obstacle(car_c1[0], car_c1[1], car_c2[0], car_c2[1]) or \
            environment.line_on_obstacle(car_c2[0], car_c2[1], car_c3[0], car_c3[1]) or \
            environment.line_on_obstacle(car_c3[0], car_c3[1], car_c4[0], car_c4[1]) or \
            environment.line_on_obstacle(car_c4[0], car_c4[1], car_c1[0], car_c1[1]):
            return True
        else:
            return False

    def is_at_end_area(self, environment):
        # get the 4 corners that make up the rectangel of the car
        car_c1 = (self.position.x + self.car_width / 2 * math.cos(self.orientation),
                  self.position.y + self.car_length / 2 * math.sin(self.orientation))
        car_c2 = (self.position.x + self.car_width / 2 * math.cos(self.orientation),
                  self.position.y - self.car_length / 2 * math.sin(self.orientation))
        car_c3 = (self.position.x - self.car_width / 2 * math.cos(self.orientation),
                  self.position.y + self.car_length / 2 * math.sin(self.orientation))
        car_c4 = (self.position.x - self.car_width / 2 * math.cos(self.orientation),
                  self.position.y - self.car_length / 2 * math.sin(self.orientation))

        if environment.line_on_end_area(car_c1[0], car_c1[1], car_c2[0], car_c2[1]) or \
            environment.line_on_end_area(car_c2[0], car_c2[1], car_c3[0], car_c3[1]) or \
            environment.line_on_end_area(car_c3[0], car_c3[1], car_c4[0], car_c4[1]) or \
            environment.line_on_end_area(car_c4[0], car_c4[1], car_c1[0], car_c1[1]):
            return True
        else:
            return False


        #creates rays which iteratively increase and stops until it hits an obstacle

    def drive(self, acc, turn):
        self.acceleration = acc
        self.steering = turn
        """self.orientation += turn
        self.speed = max(self.speed + acc - self.friction*(self.speed**2), 0) #to make sure speed is not negative b/c of friction
        self.x += math.cos(self.orientation*math.pi/180)*self.speed; self.y += math.sin(self.orientation*math.pi/180)*self.speed
        print(self.orientation, math.cos(self.orientation*math.pi/180)*self.speed, math.sin(self.orientation*math.pi/180)*self.speed)

        --
        if turn != 0:
            turning_radius = self.car_length/ math.sin(math.radians(turn))
            angular_velocity = self.speed/turning_radius
        else:
            angular_velocity = 0"""

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)

        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.car_length / math.sin(math.radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(self.orientation) * dt
        self.orientation += (math.degrees(angular_velocity) * dt)

        self.orientation %= 360


#GUI stuff
class GUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGTH))

    def draw(self, game, environment, agent):
        GREEN = (0, 255, 0)
        self.screen.fill(GREEN)

        self.draw_env(environment)
        self.draw_car(agent)
        self.draw_lines(environment, agent)
        self.draw_info(game, environment, agent)

        pygame.display.flip()
    def draw_env(self, environment):
        RED = (255, 0, 0)
        BLUE = (0, 0, 255)

        #draw start area
        pygame.draw.rect(self.screen, BLUE, pygame.Rect(
            environment.start_x - environment.start_width/2,
            environment.start_y - environment.start_length/2,
            environment.start_width,
            environment.start_length
        ))

        #draw end area
        pygame.draw.rect(self.screen, BLUE, pygame.Rect(
            environment.end_x - environment.end_width / 2,
            environment.end_y - environment.end_length / 2,
            environment.end_width,
            environment.end_length
        ))

        #draw obstacles
        for obstacle in environment.obstacles:
            rect = pygame.Rect(obstacle.position.x-obstacle.width/2,
                               obstacle.position.y-obstacle.length/2,
                               obstacle.width,
                               obstacle.length)

            pygame.draw.rect(self.screen, RED, rect)


    def draw_car(self, agent):
        YELLOW = (255, 255, 0)

        def draw_rotated_rect(screen, x, y, width, height, color, rotation=0):
            """Draw a rectangle, centered at x, y.

            Arguments:
              x (int/float):
                The x coordinate of the center of the shape.
              y (int/float):
                The y coordinate of the center of the shape.
              width (int/float):
                The width of the rectangle.
              height (int/float):
                The height of the rectangle.
              color (str):
                Name of the fill color, in HTML format.
            """
            points = []

            # The distance from the center of the rectangle to
            # one of the corners is the same for each corner.
            radius = math.sqrt((height / 2) ** 2 + (width / 2) ** 2)

            # Get the angle to one of the corners with respect
            # to the x-axis.
            angle = math.atan2(height / 2, width / 2)

            # Transform that angle to reach each corner of the rectangle.
            angles = [angle, -angle + math.pi, angle + math.pi, -angle]

            # Convert rotation from degrees to radians.
            rot_radians = (math.pi / 180) * rotation

            # Calculate the coordinates of each point.
            for angle in angles:
                y_offset = -1 * radius * math.sin(angle + rot_radians)
                x_offset = radius * math.cos(angle + rot_radians)
                points.append((x + x_offset, y + y_offset))

            pygame.draw.polygon(screen, color, points)

        #draw car
        draw_rotated_rect(self.screen,
            agent.position.x,
            agent.position.y,
            agent.car_length,
            agent.car_width,
        YELLOW, (-agent.orientation))

    def draw_lines(self, environment, agent):

        PURPLE = (255, 0, 255)

        #draw lines
        distances = agent.get_input(environment)
        degrees =  [0, 45, 90, 135, 180, 225, 270, 315]
        for i in range(8):
            line_end_pos_x = agent.position.x+distances[i]*math.cos(math.radians(agent.orientation+degrees[i]))
            line_end_pos_y = agent.position.y + distances[i] * math.sin(math.radians(agent.orientation + degrees[i]))
            pygame.draw.line(self.screen, PURPLE, (agent.position.x, agent.position.y), (line_end_pos_x, line_end_pos_y))

    def draw_info(self, game, environment, agent):
        my_font = pygame.font.SysFont('Arial', 16)

        car_info1 = my_font.render(f'Agent: speed={round(agent.velocity.x, 1)}, orientation={round(agent.orientation, 0)}', False, (0, 0, 0))
        car_info1_rect = car_info1.get_rect()
        car_info1_rect.right = SCREEN_WIDTH-10
        car_info1_rect.top = 10

        car_info2 = my_font.render(f'Distances: {agent.get_input(environment)}', False, (0, 0, 0))
        car_info2_rect = car_info2.get_rect()
        car_info2_rect.right = SCREEN_WIDTH-10
        car_info2_rect.top = 30

        car_info3 = my_font.render(f'Success/Attempts: {game.successes}/{game.attempts}', False, (0, 0, 0))
        car_info3_rect = car_info3.get_rect()
        car_info3_rect.right = SCREEN_WIDTH - 10
        car_info3_rect.top = 50

        self.screen.blit(car_info1, car_info1_rect)
        self.screen.blit(car_info2, car_info2_rect)
        self.screen.blit(car_info3, car_info3_rect)

class game:
    def __init__(self):
        self.successes = 0
        self.attempts = 0
    def add_attempt(self, success=False):
        self.attempts += 1
        self.successes += (1 if success else 0)

if __name__ == "__main__":
    myGUI = GUI()
    myGame = game()
    myEnvironment = environment(obstacles = [obstacle(100, 200, 50, 50), obstacle(300, 300, 50, 50), obstacle(500, 100, 50, 50), obstacle(200, 400, 50, 50)])
    myAgent = agent()

    while True:

        myAgent.drive(20, random.randint(-8, 0))
        myAgent.update(0.04)
        time.sleep(0.02)
        #draws
        myGUI.draw(myGame, myEnvironment, myAgent)
        if myAgent.is_collision(myEnvironment):
            myAgent.reset()
            myGame.add_attempt(success=False)
        if myAgent.is_at_end_area(myEnvironment):
            myAgent.reset()
            myGame.add_attempt(success=True)
        if pygame.event.poll().type == pygame.QUIT:
            pygame.quit()
