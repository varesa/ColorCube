import pygame
from pygame.locals import *

import numpy

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
from OpenGL.GLU import *

class ColorCube:

    screen_size = (800, 600)

    def init(self):
        #Init pygame
        pygame.init()
        self.display = pygame.display.set_mode(self.screen_size, OPENGL | HWSURFACE | DOUBLEBUF)

        #Init OpenGL

        vertex_shader = shaders.compileShader("""
        #version 130

        varying vec4 color;

        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            color = gl_Color;
        }

        """, GL_VERTEX_SHADER)

        fragment_shader = shaders.compileShader("""
        #version 130

        varying vec4 color;

        void main() {
            gl_FragColor = color;
            //gl_FragColor = vec4(1,0,1,1);
        }

        """, GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vertex_shader, fragment_shader)

        self.vbo = vbo.VBO(
            numpy.array([

                #Top face
                [-1,  1, -1,  0, 1, 0],
                [-1,  1,  1,  0, 1, 1],
                [ 1,  1,  1,  1, 1, 1],

                [-1,  1, -1,  0, 1, 0],
                [ 1,  1, -1,  1, 1, 0],
                [ 1,  1,  1,  1, 1, 1],

                #Bottom face
                [-1, -1, -1,  0, 0, 0],
                [-1, -1,  1,  0, 0, 1],
                [ 1, -1,  1,  1, 0, 1],

                [-1, -1, -1,  0, 0, 0],
                [ 1, -1, -1,  1, 0, 0],
                [ 1, -1,  1,  1, 0, 1],

                #Front face
                [-1, -1,  1,  0, 0, 1],
                [-1,  1,  1,  0, 1, 1],
                [ 1,  1,  1,  1, 1, 1],

                [-1, -1,  1,  0, 0, 1],
                [ 1, -1,  1,  1, 0, 1],
                [ 1,  1,  1,  1, 1, 1],

                #Left face
                [-1, -1, -1,  0, 0, 0],
                [-1, -1,  1,  0, 0, 1],
                [-1,  1,  1,  0, 1, 1],

                [-1, -1, -1,  0, 0, 0],
                [-1,  1, -1,  0, 1, 0],
                [-1,  1,  1,  0, 1, 1],

                #Back face
                [-1, -1, -1,  0, 0, 0],
                [-1,  1, -1,  0, 1, 0],
                [ 1,  1, -1,  1, 1, 0],

                [-1, -1, -1,  0, 0, 0],
                [ 1, -1, -1,  1, 0, 0],
                [ 1,  1, -1,  1, 1, 0],

                #Right face
                [ 1, -1, -1,  1, 0, 0],
                [ 1, -1,  1,  1, 0, 1],
                [ 1,  1,  1,  1, 1, 1],

                [ 1, -1, -1,  1, 0, 0],
                [ 1,  1, -1,  1, 1, 0],
                [ 1,  1,  1,  1, 1, 1],

            ], 'f')
        )

        glClearColor(1, 1, 1, 0)
        glEnable (GL_DEPTH_TEST);

    stop = False

    def main(self):
        self.init()

        mouse = False
        lastx = None
        lasty = None

        x_rot = 0
        y_rot = 0

        while not self.stop:
            #Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = True

                if event.type == MOUSEBUTTONDOWN:
                    mouse = True
                    lastx = pygame.mouse.get_pos()[0]
                    lasty = pygame.mouse.get_pos()[1]
                if event.type == MOUSEBUTTONUP:
                    mouse = False
                if event.type == MOUSEMOTION:
                    if mouse:
                        xdiff = event.pos[0] - lastx
                        ydiff = event.pos[1] - lasty

                        y_rot += ydiff

                        if y_rot < 90 or y_rot > 270:
                            x_rot += xdiff
                        else:
                            x_rot -= xdiff

                        if x_rot > 360:
                            x_rot -= 360
                        if x_rot < 0:
                            x_rot += 360

                        if y_rot > 360:
                            y_rot -= 360
                        if y_rot < 0:
                            y_rot += 360

                        lastx = event.pos[0]
                        lasty = event.pos[1]

            #Render
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(60, (1.0*self.screen_size[0])/(1.0*self.screen_size[1]), 0.1, 100)
            gluLookAt(0, 0, 5,  0, 0, 0,  0, 1, 0)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            glRotatef(x_rot, 0, 1, 0)

            if x_rot < 90:
                glRotatef(y_rot, 1-x_rot/90.0, 0, x_rot/90.0)
            elif x_rot < 180:
                t = x_rot - 90
                glRotatef(y_rot, -t/90.0, 0, 1-t/90.0)
            elif x_rot < 270:
                t = x_rot - 180
                glRotatef(y_rot, -1+t/90.0, 0, -t/90.0)
            else:
                t = x_rot - 270
                glRotatef(y_rot, t/90.0, 0, -1+t/90.0)

            glUseProgram(self.shader)

            try:
                self.vbo.bind()
                try:
                    glEnableClientState(GL_VERTEX_ARRAY)
                    glEnableClientState(GL_COLOR_ARRAY)

                    glVertexPointer(3, GL_FLOAT, 24, self.vbo)
                    glColorPointer(3, GL_FLOAT, 24, self.vbo+12)

                    glDrawArrays(GL_TRIANGLES, 0, 36)
                finally:
                    glDisableClientState(GL_VERTEX_ARRAY)
                    glDisableClientState(GL_COLOR_ARRAY)

                    self.vbo.unbind()
            finally:
                glUseProgram(0)

            pygame.display.flip()


if __name__ == "__main__":
    ColorCube().main()