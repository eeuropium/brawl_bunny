#version 330 core

const int WIDTH = 320, HEIGHT = 180;
const int MAX_SPHERES = 20;

uniform sampler2D frame_texture;
uniform float time;
uniform bool use_shadow_realm_shader;

uniform vec3 orbs_data[MAX_SPHERES];
uniform vec3 light_orb;
uniform vec2 light_beam_start;
uniform vec2 light_beam_end;

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

vec4 orbs_shader(vec4 pixel_colour) {
    float x_coor = uvs.x * WIDTH, y_coor = uvs.y * HEIGHT;

    vec2 view_dir = normalize(vec2(0.5 - uvs.x, 1.0 - uvs.y));
    // vec2 view_dir = normalize(vec2(0.5 - uvs.x, 0.5 - uvs.y)); // Assuming the center of the screen is the view direction

    for (int i = 0; i < MAX_SPHERES; i++) {
        vec3 orb = orbs_data[i];

        if (orb.z == 0.0) break; // 0 radius, meaning no orbs left to process

        vec2 orb_center = orb.xy;
        float orb_radius = orb.z;

        // Check if the pixel is inside the orb
        if (distance(vec2(x_coor, y_coor), orb.xy) > orb.z) continue;

        // Calculate the vector from the orb center to the current pixel
        vec2 to_pixel = vec2(x_coor, y_coor) - orb_center;

        // Calculate the surface normal of the orb
        vec2 surface_normal = normalize(to_pixel);

        // Calculate the angle between the view direction and the surface normal
        float fresnel = dot(view_dir, surface_normal);

        // Apply Fresnel effect to the pixel color
        // pixel_colour.rgb *= 1.0 - fresnel * 0.5; // Adjust the strength of the Fresnel effect

        pixel_colour.rgb += 0.005 * (vec3(57, 71, 120) * (1.0 - fresnel * 0.5));
        // pixel_colour.rgb = mix(pixel_colour.rgb, vec3(57, 71, 120), 0.1);

        // pixel_colour = mix(pixel_colour, vec4(57, 71, 120, 255),fresnel * 0.5); // Adjust the strength and exponent of the Fresnel effect

        return pixel_colour;
    }

    return pixel_colour;
}

vec4 light_orb_shader(vec4 pixel_colour) {
    // calculate coordinates in the game using uvs
    vec2 coor = vec2(uvs.x * WIDTH, uvs.y * HEIGHT);

    // radius is 0
    if (light_orb.z == 0.0) return pixel_colour;

    // distance from pixel to center of the light orb
    float dist = distance(coor, light_orb.xy);

    // pixel is greater than radius of orb, so we return
    if (dist > light_orb.z) return pixel_colour;

    vec3 col = vec3(223, 246, 245);

    float t = 1 - pow(dist / light_orb.z, 2);
    if (t < 0.05) t = 1;

    return mix(vec4(244, 179, 27, 255) / 255, vec4(col / 255, 1.0), t);
    // return vec4(mix(pixel_colour.rgb, vec3(244, 204, 161), 1 - alpha), 0);  // vec4(244, 204, 161, alpha);
}

vec4 light_beam_shader(vec4 pixel_colour) {
    return pixel_colour;

    // calculate coordinates in the game using uvs
    vec2 coor = vec2(uvs.x * WIDTH, uvs.y * HEIGHT);

    if (distance(coor, light_beam_start) < 40) return vec4(0, 1, 0, 1);

    // no light beam currently
    if (light_beam_start == vec2(-1, -1) && light_beam_end == vec2(-1, -1)) return pixel_colour;

    float gradient = (light_beam_start.y - light_beam_end.y) / (light_beam_start.x - light_beam_end.x);

    if (gradient == 0) {
        return pixel_colour;
    }
    else {
        float y = light_beam_start.y + (coor.x - light_beam_start.x) * gradient;

        if (distance(vec2(coor.x, y), coor) <= 0.5) {
            return vec4(1, 0, 0, 1);
        }
    }

    return pixel_colour;
    // sin(20 * uvs.y + 3 * time);

// 378545
}

void main() {
    vec4 pixel_colour = texture(frame_texture, uvs); // RBGA colour values range from 0 to 1, not 0 to 255
    output_colour = pixel_colour;

    // shadow realm shader
    if (use_shadow_realm_shader) {
        output_colour = shadow_realm_shader(output_colour);
    }

    // orbs shader
    output_colour = orbs_shader(output_colour);

    // light orb shader
    output_colour = light_orb_shader(output_colour);

    // light beam shader
    output_colour = light_beam_shader(output_colour);
    // vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + time * 0.01) * 0.1, uvs.y);
    // f_color = vec4(texture(tex, sample_pos).rg, texture(tex, sample_pos).b * 1.5, 1.0);
}
