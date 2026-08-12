import sys
import math
import time
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Aircraft:
    def __init__(self):
        self.pos = np.array([0.0, 60.0, 0.0], dtype=float)
        self.vel = np.array([0.0, 0.0, -30.0], dtype=float)
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.throttle = 0.3
        self.crashed = False
        self.mass = 1200.0
        self.wing_area = 16.2
        self.cl0 = 0.2
        self.cl_alpha = 5.0
        self.cd0 = 0.02
        self.cd_alpha = 0.4
        self.max_thrust = 12000.0

    def reset(self):
        self.__init__()

    def get_body_axes(self):
        cy = math.cos(self.yaw); sy = math.sin(self.yaw)
        cp = math.cos(self.pitch); sp = math.sin(self.pitch)
        cr = math.cos(self.roll); sr = math.sin(self.roll)
        Ry = np.array([[cy, 0.0, sy],
                       [0.0, 1.0, 0.0],
                       [-sy, 0.0, cy]], dtype=float)
        Rx = np.array([[1.0, 0.0, 0.0],
                       [0.0, cp, -sp],
                       [0.0, sp, cp]], dtype=float)
        Rz = np.array([[cr, -sr, 0.0],
                       [sr, cr, 0.0],
                       [0.0, 0.0, 1.0]], dtype=float)
        R = Ry @ Rx @ Rz
        forward = R @ np.array([0.0, 0.0, -1.0], dtype=float)
        right = R @ np.array([1.0, 0.0, 0.0], dtype=float)
        up = R @ np.array([0.0, 1.0, 0.0], dtype=float)
        forward /= (np.linalg.norm(forward) + 1e-12)
        right /= (np.linalg.norm(right) + 1e-12)
        up /= (np.linalg.norm(up) + 1e-12)
        return forward, right, up

    def update(self, dt, pitch_input, roll_input, yaw_input, throttle_input):
        if self.crashed:
            self.vel += np.array([0.0, -9.81, 0.0]) * dt * 0.2
            self.pos += self.vel * dt
            return
        pitch_rate = pitch_input * 0.8
        roll_rate = roll_input * 1.2
        yaw_rate = yaw_input * 0.6
        self.pitch += pitch_rate * dt
        self.roll += roll_rate * dt
        self.yaw += yaw_rate * dt
        max_pitch = math.pi / 3.5
        max_roll = math.pi / 2.5
        self.pitch = max(-max_pitch, min(max_pitch, self.pitch))
        self.roll = max(-max_roll, min(max_roll, self.roll))
        self.throttle += throttle_input * dt * 0.5
        self.throttle = max(0.0, min(1.0, self.throttle))
        forward, right, up = self.get_body_axes()
        airspeed = np.linalg.norm(self.vel) + 1e-6
        rho = 1.225
        vel_dir = self.vel / (airspeed + 1e-9)
        aoa = math.asin(max(-1.0, min(1.0, np.dot(vel_dir, up))))
        cl = self.cl0 + self.cl_alpha * aoa
        lift = 0.5 * rho * airspeed * airspeed * self.wing_area * cl
        cd = self.cd0 + self.cd_alpha * (aoa * aoa)
        drag = 0.5 * rho * airspeed * airspeed * self.wing_area * cd
        thrust = self.max_thrust * self.throttle
        lift_force = up * lift
        drag_force = -vel_dir * drag
        thrust_force = forward * thrust
        gravity_force = np.array([0.0, -9.81 * self.mass, 0.0], dtype=float)
        total_force = lift_force + drag_force + thrust_force + gravity_force
        accel = total_force / self.mass
        self.vel += accel * dt
        self.pos += self.vel * dt
        bank_turn_effect = self.roll * 0.8
        self.yaw += bank_turn_effect * dt * 0.1
        if self.pos[1] <= 0.0:
            self.pos[1] = 0.0
            self.crashed = True
            self.vel *= 0.2
            self.pitch = 0.0
            self.roll = max(-0.5, min(0.5, self.roll))
            print("CRASHED!")


def draw_aircraft():
    glBegin(GL_TRIANGLES)
    glColor3f(0.6, 0.6, 0.85)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(1.5, 0.5, 2.0)
    glVertex3f(-1.5, 0.5, 2.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(-1.5, -0.5, 2.0)
    glVertex3f(1.5, -0.5, 2.0)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.5, 0.8)
    glVertex3f(-1.5, 0.5, 2.0)
    glVertex3f(1.5, 0.5, 2.0)
    glVertex3f(1.5, -0.5, 2.0)
    glVertex3f(-1.5, -0.5, 2.0)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.75, 0.75, 0.9)
    glVertex3f(-10.0, 0.0, 0.5)
    glVertex3f(-2.0, 0.0, 0.5)
    glVertex3f(2.0, 0.0, 0.5)
    glVertex3f(10.0, 0.0, 0.5)
    glVertex3f(-10.0, 0.0, 0.5)
    glVertex3f(-2.0, 0.0, 0.5)
    glVertex3f(-2.0, 0.0, -1.5)
    glVertex3f(-10.0, 0.0, -1.5)
    glVertex3f(10.0, 0.0, 0.5)
    glVertex3f(2.0, 0.0, 0.5)
    glVertex3f(2.0, 0.0, -1.5)
    glVertex3f(10.0, 0.0, -1.5)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.7, 0.7, 0.85)
    glVertex3f(-1.0, 0.6, -3.0)
    glVertex3f(1.0, 0.6, -3.0)
    glVertex3f(1.0, 0.6, -2.0)
    glVertex3f(-1.0, 0.6, -2.0)
    glVertex3f(-1.0, -0.6, -3.0)
    glVertex3f(1.0, -0.6, -3.0)
    glVertex3f(1.0, -0.6, -2.0)
    glVertex3f(-1.0, -0.6, -2.0)
    glEnd()
    glBegin(GL_QUADS)
    glColor4f(0.2, 0.4, 0.7, 0.8)
    glVertex3f(-0.6, 0.5, -0.5)
    glVertex3f(0.6, 0.5, -0.5)
    glVertex3f(0.6, -0.1, 1.0)
    glVertex3f(-0.6, -0.1, 1.0)
    glEnd()


def draw_ground_grid(size=500, step=10):
    glDisable(GL_LIGHTING)
    glColor3f(0.2, 0.6, 0.2)
    glBegin(GL_LINES)
    for x in range(-size, size + 1, step):
        glVertex3f(x, 0.0, -size)
        glVertex3f(x, 0.0, size)
    for z in range(-size, size + 1, step):
        glVertex3f(-size, 0.0, z)
        glVertex3f(size, 0.0, z)
    glEnd()
    glEnable(GL_LIGHTING)


def init_opengl(width, height):
    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.53, 0.78, 0.92, 1.0)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_POSITION, (0.5, 1.0, 0.2, 0.0))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height or 1), 0.1, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    pygame.init()
    screen_size = (1280, 720)
    pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("flight_sim_3d.py")
    init_opengl(*screen_size)
    clock = pygame.time.Clock()
    craft = Aircraft()
    running = True
    last_time = time.perf_counter()
    while running:
        now = time.perf_counter()
        dt = now - last_time
        last_time = now
        if dt > 0.05:
            dt = 0.05
        pitch_in = roll_in = yaw_in = throttle_in = 0.0
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                w, h = event.size
                pygame.display.set_mode((w, h), DOUBLEBUF | OPENGL | RESIZABLE)
                init_opengl(w, h)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_r:
                    craft.reset()
        keys = pygame.key.get_pressed()
        if keys[K_w]:
            pitch_in += 1.0
        if keys[K_s]:
            pitch_in -= 1.0
        if keys[K_a]:
            roll_in -= 1.0
        if keys[K_d]:
            roll_in += 1.0
        if keys[K_q]:
            yaw_in -= 1.0
        if keys[K_e]:
            yaw_in += 1.0
        if keys[K_UP]:
            throttle_in += 0.6
        if keys[K_DOWN]:
            throttle_in -= 0.6
        craft.update(dt, pitch_in, roll_in, yaw_in, throttle_in)
        forward, right, up = craft.get_body_axes()
        cam_distance = 20.0
        cam_height = 6.0
        cam_pos = craft.pos - forward * cam_distance + np.array([0.0, cam_height, 0.0])
        cam_target = craft.pos + forward * 8.0
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  cam_target[0], cam_target[1], cam_target[2],
                  0.0, 1.0, 0.0)
        glLightfv(GL_LIGHT0, GL_POSITION, (0.5, 1.0, 0.2, 0.0))
        draw_ground_grid(size=500, step=10)
        glPushMatrix()
        glTranslatef(float(craft.pos[0]), float(craft.pos[1]), float(craft.pos[2]))
        glRotatef(math.degrees(craft.yaw), 0.0, 1.0, 0.0)
        glRotatef(math.degrees(craft.pitch), 1.0, 0.0, 0.0)
        glRotatef(math.degrees(craft.roll), 0.0, 0.0, 1.0)
        draw_aircraft()
        glPopMatrix()
        w, h = pygame.display.get_surface().get_size()
        font = pygame.font.get_default_font()
        f = pygame.font.Font(font, 18)
        # large bold font for crash message
        crash_font = pygame.font.SysFont(None, 72, bold=True)

        hud_lines = [
            f"Pos: X={craft.pos[0]:.1f} Y={craft.pos[1]:.1f} Z={craft.pos[2]:.1f}",
            f"Vel: {np.linalg.norm(craft.vel):.1f} m/s",
            f"Pitch: {math.degrees(craft.pitch):.1f}° Roll: {math.degrees(craft.roll):.1f}° Yaw: {math.degrees(craft.yaw):.1f}°",
            f"Throttle: {craft.throttle:.2f}",
            "Controls: W/S pitch, A/D roll, Q/E yaw, Up/Down throttle, R reset, Esc quit",
            "Note: This is a simple prototype (PyOpenGL + pygame + numpy)."
        ]

        # Make HUD taller if crashed so the CRASHED message fits
        hud_height = 140 if craft.crashed else 100
        surf = pygame.Surface((w, hud_height), SRCALPHA, 32)
        surf = surf.convert_alpha()
        surf.fill((0, 0, 0, 0))
        y = 2
        for line in hud_lines:
            txt = f.render(line, True, (255, 255, 255))
            surf.blit(txt, (8, y))
            y += 18

        # If crashed, draw a large bold red "CRASHED!" centered near the top of the HUD.
        if craft.crashed:
            crash_text = "CRASHED!"
            # shadow for readability
            shadow_surf = crash_font.render(crash_text, True, (0, 0, 0))
            crash_surf = crash_font.render(crash_text, True, (220, 40, 40))
            cx = (w - crash_surf.get_width()) // 2
            cy = 8
            surf.blit(shadow_surf, (cx + 2, cy + 2))
            surf.blit(crash_surf, (cx, cy))

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        hud_data = pygame.image.tostring(surf, "RGBA", True)
        glRasterPos2i(0, 0)
        glDrawPixels(surf.get_width(), surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, hud_data)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()