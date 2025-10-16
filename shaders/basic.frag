#version 330

//inyección de código en el Render Pipeline de la GPU que gestiona cada píxel generado en la rasterización de un objeto poligonal. Siempre debe devolver un vec4 de color (r,g,b,a) donde alpha es la transparencia del color.

in vec3 v_color;
out vec4 f_color;

void main() {
    f_color = vec4(v_color, 1.0);
}