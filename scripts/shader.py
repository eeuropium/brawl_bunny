import moderngl
from time import time
from array import array

class Shader():
    def __init__(self):
        self.context = moderngl.create_context()

        self.quad_buffer = self.context.buffer(data = array('f', [
            # position (x, y), uv coords (x, y)
            -1.0, 1.0, 0.0, 0.0,  # topleft
            1.0, 1.0, 1.0, 0.0,   # topright
            -1.0, -1.0, 0.0, 1.0, # bottomleft
            1.0, -1.0, 1.0, 1.0,  # bottomright
        ]))

        # load vertex and fragment shader from their glsl files
        with open("scripts/vertex_shader.glsl", "r") as file:
            vert_shader = file.read()

        with open("scripts/fragment_shader.glsl", "r") as file:
            frag_shader = file.read()

        # pass in shader programs
        self.program = self.context.program(vertex_shader = vert_shader, fragment_shader = frag_shader)

        self.render_object = self.context.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vertex', 'texture_coordinate')])
        # the arguments represent - 2 floats representing vertex, 2 floats representing texture coordinate

        # set start time to allow time calculations in shader
        self.start_time = time()

    def surf_to_texture(self, surf):
        texture = self.context.texture(surf.get_size(), 4) # surface dimensions and number of colour channels (RGBA)

        # transition / interpolation between textures (pixel art uses NEAREST)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST) # (minification filter, magnification filter)

        # pygame colour channel mapped to openGL colour channel
        texture.swizzle = 'BGRA'

        # surf.get_view() - return a buffer view of the Surface's pixels, '1' specifies the type of return data
        texture.write(surf.get_view('1'))

        return texture

    def apply_shader(self, surf):
        self.frame_texture = self.surf_to_texture(surf)

        # have to be same at 0
        self.frame_texture.use(0)
        self.program["frame_texture"] = 0
        self.program["time"] = time() - self.start_time
        self.program["use_shadow_realm_shader"] = False

        self.render_object.render(mode = moderngl.TRIANGLE_STRIP)

    def release_memory(self):
        self.frame_texture.release()
