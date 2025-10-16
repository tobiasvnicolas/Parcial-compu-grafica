import numpy as np
import glm

class Graphics:
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material

        self.__vbo = self.create_buffers()
        self.__ibo = ctx.buffer(model.indices.tobytes())
        self.__vao = ctx.vertex_array(material.shader_program.prog, [*self.__vbo], self.__ibo)

        self.textures = self.load_textures(material.textures_data)

    def create_buffers(self):
        buffers = []
        shader_attributes = self.__material.shader_program.attributes

        for attribute in self.__model.vertex_layout.get_attributes():
            if attribute.name in shader_attributes:
                vbo = self.__ctx.buffer(attribute.array.tobytes())
                buffers.append((vbo, attribute.format, attribute.name))
        return buffers

    def load_textures(self, textures_data):
        textures = {} # diccionario en vez de lista pq quiero acceder por nombre
        for texture in textures_data:
            if texture.image_data is not None: # puse is not None pq si no le paso nada me crea una textura negra
                texture_ctx = self.__ctx.texture(texture.size, texture.channels_amount, texture.image_data.tobytes()) # corregi aca pq antes le pasaba el objeto ImageData y no los bytes
                if texture.build_mipmaps:
                    texture_ctx.build_mipmaps()
                texture_ctx.repeat_x = texture.repeat_x
                texture_ctx.repeat_y = texture.repeat_y
                textures[texture.name] = (texture, texture_ctx)
        return textures

    def bind_to_image(self, name = "u_texture", unit = 0, read = False, write = True):
        self.textures[name][1].bind_to_image(unit, read, write)

    def render(self, uniforms):
        for name, value in uniforms.items():
            if name in self.__material.shader_program.prog:
                self.__material.set_uniform(name, value)
        
        for i, (name, (tex, texture_ctx)) in enumerate(self.textures.items()):
            texture_ctx.use(i)
            self.__material.shader_program.set_uniform(name, i)

        self.__vao.render()

    def update_texture(self, texture_name, new_data):
        if texture_name not in self.textures: #El error q me tiraba era pq __textures es un atributo privado, como uso un diccionario, no me va a aceptar atrivutos privados
            raise ValueError(f"No existe la textura {texture_name}")
        
        texture_obj, texture_ctx = self.textures[texture_name] # devuelta, hago la referencia sin __
        texture_obj.update_data(new_data)
        texture_ctx.write(texture_obj.get_bytes())

    def set_shader(self, shader_program):
        self.shader_program = shader_program.prog
    
    def set_uniform(self, name, value):
        self.shader_program.set_uniform(name, value)

class ComputeGraphics(Graphics):
    def __init__(self, ctx, model, material):
        self._ctx = ctx
        self._model = model
        self._material = material
        self.textures = material.textures_data
        super().__init__(ctx, model, material)

    def create_primitive(self, primitives):
        amin, amax = self._model.aabb
        primitives.append({"aabb_min": amin, "aabb_max": amax})

    def create_transformation_matrix(self, transformations_matrix, index):
        m = self._model.get_model_matrix()
        transformations_matrix[index, :] = np.array(m.to_list(), dtype="f4").reshape(16)

    def create_inverse_transformation_matrix(self, inverse_transformations_matrix, index):
        m = self._model.get_model_matrix()
        inverse = glm.inverse(m)
        inverse_transformations_matrix[index, :] = np.array(inverse.to_list(), dtype="f4").reshape(16)

    def create_material_matrix(self, materials_matrix, index):
        reflectivity = self._material.reflectivity
        color = self._material.colorRGB
        
        if hasattr(color, 'tolist'):
            color = color.tolist() if hasattr(color, 'tolist') else list(color)
        
        if len(color) >= 3:
            r, g, b = float(color[0]), float(color[1]), float(color[2])
        else:
            r = g = b = 0.0

        r = r / 255.0 if r > 1.0 else r
        g = g / 255.0 if g > 1.0 else g
        b = b / 255.0 if b > 1.0 else b

        materials_matrix[index, :] = np.array([r, g, b, reflectivity], dtype="f4")