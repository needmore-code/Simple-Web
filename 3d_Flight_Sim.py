import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def clamp(value, minval, maxval):
    return max(minval, min(maxval, value))

def vec_len(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def vec_normalize(v):
    length = vec_len(v)
    if length < 1e-6:
        return (0.0, 0.0, 0.0)
    return (v[0]/length, v[1]/length, v[2]/length)

def vec_add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])

def vec_mul_scalar(v, s):
    return (v[0]*s, v[1]*s, v[2]*s)

def mat_vec_mul(M, v):
    return (
        M[0][0]*v[0] + M[0][1]*v[1] + M[0][2]*v[2],
        M[1][0]*v[0] + M[1][1]*v[1] + M[1][2]*v[2],
        M[2][0]*v[0] + M[2][1]*v[1] + M[2][2]*v[2],
    )

def rotation_matrix(yaw, pitch, roll):
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    return (
        (cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr),
        (sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr),
        (-sp,   cp*sr,            cp*cr),
    )

def terrain_height(x, z):
    return 20.0 + 15.0 * math.sin(x * 0.01) * math.cos(z * 0.01)

class Aircraft:
    def __init__(self):
        self.mass = 1000.0
        self.S = 20.0
        self.gravity = 9.81
        self.rho = 1.225
        self.CL0 = 0.2
        self.CL_alpha = 5.0
        self.CD0 = 0.02
        self.k = 0.05
        self.max_thrust = 30000.0
        self.pitch_rate = 2.0
        self.roll_rate = 2.5
        self.yaw_rate = 1.0
        self.position = (0.0, 60.0, 0.0)
        self.velocity = (25.0, 0.0, 0.0)
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.throttle = 0.3
        self.alive = True

    def reset(self):
        self.position = (0.0, 60.0, 0.0)
        self.velocity = (25.0, 0.0, 0.0)
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.throttle = 0.3
        self.alive = True

    def physics_step(self, dt, controls):
        if not self.alive:
            return
        self.pitch += (-controls['pitch']) * self.pitch_rate * dt
        self.roll += (controls['roll']) * self.roll_rate * dt
        self.yaw += (controls['yaw']) * self.yaw_rate * dt
        self.pitch = clamp(self.pitch, -math.pi/2 + 0.1, math.pi/2 - 0.1)
        if controls['th_up']:
            self.throttle = clamp(self.throttle + 0.8 * dt, 0.0, 1.0)
        if controls['th_down']:
            self.throttle = clamp(self.throttle - 0.8 * dt, 0.0, 1.0)
        R = rotation_matrix(self.yaw, self.pitch, self.roll)
        forward = mat_vec_mul(R, (1.0, 0.0, 0.0))
        up = mat_vec_mul(R, (0.0, 1.0, 0.0))
        speed = vec_len(self.velocity)
        V_world = self.velocity
        V_body = (
            R[0][0]*V_world[0] + R[1][0]*V_world[1] + R[2][0]*V_world[2],
            R[0][1]*V_world[0] + R[1][1]*V_world[1] + R[2][1]*V_world[2],
            R[0][2]*V_world[0] + R[1][2]*V_world[1] + R[2][2]*V_world[2],
        )
        aoa = math.atan2(V_body[1], max(1e-6, V_body[0]))
        CL = self.CL0 + self.CL_alpha * aoa
        CD = self.CD0 + self.k * (CL**2)
        q = 0.5 * self.rho * speed * speed
        lift_mag = q * self.S * CL
        drag_mag = q * self.S * CD
        lift = vec_mul_scalar(up, lift_mag)
        vel_norm = vec_normalize(self.velocity) if speed > 0.01 else (0.0, 0.0, 0.0)
        drag = vec_mul_scalar(vel_norm, -drag_mag)
        thrust = vec_mul_scalar(forward, self.throttle * self.max_thrust)
        gravity_force = (0.0, -self.mass * self.gravity, 0.0)
        total_force = vec_add(vec_add(vec_add(thrust, lift), drag), gravity_force)
        accel = vec_mul_scalar(total_force, 1.0 / self.mass)
        self.velocity = vec_add(self.velocity, vec_mul_scalar(accel, dt))
        self.position = vec_add(self.position, vec_mul_scalar(self.velocity, dt))
        ground_y = terrain_height(self.position[0], self.position[2])
        altitude = self.position[1] - ground_y
        if altitude <= 1.0 and vec_len(self.velocity) > 12.0:
            self.alive = False
        elif altitude <= 0.05:
            self.velocity = (0.0, 0.0, 0.0)
            self.position = (self.position[0], ground_y + 0.05, self.position[2])

class FlightSimulator:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.aircraft = Aircraft()
        self.paused = False
        self.debug_info = True
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Flight Simulator")
        self.setup_gl()
        self.clock = pygame.time.Clock()

    def setup_gl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLight(GL_LIGHT0, GL_POSITION, (100, 200, 100, 0))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1))
        glLight(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        glLight(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
        glMatrixMode(GL_PROJECTION)
        gluPerspective(60, (self.width / self.height), 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW)

    def draw_aircraft(self):
        glPushMatrix()
        R = rotation_matrix(self.aircraft.yaw, self.aircraft.pitch, self.aircraft.roll)
        gl_matrix = [
            R[0][0], R[1][0], R[2][0], 0,
            R[0][1], R[1][1], R[2][1], 0,
            R[0][2], R[1][2], R[2][2], 0,
            0, 0, 0, 1
        ]
        glMultMatrixf(gl_matrix)
        glColor3f(0.2, 0.2, 0.2)
        self.draw_cylinder(0.5, 3.0, 20)
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(0, 0.3, 0)
        self.draw_box(8.0, 0.2, 1.0)
        glPopMatrix()
        glColor3f(0.4, 0.4, 0.4)
        glPushMatrix()
        glTranslatef(0, 0.2, -2.5)
        self.draw_box(3.0, 0.1, 0.8)
        glPopMatrix()
        glPopMatrix()

    def draw_cylinder(self, radius, height, slices):
        quad = GLUquadric()
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        gluCylinder(quad, radius, radius, height, slices, 10)
        glPopMatrix()

    def draw_box(self, width, height, depth):
        glBegin(GL_TRIANGLES)
        w, h, d = width/2, height/2, depth/2
        vertices = [
            (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),
            (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d)
        ]
        faces = [
            (0,1,2), (0,2,3),
            (4,6,5), (4,7,6),
            (0,4,5), (0,5,1),
            (2,6,7), (2,7,3),
            (0,3,7), (0,7,4),
            (1,5,6), (1,6,2),
        ]
        for face in faces:
            for vertex_idx in face:
                glVertex3fv(vertices[vertex_idx])
        glEnd()

    def draw_terrain(self):
        glColor3f(0.2, 0.6, 0.2)
        grid_size = 200
        grid_step = 5
        glBegin(GL_TRIANGLES)
        for x in range(-grid_size, grid_size, grid_step):
            for z in range(-grid_size, grid_size, grid_step):
                y00 = terrain_height(x, z)
                y10 = terrain_height(x + grid_step, z)
                y01 = terrain_height(x, z + grid_step)
                y11 = terrain_height(x + grid_step, z + grid_step)
                glVertex3f(x, y00, z)
                glVertex3f(x + grid_step, y10, z)
                glVertex3f(x, y01, z + grid_step)
                glVertex3f(x + grid_step, y10, z)
                glVertex3f(x + grid_step, y11, z + grid_step)
                glVertex3f(x, y01, z + grid_step)
        glEnd()

    def draw_sky(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.5, 0.7, 1.0)
        pos = self.aircraft.position
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        quad = GLUquadric()
        gluSphere(quad, 300, 30, 30)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def render_text(self, text, x, y, size=72, color=(255,0,0), bold=True):
        font = pygame.font.SysFont(None, size, bold)
        text_surface = font.render(text, True, color)
        w, h = text_surface.get_size()
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1,1,1)
        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex2f(x, y)
        glTexCoord2f(1,0); glVertex2f(x + w, y)
        glTexCoord2f(1,1); glVertex2f(x + w, y + h)
        glTexCoord2f(0,1); glVertex2f(x, y + h)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        try:
            glDeleteTextures([tex_id])
        except Exception:
            pass

    def draw_hud(self):
        if not self.aircraft.alive:
            text = "CRASHED!"
            font = pygame.font.SysFont(None, 72, True)
            w, h = font.size(text)
            x = (self.width - w) // 2
            y = (self.height - h) // 2
            self.render_text(text, x, y, size=72, color=(255, 0, 0), bold=True)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        controls = {
            'pitch': -1 if keys[K_w] else (1 if keys[K_s] else 0),
            'roll': 1 if keys[K_d] else (-1 if keys[K_a] else 0),
            'yaw': 1 if keys[K_q] else (-1 if keys[K_e] else 0),
            'th_up': keys[K_UP],
            'th_down': keys[K_DOWN],
        }
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                if event.key == K_r:
                    self.aircraft.reset()
                if event.key == K_SPACE:
                    self.paused = not self.paused
                if event.key == K_i:
                    self.debug_info = not self.debug_info
        return True, controls

    def update(self, dt, controls):
        if not self.paused:
            self.aircraft.physics_step(dt, controls)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        pos = self.aircraft.position
        glTranslatef(0, 0, -30)
        R = rotation_matrix(self.aircraft.yaw, self.aircraft.pitch, self.aircraft.roll)
        gl_matrix = [
            R[0][0], R[1][0], R[2][0], 0,
            R[0][1], R[1][1], R[2][1], 0,
            R[0][2], R[1][2], R[2][2], 0,
            0, 0, 0, 1
        ]
        glMultMatrixf(gl_matrix)
        glTranslatef(-pos[0], -pos[1], -pos[2])
        self.draw_sky()
        self.draw_terrain()
        self.draw_aircraft()
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            result = self.handle_input()
            if result is False:
                running = False
                break
            running, controls = result
            dt = self.clock.tick(60) / 1000.0
            self.update(dt, controls)
            self.render()
        pygame.quit()

if __name__ == "__main__":
    sim = FlightSimulator()
    sim.run()
