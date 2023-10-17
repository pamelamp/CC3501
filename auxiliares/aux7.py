import pyglet
from OpenGL import GL
import numpy as np
import sys

# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio
# v
if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../../')
# ^
# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = { "total_time": 0.0, "camera": None }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 7", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([2.5, 2.5, 2.5], "perspective")
    controller.program_state["camera"].yaw = -3* np.pi/ 4
    controller.program_state["camera"].pitch = -np.pi / 4

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh.vert"),
        get_path("auxiliares/shaders/textured_mesh.frag"))
    
    textured_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh_lit.vert"),
        get_path("auxiliares/shaders/textured_mesh_lit.frag"))

    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    arrow = mesh_from_file("assets/arrow.off")[0]["mesh"]

    graph = SceneGraph(controller)

    graph.add_node("sun",
                   pipeline=textured_mesh_lit_pipeline,
                   position=[0, 2, 0],  # Irrelevante, solo se define para posicionar la flecha
                   rotation=[-3*np.pi/4, 0, 0],
                   light=DirectionalLight(diffuse = [0, 0, 0], specular = [0, 0, 0], ambient = [0, 0, 0]))

    graph.add_node("light",
                   pipeline=textured_mesh_lit_pipeline,
                   position=[1, 1, 1],
                   light=PointLight(
                       diffuse = [1, 0, 0], # rojo
                       specular = [0, 0, 1], # azul
                       ambient = [0, 0.15, 0], # verde
                       #constant = 1.0,
                       #linear = 0.7,
                       #quadratic = 1.8
                       )
                    )

    graph.add_node("spotlight",
                   pipeline=textured_mesh_lit_pipeline,
                   position=[-2, 1, -2],
                   rotation=[-3*np.pi/4, np.pi/4, 0],
                   light=SpotLight(
                          diffuse = [1, 0, 0],
                          specular = [0, 0, 1],
                          ambient = [0.15, 0.15, 0.15],
                          cutOff = 0.91, # siempre mayor a outerCutOff
                          outerCutOff = 0.82
                   )
                )

    graph.add_node("arrow",
                   attach_to="spotlight",
                   mesh=arrow,
                   position=[0, 0, -0.5],
                   rotation=[-np.pi, 0, 0],
                   scale=[0.5, 0.5, 0.5],
                   color=[1, 1, 0],
                   pipeline=color_mesh_pipeline)
    

    # diffuse: Color difuso del material
    # specular: Color especular del material
    # ambient: Color ambiental del material
    # shininess: Exponente especular del material
    material = Material(
        diffuse = [1, 1, 1],
        specular = [1, 1, 1],
        ambient = [1, 1, 1],
        shininess = 32)

    textura = Texture("assets/wall1.jpg")

    graph.add_node("object",
                   mesh = cube,
                   pipeline = textured_mesh_lit_pipeline,
                   rotation = [-np.pi/2, 0, 0],
                   texture=textura,
                   scale = [5, 5, 1],
                   material = material)


    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]
        if controller.is_key_pressed(pyglet.window.key.A):
            camera.position -= camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.D):
            camera.position += camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.W):
            camera.position += camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.S):
            camera.position -= camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.Q):
            camera.position[1] -= dt
        if controller.is_key_pressed(pyglet.window.key.E):
            camera.position[1] += dt
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"
        camera.update()

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.RIGHT:
            controller.program_state["camera"].yaw += dx * 0.01
            controller.program_state["camera"].pitch += dy * 0.01


    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
