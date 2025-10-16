import numpy as np
import glm
import math

class Sphere:
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), 
                 radius=1.0, latitude_segments=16, longitude_segments=32, name="sphere"):
        self.name = name
        self.position = glm.vec3(*position)
        self.rotation = glm.vec3(*rotation)
        self.scale = glm.vec3(*scale)
        self.radius = radius
        self.rotation_speed = glm.vec3(20, 40, 15)
        self.vertices, self.indices = self.generate_sphere(latitude_segments, longitude_segments)

    def generate_sphere(self, lat_segments, lon_segments):
        vertices = []
        indices = []
        
        # Vertices
        for i in range(lat_segments + 1):  #Pi
            lat = math.pi * i / lat_segments
            sin_lat = math.sin(lat)
            cos_lat = math.cos(lat)
            
            for j in range(lon_segments + 1):  #2Pi
                lon = 2 * math.pi * j / lon_segments
                sin_lon = math.sin(lon)
                cos_lon = math.cos(lon)
                
                # Posiciones
                x = self.radius * sin_lat * cos_lon
                y = self.radius * cos_lat
                z = self.radius * sin_lat * sin_lon
                
                # Colores
                r = (x / self.radius + 1) * 0.5
                g = (y / self.radius + 1) * 0.5
                b = (z / self.radius + 1) * 0.5
                
                vertices.extend([x, y, z, r, g, b])
        
        # Indices
        for i in range(lat_segments):
            for j in range(lon_segments):
                first = i * (lon_segments + 1) + j
                second = first + lon_segments + 1
                
                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
        
        return np.array(vertices, dtype='f4'), np.array(indices, dtype='i4')

    def get_model_matrix(self):
        model = glm.mat4(1)
        model = glm.translate(model, self.position)
        model = glm.rotate(model, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        model = glm.scale(model, self.scale)
        return model
    
    def update(self):
        self.rotation.x += 1.5