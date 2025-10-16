from model import Model
from hit import HitBox
import numpy as np
import glm


class Quad(Model):
    def __init__(self, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1), name="quad", animated = True, hittable = True):
        self.name = name
        self.animated = animated
        self.position = glm.vec3(*position)
        self.rotation = glm.vec3(*rotation)
        self.scale = glm.vec3(*scale)
        self.__colision = HitBox(get_model_matrix = lambda: self.get_model_matrix(), hittable = hittable)
   
        vertices = np.array([
            -1, -1, 0,
            1, -1, 0,
            1,  1, 0,
            -1,  1, 0,
        ], dtype="f4")


        colors = np.array([
            0,1,1,
            0,0,1,
            1,0,1,
            1,1,0
        ], dtype='f4')


        texcoords = np.array([
            0, 0,
            1, 0,
            1, 1,
            0, 1,
        ], dtype="f4")


        normals = np.array([
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
            0, 0, 1,
        ], dtype="f4")


        indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype="i4")

        self.__vertices = vertices

        super().__init__(vertices, indices, colors= colors, textcoords=texcoords, normals=normals)

    @property
    def aabb(self):
        verts3 = self.__vertices.reshape(-1, 3)
    
        pts = [self.get_model_matrix() * glm.vec4(v[0], v[1], v[2], 1.0) for v in verts3]
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        zs = [p.z for p in pts]
        return (glm.vec3(min(xs), min(ys), min(zs)),
                    glm.vec3(max(xs), max(ys), max(zs)))


    def check_hit(self, origin, direction):
        return self.__colision.check_hit(origin, direction)
   
    def get_model_matrix(self):
        model = glm.mat4(1)
        model = glm.translate(model, self.position)
        model = glm.rotate(model, glm.radians(self.rotation.x % 360), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(self.rotation.y % 360), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(self.rotation.z % 360), glm.vec3(0, 0, 1))
        model = glm.scale(model, self.scale)
        return model