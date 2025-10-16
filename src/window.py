### extiende de la clase Window de Pyglet. Se encarga de gestionar la creación de la ventana y sus eventos. Crea el contexto de ModernGL para trabajar con OpenGL. Implementa el método on_draw que limpia y renderiza la escena en cada frame. También implementa on_resize para escalar el contexto al escalar la ventana (y que no se vea lento) y run para ejecutar el loop principal de Pyglet.

import moderngl
import pyglet

class Window(pyglet.window.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.ctx = moderngl.create_context()
        self.scene = None

    def set_scene(self, scene):
        self.scene = scene
        scene.start()
    
    def on_draw(self): # se ejecuta por cada frame
        self.clear()
        self.ctx.enable(moderngl.DEPTH_TEST)
        if self.scene:
            self.scene.update(0)
            self.scene.render()
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.scene is None:
            return
        
        # Convertir posición del mouse a u,v [0,1]
        u = x / self.width
        v = y / self.height

        self.scene.on_mouse_click(u, v)

    def on_resize(self, width, height):
        if self.scene:
            self.scene.on_resize(width, height)
    
    def run(self): # activar el loop de la ventana
        pyglet.app.run()