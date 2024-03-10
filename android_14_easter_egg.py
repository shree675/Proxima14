import numpy as np
import pygame
import math
import time
import random

PI = math.pi


class Game:

    def __init__(self):
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.orange = (255, 160, 0)
        self.light_violet = (207, 159, 255)
        self.grey = (88, 88, 88)
        self.light_green = (144, 238, 144)
        self.dark_blue = (0, 25, 150)
        self.black_ship_surface = (10, 10, 10)
        self.red = (150, 10, 10)
        self.orbit_green = (98, 188, 184)

        pygame.init()
        self.font1 = pygame.font.SysFont('comicsancms', 23)
        self.screen_size = (1500, 780)
        self.space_size = (200000, 200000)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.frame_rate = 180
        self.boost_factor = self.frame_rate / 40
        self.running = True
        self.spaceship = None
        self.discovered_bodies = 0

        self.spaceship_position = tuple([x / 2 for x in self.screen_size])
        self.planets = self.generate_planets()

    def generate_planets(self):
        return [
            {
                "center": (self.space_size[0] // 2 + self.screen_size[0] // 2 + 45000, self.space_size[1] // 2 + self.screen_size[1] // 2 + 45000),
                "radius": 600.0,
                "mass": 10,
                "isStar": False,
                "orbit_speed": -6,
                "visited": False,
                "details": {"BODY": "Proxima Centauri c", "TYPE": "Super Earth", "ATMO": "Unknown", "TEMP": "39"}
            },
            {
                "center": (self.space_size[0] // 2 + self.screen_size[0] // 2 + 30000, self.space_size[1] // 2 + self.screen_size[1] // 2 - 30000),
                "radius": 400.0,
                "mass": 7,
                "isStar": False,
                "orbit_speed": 5,
                "visited": False,
                "details": {"BODY": "Proxima Centauri b", "TYPE": "Super Earth", "ATMO": "Irradiated", "TEMP": "234"}
            },
            {
                "center": (self.space_size[0] // 2 + self.screen_size[0] // 2 + 10000, self.space_size[1] // 2 + self.screen_size[1] // 2 - 10000),
                "radius": 200.0,
                "mass": 5,
                "isStar": False,
                "orbit_speed": 5,
                "visited": False,
                "details": {"BODY": "Proxima Centauri d", "TYPE": "Sub Earth", "ATMO": "Polar", "TEMP": "360"}
            },
            {
                "center": (self.space_size[0] // 2 + self.screen_size[0] // 2, self.space_size[1] // 2 + self.screen_size[1] // 2),
                "radius": 1000.0,
                "mass": 60,
                "isStar": True,
                "orbit_speed": 0,
                "details": {"STAR": "Proxima Centauri (HIP 70890)", "TYPE": "M", "RADIUS": "1000", "MASS": "2.4e+29"}
            }
        ]

    def blit_spaceship(self, px, py):
        self.ship_surface = pygame.Surface((16, 22))
        self.ship_surface.set_colorkey(self.black)
        color = self.white
        star = list(filter(lambda planet: planet["isStar"], self.planets))[0]
        if self.detect_collision(px, py, star["center"], star["radius"], False):
            color = self.black_ship_surface
        pygame.draw.rect(self.ship_surface, color, pygame.Rect(0, 0, 16, 24), 2, border_top_left_radius=8,
                         border_top_right_radius=8, border_bottom_left_radius=4, border_bottom_right_radius=4)
        pygame.draw.arc(self.ship_surface, color, pygame.Rect(1, 15, 14, 23), PI / 6, PI - PI / 6, 2)
        self.spaceship = self.ship_surface.get_rect()

    def render_spaceship(self, angle, exhaust):
        if exhaust:
            pygame.draw.rect(self.ship_surface, self.orange, pygame.Rect(6, 16, 4, 6), border_top_left_radius=2,
                             border_top_right_radius=2, border_bottom_left_radius=4, border_bottom_right_radius=4)
        else:
            pygame.draw.rect(self.ship_surface, self.black, pygame.Rect(6, 16, 4, 6), border_top_left_radius=2,
                             border_top_right_radius=2, border_bottom_left_radius=4, border_bottom_right_radius=4)

        rotated_spaceship = pygame.transform.rotate(self.ship_surface, angle)
        self.spaceship = rotated_spaceship.get_rect()
        self.spaceship.center = self.spaceship_position     # type: ignore
        self.screen.blit(rotated_spaceship, self.spaceship)

    def render_text(self, velocity, px, py, thrust):
        start = self.screen_size[1] - 20
        self.screen.blit(self.font1.render('VEL: {}'.format(int(velocity)), True, self.light_violet), (10, start))
        start -= 20
        self.screen.blit(self.font1.render('POS: <{}, {}>'.format(int(px), int(py)), True, self.light_violet), (10, start))
        start -= 20
        if thrust > 0:
            thrust = self.font1.render('THRUST: {}%'.format(int(thrust)), True, self.light_violet)
            self.screen.blit(thrust, (10, start))
        top_start = 20
        star_details = list(filter(lambda planet: planet["isStar"], self.planets))[0]["details"]
        for key, val in star_details.items():
            self.screen.blit(self.font1.render("{}: {}".format(key, val), True, self.light_violet), (10, top_start))
            top_start += 20
        self.screen.blit(self.font1.render("BODIES: {} / {}".format(self.discovered_bodies, len(self.planets) - 1), True,
                                           self.light_violet), (10, top_start))
        top_start += 20
        for planet in self.planets:
            if not planet["isStar"] and planet["visited"]:
                top_start += 30
                for key, val in planet["details"].items():
                    self.screen.blit(self.font1.render("{}: {}".format(key, val), True, self.light_violet), (10, top_start))
                    top_start += 20

    def detect_collision(self, px, py, center, radius, isStar):
        if isStar or px is None or py is None:
            return False
        return (((center[0] - px - 7 - self.screen_size[0] // 2) ** 2 + (center[1] - py - 10 - self.screen_size[1] // 2) ** 2) <= radius ** 2) or \
            (((center[0] - px + 7 - self.screen_size[0] // 2) ** 2 + (center[1] - py - 10 - self.screen_size[1] // 2) ** 2) <= radius ** 2) or \
            (((center[0] - px - 7 - self.screen_size[0] // 2) ** 2 + (center[1] - py + 10 - self.screen_size[1] // 2) ** 2) <= radius ** 2) or \
            (((center[0] - px + 7 - self.screen_size[0] // 2) ** 2 + (center[1] - py + 10 - self.screen_size[1] // 2) ** 2) <= radius ** 2)
    
    def gravitational_force(self, center, px, py, mass, radius):
        r = (self.screen_size[0] // 2 - center[0] + px)**2 + (self.screen_size[1] // 2 - center[1] + py)**2
        return 1000000 * mass / max(r, radius**2)

    def compute_velocity(self, velocity, vx, vy, angle, thrust, prev_time, px, py):
        ax = 0; ay = 0
        for planet in self.planets:
            vector_angle = 90 - math.degrees(math.atan((self.screen_size[1] // 2 - planet["center"][1] + py) / (self.screen_size[0] // 2 - planet["center"][0] + px)))
            if ((self.screen_size[0] // 2 - planet["center"][0] + px) < 0):
                vector_angle = vector_angle - 180
            ax += - self.gravitational_force(planet["center"], px, py, planet["mass"], planet["radius"]) * math.sin(PI * vector_angle / 180)
            ay += - self.gravitational_force(planet["center"], px, py, planet["mass"], planet["radius"]) * math.cos(PI * vector_angle / 180)
        ax += - thrust * math.sin(PI * angle / 180) * 2
        ay += - thrust * math.cos(PI * angle / 180) * 2
        if velocity <= 5000:
            vx = vx + ax * (time.time() - prev_time) * self.boost_factor
            vy = vy + ay * (time.time() - prev_time) * self.boost_factor
        velocity = math.sqrt(vx**2 + vy**2)
        return min(velocity, 5000), vx, vy

    def compute_position(self, px, py, vx, vy, prev_time):
        self.compute_planets_positions(prev_time)
        px += vx * (time.time() - prev_time) * self.boost_factor
        py += vy * (time.time() - prev_time) * self.boost_factor
        if px <= 0:
            vx = 0
            px = 0
        elif px >= self.space_size[0]:
            vx = 0
            px = self.space_size[0]
        if py <= 0:
            vy = 0
            py = 0
        elif py >= self.space_size[1]:
            vy = 0
            py = self.space_size[1]
        for planet in self.planets:
            if self.detect_collision(px, py, planet["center"], planet["radius"], planet["isStar"]):
                if planet["visited"] is False:
                    self.discovered_bodies += 1
                    planet["visited"] = True
                if vx < 0:
                    if planet["orbit_speed"] < 0:
                        px += 1
                    else:
                        px += 2.5
                else:
                    if planet["orbit_speed"] < 0:
                        px -= 2.5
                    else:
                        px -= 1
                if vy < 0:
                    if planet["orbit_speed"] < 0:
                        py += 1
                    else:
                        py += 2.5
                else:
                    if planet["orbit_speed"] < 0:
                        py -= 2.5
                    else:
                        py -= 1
                vx = - vx / 5
                vy = - vy / 5
                break
        return px, py, vx, vy
    
    def compute_planets_positions(self, prev_time):
        star = list(filter(lambda planet: planet["isStar"], self.planets))[0]
        for planet in self.planets:
            if not planet["isStar"]:
                px = planet["center"][0]
                py = planet["center"][1]
                vector_angle = 90 + math.degrees(math.atan((star["center"][1] - py) / (star["center"][0] - px)))
                if ((px - star["center"][0]) < 0):
                    vector_angle = vector_angle - 180
                speed = planet["orbit_speed"]
                vx = - speed * math.cos(PI * vector_angle / 180)
                vy = - speed * math.sin(PI * vector_angle / 180)
                planet["center"] = (planet["center"][0] + vx * (time.time() - prev_time) * self.boost_factor,
                                    planet["center"][1] + vy * (time.time() - prev_time) * self.boost_factor)

    def draw_grid(self, px, py):
        grid_size = 1000
        for i in range(self.space_size[0] // grid_size + 1):
            pygame.draw.line(self.screen, self.grey, (0, i * grid_size - py), (self.space_size[0], i * grid_size - py))
        for i in range(self.space_size[1] // grid_size + 1):
            pygame.draw.line(self.screen, self.grey, (i * grid_size - px, 0), (i * grid_size - px, self.space_size[1]))

    def draw_trail(self, px, py, trail):
        trail.append((px, py))
        for p in trail:
            self.screen.set_at((self.spaceship.center[0] + (p[0] - px), self.spaceship.center[1] + (p[1] - py)), self.light_green)

    def draw_planets(self, px, py):
        star = None
        for planet in self.planets:
            if planet["isStar"]:
                star = planet
                pygame.draw.circle(self.screen, self.white, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"], 0)
                pygame.draw.circle(self.screen, self.red, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"] + 200, 1)
                pygame.draw.circle(self.screen, self.red, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"] + 400, 1)
                pygame.draw.circle(self.screen, self.red, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"] + 800, 1)
            else:
                pygame.draw.circle(self.screen, self.white, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"], 1)
                pygame.draw.circle(self.screen, self.dark_blue, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"] + 200, 1)
                pygame.draw.circle(self.screen, self.dark_blue, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"] + 400, 1)
                pygame.draw.circle(self.screen, self.dark_blue, (planet["center"][0] - px, planet["center"][1] - py), planet["radius"] + 800, 1)
        # drawing orbits of planets
        for planet in self.planets:
            if not planet["isStar"]:
                radius = np.linalg.norm(np.array(star["center"]) - np.array(planet["center"]))
                pygame.draw.circle(self.screen, self.orbit_green, (star["center"][0] - px, star["center"][1] - py), radius, 1)

    def render_universe(self, px, py, trail):
        self.draw_grid(px, py)
        if (self.spaceship is not None):
            self.draw_trail(int(px), int(py), trail)
            self.draw_planets(px, py)

    def run(self):
        angle = (random.random() * 1000) % 360
        thrust = 0
        velocity = 0
        vx = 0
        vy = 0
        px = self.space_size[0] // 2 - 26200
        py = self.space_size[1] // 2 + 18500
        trail = []

        while self.running:
            prev_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

            press = pygame.key.get_pressed()
            if press[pygame.K_RIGHT]:
                angle -= 3.0
            if press[pygame.K_LEFT]:
                angle += 3.0
            if press[pygame.K_SPACE]:
                thrust = min(100, thrust + 0.5)
            else:
                thrust = 0

            self.clock.tick(self.frame_rate)
            self.screen.fill(self.black)

            self.render_universe(px, py, trail)
            self.blit_spaceship(px, py)
            self.render_spaceship(angle, True if thrust > 0 else False)

            velocity, vx, vy = self.compute_velocity(velocity, vx, vy, angle, thrust, prev_time, px, py)
            px, py, vx, vy = self.compute_position(px, py, vx, vy, prev_time)

            self.render_text(velocity, px, py, thrust)

            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
