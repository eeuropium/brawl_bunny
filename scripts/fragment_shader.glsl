#version 330 core

uniform sampler2D frame_texture;
uniform float time;
uniform bool use_shadow_realm_shader;

in vec2 uvs; // x, y coordinate of current pixel - coordinates range from 0 to 1 (same as pygame - top left corner is (0, 0))
out vec4 output_colour;

vec4 shadow_realm_shader(vec4 pixel_colour) {
    const float BOX_X = 0.3, BOX_Y = 0.2;

    // overlay sin waves to make it seem more natural
    float y_offset = 0;
    y_offset += 0.03 * sin(20 * uvs.x + 3 * time);
    y_offset += 0.06 * sin(10 * uvs.x + 2 * time);
    y_offset += 0.01 * sin(30 * uvs.x + 0.5 * time);

    // calculate top and bottom coordinate
    float top = BOX_Y + y_offset, bottom = 1 - BOX_Y + y_offset;

    // overlay sin waves to make it seem more natural
    float x_offset = 0;
    x_offset += 0.03 * sin(20 * uvs.y + 3 * time);
    x_offset += 0.06 * sin(10 * uvs.y + 2 * time);
    x_offset += 0.01 * sin(30 * uvs.y + 0.5 * time);

    // calculate left and right coordinate
    float left = BOX_X + x_offset, right = 1 - BOX_X + x_offset;

    // calculate grey_scale value by averaging r, g, b values
    float gray_value = (pixel_colour.r + pixel_colour.g + pixel_colour.b) / 3;

    // check if current pixel is within our bounding box
    if (left <= uvs.x && uvs.x <= right &&
        top <= uvs.y && uvs.y <= bottom) {

        return vec4(gray_value, gray_value, gray_value, 1.0);
    }
    else {
        // weird distance calculation for cool effect
        float dist = 1e3;
        dist = min(dist, distance(uvs, vec2(uvs.x, top)));
        dist = min(dist, distance(uvs, vec2(uvs.x, bottom)));
        dist = min(dist, distance(uvs, vec2(left, uvs.y)));
        dist = min(dist, distance(uvs, vec2(right, uvs.y)));

        return mix(vec4(gray_value, gray_value, gray_value, 1.0), pixel_colour, dist / distance(vec2(0, 0), vec2(BOX_X, BOX_Y)));
    }
}

void main() {
    vec4 pixel_colour = texture(frame_texture, uvs); // RBGA colour values range from 0 to 1, not 0 to 255
    output_colour = pixel_colour;

    if (use_shadow_realm_shader) {
        output_colour = shadow_realm_shader(output_colour);
    }

    // vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + time * 0.01) * 0.1, uvs.y);
    // f_color = vec4(texture(tex, sample_pos).rg, texture(tex, sample_pos).b * 1.5, 1.0);
}
