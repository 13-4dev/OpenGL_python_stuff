import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
from PIL import Image


def load_shader(file_path):
    with open(file_path, 'r') as file:
        shader_code = file.read()
    return shader_code


def load_texture(texture_path):
    image = Image.open(texture_path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # OpenGL requires the texture to be flipped vertically
    img_data = np.array(image, dtype=np.uint8)
    return img_data, image.width, image.height


# Initialize GLFW
if not glfw.init():
    raise Exception("Failed to initialize GLFW")

# Configure GLFW window
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

# Create window
window = glfw.create_window(800, 600, "Rotating Windows Logo", None, None)
if not window:
    glfw.terminate()
    raise Exception("Failed to create a window")

glfw.make_context_current(window)

# Load shaders
vertex_shader = load_shader("shaders/vertex_shader.glsl")
fragment_shader = load_shader("shaders/fragment_shader.glsl")

shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                        compileShader(fragment_shader, GL_FRAGMENT_SHADER))

# Data for the quad (flat rectangle)
vertices = np.array([
    # Positions        # Texture coordinates
    -0.5, -0.5, 0.0,   0.0, 0.0,  # Bottom-left
     0.5, -0.5, 0.0,   1.0, 0.0,  # Bottom-right
     0.5,  0.5, 0.0,   1.0, 1.0,  # Top-right
    -0.5,  0.5, 0.0,   0.0, 1.0   # Top-left
], dtype=np.float32)

indices = np.array([
    0, 1, 2,  # First triangle
    2, 3, 0   # Second triangle
], dtype=np.uint32)

# Create VAO and VBO
vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)
ebo = glGenBuffers(1)

glBindVertexArray(vao)

glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

# Set vertex attributes
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))  # Position
glEnableVertexAttribArray(0)

glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))  # Texture coordinates
glEnableVertexAttribArray(1)

# Load texture
texture_data, tex_width, tex_height = load_texture("textures/windows_logo.png")

# Create and bind texture
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
glGenerateMipmap(GL_TEXTURE_2D)

# Camera and projection matrices setup
model = glm.mat4(1.0)
view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)

glEnable(GL_DEPTH_TEST)

# Main loop
while not glfw.window_should_close(window):
    glfw.poll_events()
    
    # Clear buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Use shader
    glUseProgram(shader)
    
    # Rotate model (slowed down)
    model = glm.rotate(model, glm.radians(0.2), glm.vec3(0.0, 1.0, 0.0))
    
    model_loc = glGetUniformLocation(shader, "model")
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
    
    view_loc = glGetUniformLocation(shader, "view")
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
    
    proj_loc = glGetUniformLocation(shader, "projection")
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))
    
    # Bind texture and draw quad
    glBindTexture(GL_TEXTURE_2D, texture)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    
    # Update window
    glfw.swap_buffers(window)

# Clean up resources
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo, ebo])
glDeleteProgram(shader)
glDeleteTextures(1, [texture])

glfw.terminate()
