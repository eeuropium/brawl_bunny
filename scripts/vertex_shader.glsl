#version 330 core

in vec2 vertex;
in vec2 texture_coordinate;
out vec2 uvs;

void main() {
    // set UV to texture coordinates - pygame coordinate system to glsl coordinate system
    uvs = texture_coordinate;
    gl_Position = vec4(vertex, 0.0, 1.0); // homogenous coordinate
}
