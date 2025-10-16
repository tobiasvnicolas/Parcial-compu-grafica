### posiciona una cámara, administra los objetos y sus Graphics (VBO, VAO, ShaderProgram). Realiza transformaciones a los objetos que están en la escena y actualiza sus shaders. También actualiza viewport en on_resize.

import math
from graphics import Graphics
import glm
from raytracer import RayTracer
from raytracer import RayTracerGPU
from graphics import ComputeGraphics
import numpy as np

class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.objects = []
        self.graphics = {}
        self.camera = camera
        self.model = glm.mat4(1)
        self.view = camera.get_view_matrix()
        self.projection = camera.get_perspective_matrix()
        self.time = 0

    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = Graphics(self.ctx, model, material)

    def start(self):
        print("Start!")

    def render(self):
        self.time += 0.01 # En el constructor (__init_) definir self.time = 0
            # Rotar los objetos fuera del shader y actualizar sus matrices
        for obj in self.objects:
            if(obj.animated):
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01
                #pass # me molesta q se mueva el fondo

        # for obj in self.objects:
        #     obj.rotation.x += 0.8
        #     obj.rotation.y += 0.6
        #     obj.rotation.z += 0.4

        #     obj.position.x += math.sin(self.time) * 0.01

            model = obj.get_model_matrix()
            mvp = self.projection * self.view * model
            # self.graphics[obj.name].set_uniform({'Mvp' : mvp}) ### Como aca no acepta un diccionario, en vez de cambiar la funcion set_uniform en graphics.py, hago esto:
            uniforms = {'Mvp': mvp}
            self.graphics[obj.name].render(uniforms) ### Y aca uso la funcion render que ya tiene todo


    # def render(self):
    #     self.view = self.camera.get_view_matrix()
    #     self.projection = self.camera.get_perspective_matrix()
        
    #     for obj in self.objects:
    #         model_matrix = obj.get_model_matrix()
    #         mvp_matrix = self.projection * self.view * model_matrix
    #         graphics = self.graphics[obj.name]
    #         graphics.shader_program.set_uniform('Mvp', mvp_matrix)
    #         graphics.vao.render()
    
    def on_mouse_click(self, u, v):
        ray = self.camera.raycast(u, v)

        for obj in self.objects:
            if obj.check_hit(ray.origin, ray.direction):
                print(f"Golpeaste un {obj.name}")
                2

    def update(self, dt):
        for obj in self.objects:
            if hasattr(obj, 'update'):
                obj.update()

    def on_resize(self, width, height):
        self.ctx.viewport = (0, 0, width, height)
        self.camera.projection = glm.perspective(glm.radians(45), width / height, 0.1, 100)


class RayScene(Scene):
    def __init__(self, ctx, camera, width, height):
        super().__init__(ctx, camera)
        self.raytracer = RayTracer(camera, width, height)
    
    def start(self):
        # self.raytracer.render_frame(self.objects) ### Solo quiero pasar los objetos que tienen check_hit
        hittable_objects = [obj for obj in self.objects if hasattr(obj, 'check_hit')] ### Este es mi filtro
        self.raytracer.render_frame(hittable_objects) ### El tema es q si le paso un objeto q no tiene check_hit, revienta
        if "Sprite" in self.graphics:
            self.graphics["Sprite"].update_texture("u_texture", self.raytracer.get_texture())
        
    def render(self):
        super().render()
    
    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.raytracer = RayTracer(self.camera, width, height)
        self.start()

class RaySceneGPU(Scene):
    def __init__(self, ctx, camera, width, height, output_model, output_material):
        self.ctx = ctx
        self.camera = camera
        self.width = width
        self.height = height
        self.raytracer = None

        self.output_graphics = Graphics(ctx, output_model, output_material)
        self.raytracer = RayTracerGPU(self.ctx, self.camera, self.width, self.height, self.output_graphics)

        super().__init__(self.ctx, self.camera)

    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = ComputeGraphics(self.ctx, model, material)

    def start(self):
        print("Start Raytracing!")
        self.primitives = []
        n = len(self.objects)
        self.models_f = np.zeros((n, 16), dtype='f4')
        self.inv_f = np.zeros((n, 16), dtype='f4')
        self.mats_f = np.zeros((n, 4), dtype='f4')

        self._update_matrix()

        self._matrix_to_ssbo()

    def _matrix_to_ssbo(self):
        self.raytracer.matrix_to_ssbo(self.models_f, 0)
        self.raytracer.matrix_to_ssbo(self.inv_f, 1)
        self.raytracer.matrix_to_ssbo(self.mats_f, 2)
        self.raytracer.primitives_to_ssbo(self.primitives, 3)

    def render(self):
        self.time += 0.01
        for obj in self.objects:
            if obj.animated:
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01
            
        if(self.raytracer is not None):
            self._update_matrix()
            self._matrix_to_ssbo()
            self.raytracer.run()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.width, self.height = width, height
        self.camera.aspect = width/height
    
    def _update_matrix(self):
        self.primitives = []

        for i, (name, graphics) in enumerate(self.graphics.items()):
            graphics.create_primitive(self.primitives)
            graphics.create_transformation_matrix(self.models_f, i)
            graphics.create_inverse_transformation_matrix(self.inv_f, i)
            graphics.create_material_matrix(self.mats_f, i)

    def _matrix_to_ssbo(self):
        self.raytracer.matrix_to_ssbo(self.models_f, 0)
        self.raytracer.matrix_to_ssbo(self.inv_f, 1)
        self.raytracer.matrix_to_ssbo(self.mats_f, 2)
        self.raytracer.primitives_to_ssbo(self.primitives, 3)