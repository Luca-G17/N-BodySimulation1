import pygame
import math

pygame.init()

clock = pygame.time.Clock()

WIDTH = 1020
HEIGHT = 800

win = pygame.display.set_mode((WIDTH, HEIGHT))
colours = [[0, 0, 0], [0, 255, 0], [0, 0, 128], [255, 128, 0], [0, 153, 0]]
# white, red, green, cyan, magenta, orange, dark green
WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
RED = [255, 0, 0]

win.fill(WHITE)

Ar = pygame.image.load('ArrowEdited.png')

velocity = 3


class Arrow(object):
    def __init__(self, x, y, visible):
        self.y = y
        self.x = x
        self.visible = visible
        self.angle = 0
        self.arrow_image = Ar
        self.rotated = Ar
        self.distance = 0

    def follow_cursor(self, body_x, body_y):
        pos = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(body_y - pos[1], body_x - pos[0]))
        self.rotated = image_rot(self.arrow_image, 180 - self.angle)
        self.x = body_x - 32
        self.y = body_y - 32
        self.visible = True
        self.distance = math.sqrt(abs(pos[1]) ** 2 + abs(pos[0]) ** 2)

    def draw(self, win):
        if self.visible:
            win.blit(self.rotated, (self.x, self.y))


class Body(object):
    def __init__(self, x, y, radius, colour):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.vel_angle = 540
        self.x_vel = 0
        self.y_vel = 0
        self.forces = []
        self.physics = False

    def move(self):
        if self.vel_angle != 540:
            self.x_vel += velocity * math.cos(math.radians(180 - self.vel_angle))
            self.y_vel += velocity * math.sin(math.radians(180 - self.vel_angle)) * -1
            self.vel_angle = 540
        self.x += self.x_vel
        self.y += self.y_vel

    def draw(self, win):
        self.move()
        pygame.draw.circle(win, self.colour, (round(self.x), round(self.y)), self.radius)


class GravBody(Body):
    def __init__(self, gravity_radius, gravity, x, y, colour, radius):
        super().__init__(x, y, radius, colour)
        self.gravity_radius = gravity_radius
        self.gravity = gravity


class Trail(object):
    def __init__(self, x, y, radius, colour):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.age = 0

    def age_inc(self):
        self.age += 1

    def draw(self, win):
        self.age_inc()
        pygame.draw.circle(win, self.colour, (round(self.x), round(self.y)), self.radius)


def image_rot(image, angle):
    rot_image = pygame.transform.rotate(image, angle)
    return rot_image


def redraw_window():
    win.fill(WHITE)

    # pygame.draw.rect(win, (255, 0, 0), (100, 100, 20, 20))
    # pygame.draw.circle(win, (255, 0, 0), (50, 50), 20)
    # win.blit(Ar, (40, 40))
    # win.blit(image_rot(Ar, 270), (8, 72))
    # rot_image = pygame.transform.rotate(Ar, 90)
    # win.blit(rot_image, (40, 40))
    # now = float(str(datetime.datetime.now())[18:22])
    # text = font.render('VELOCITY :', , 1, (0, 0, 0))
    # win.blit(text, (340, 10))
    offset = 0
    for item in bodies:
        Body.draw(item, win)
        text = font.render('VELOCITY : ' + str(round(math.hypot(item.x_vel, item.y_vel), 4)) , 1, item.colour)
        win.blit(text, (10, 10 + offset))
        offset += 30

    Arrow.draw(Pointer, win)
    if not hide_trails:
        for item in trail_dots:
            Trail.draw(item, win)
            if item.age == 300:
                trail_dots.pop(trail_dots.index(item))

    pygame.display.update()


# Main Loop
hide_trails = False
hide_timer = 0
font = pygame.font.SysFont('roboto', 30, False, False)
MaxFps = 90
Pointer = Arrow(0, 0, False)
body_placement = 0
bodies = []
trail_dots = []
grav_bodies = []
cycles = 0
grav_placement = False
colour_num = 0
run = True
while run:
    clock.tick(MaxFps)
    if hide_timer > 0:
        if hide_timer > 90:
            hide_timer = 0
        else:
            hide_timer += 1
    if grav_placement:
        cycles += 1
        if cycles == 90:
            cycles = 0
            grav_placement = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if pygame.mouse.get_pressed()[0] and not body_placement:
        radius = 10
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]
        body_placement = True
        bodies.append(Body(pos[0], pos[1], radius, colours[colour_num]))
        if colour_num == len(colours) - 1:
            colour_num = 0
        else:
            colour_num += 1
    elif keys[pygame.K_SPACE] and not grav_placement and cycles == 0 and not body_placement:
        radius = 20
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]
        grav_placement = True
        grav_bodies.append(GravBody(4000, 15, pos[0], pos[1], RED, radius))
        bodies.append(grav_bodies[len(grav_bodies) - 1])
        bodies[len(bodies) - 1].physics = False
    elif keys[pygame.K_e] and not grav_placement and not body_placement:
        radius = 10
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]
        body_placement = True
        grav_bodies.append(GravBody(100, 1, pos[0], pos[1], RED, radius))
        bodies.append(grav_bodies[len(grav_bodies) - 1])
        bodies[len(bodies) - 1].physics = False

    if keys[pygame.K_q] and hide_timer == 0:
        hide_timer = 1
        if not hide_trails:
            hide_trails = True
        else:
            hide_trails = False
    if body_placement:
        Pointer.follow_cursor(x, y)
        if pygame.mouse.get_pressed()[2]:
            body_placement = False
            Pointer.visible = False
            bodies[len(bodies) - 1].vel_angle = Pointer.angle
            bodies[len(bodies) - 1].physics = True
    # Bouncing:
    '''
    for body in bodies:
        if body.x - body.radius < 0 or body.x + body.radius > WIDTH:
            body.x_vel = body.x_vel * -1
        if body.y + body.radius < 35 or body.y + body.radius > HEIGHT:
            body.y_vel = body.y_vel * -1
    '''
    for body in bodies:
        for grav_body in grav_bodies:
            hypotenuse = math.sqrt((body.x - grav_body.x) ** 2 + (body.y - grav_body.y) ** 2)
            if hypotenuse < grav_body.gravity_radius and hypotenuse != 0 and body.physics:
                k = (grav_body.radius ** 2) * grav_body.gravity
                gravity = k / (hypotenuse ** 2)
                body.x_vel += gravity * ((grav_body.x - body.x) / ((abs(grav_body.x - body.x)) + (abs(grav_body.y - body.y))))
                body.y_vel += gravity * ((grav_body.y - body.y) / ((abs(grav_body.x - body.x)) + (abs(grav_body.y - body.y))))

    for body in bodies:
        trail_dots.append(Trail(body.x, body.y, 2, BLUE))

        if math.sqrt((body.x_vel ** 2) + (body.y_vel ** 2)) > 30:
            bodies.pop(bodies.index(body))
            for item in grav_bodies:
                if item.x == body.x and item.y == body.y and item.x_vel == body.x_vel:
                    grav_bodies.pop(grav_bodies.index(item))

    redraw_window()

pygame.QUIT
