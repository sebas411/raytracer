from cube import Cube
from lib import *
from math import pi, tan
from random import random

from sphere import Sphere
from envmap import Envmap

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)
GREY = color(150, 150, 150)

MAX_RECURSION_DEPTH = 3

class Raytracer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.clear()
    self.background_color = BLACK

  def clear(self):
    self.pixels = [
      [BLACK for x in range(self.width)]
      for y in range(self.height)
    ]

  def write(self, filename):
    writebmp(filename, self.width, self.height, self.pixels)

  def point(self, x, y, col):
    self.pixels[y][x] = col

  def cast_ray(self, origin, direction, recursion = 0):
    material, intersect = self.scene_intersect(origin, direction)
    if material is None or recursion >= MAX_RECURSION_DEPTH:
      if self.envmap: return self.envmap.get_color(direction)
      return self.background_color

    light_dir = norm(sub(self.light.position, intersect.point))
    light_distance = length(sub(self.light.position, intersect.point))

    offset_normal = mul(intersect.normal, 0.1)
    shadow_origin = sum(intersect.point, offset_normal) if dot(intersect.normal, light_dir) > 0 else sub(intersect.point, offset_normal)
    shadow_material, shadow_intersect = self.scene_intersect(shadow_origin, light_dir)
    if shadow_material is None or length(sub(shadow_intersect.point, shadow_origin)) > light_distance: shadow_intensity = 0
    else: shadow_intensity = 0.6

    if material.albedo[2] > 0:
      reverse_direction = mul(direction, -1)
      reflect_direction = reflect(reverse_direction, intersect.normal)
      reflect_origin = sub(intersect.point, offset_normal) if dot(reflect_direction, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      reflect_color = self.cast_ray(reflect_origin, reflect_direction, recursion + 1)
    else:
      reflect_color = BLACK

    if material.albedo[3] > 0:
      refract_direction = refract(direction, intersect.normal, material.refractive_index)
      if refract_direction is None:
        refract_color = BLACK
      else:
        refract_origin = sub(intersect.point, offset_normal) if dot(refract_direction, intersect.normal) < 0 else sum(intersect.point, offset_normal)
        refract_color = self.cast_ray(refract_origin, refract_direction, recursion + 1)
    else:
      refract_color = BLACK

    intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)
    if material.texture:
      if intersect.normal.z != 0:
        tx = intersect.point.x - int(intersect.point.x) 
        ty = intersect.point.y - int(intersect.point.y)
      elif intersect.normal.y != 0:
        tx = intersect.point.x - int(intersect.point.x) 
        ty = intersect.point.z - int(intersect.point.z)
      else:
        ty = intersect.point.y - int(intersect.point.y)
        tx = intersect.point.z - int(intersect.point.z)
      if material.top_texture and intersect.normal.y != 0:
        diffuse = material.top_texture.get_color(tx, ty) * (intensity * material.albedo[0])
      else:
        diffuse = material.texture.get_color(tx, ty) * (intensity * material.albedo[0])
    else:
      diffuse = material.diffuse * (intensity * material.albedo[0])

    specular_reflection = reflect(light_dir, intersect.normal)
    specular_intensity = self.light.intensity * max(0, -dot(specular_reflection, direction))**material.spec if shadow_intensity == 0 else 0
    specular = self.light.color * specular_intensity * material.albedo[1]
    
    reflection = reflect_color * material.albedo[2]
    refraction = refract_color * material.albedo[3]
    
    c = diffuse + specular + reflection + refraction
    return c

  def scene_intersect(self, origin, direction):
    zbuffer = float('inf')
    material = None
    retintersect = None
    for obj in self.scene:
      intersect = obj.ray_intersect(origin, direction)
      if intersect:
        if intersect.distance < zbuffer:
          zbuffer = intersect.distance
          material = obj.material
          retintersect = intersect
    return material, retintersect

  def render(self):
    fov = pi/2
    ar = self.width / self.height
    c1 = tan(fov/2)

    for y in range(self.height):
      for x in range(self.width):
        if random() > 0:
          i = ((2 * x + 1) / self.width - 1) * c1 * ar
          j = (1 - (2 * y + 1) / self.height) * c1

          direction = norm(sum(V3(i, -j, 0), self.orientation))

          col = self.cast_ray(self.camera, direction)
          self.point(x, y, col)

r = Raytracer(1920, 1080)
#r = Raytracer(854, 480)

r.camera = V3(5, 5, 4)
r.orientation = V3(0, -0.75, -1)

r.light = Light(
  position = V3(20, 20, 20),
  intensity = 2,
  color = color(255, 255, 200)
)

def setCubes(pos, size, material):
  cubes = []
  for x in range(size.x):
    for y in range(size.y):
      for z in range(size.z):
        cubes.append(Cube(V3(pos.x + x, pos.y + y, pos.z - z), material))
  return cubes

diamond = Material(diffuse=color(50, 75, 180), albedo=[0.7, 0.1, 0.55, 0], spec=10, texture='./textures/diamond.bmp')
grass = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/grass.bmp', top_texture='./textures/grass_top.bmp')
log = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/log.bmp', top_texture='./textures/log_top.bmp')
planks = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/planks.bmp')
leaves = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/leaves.bmp')
door_bottom = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/door_bottom.bmp')
door_top = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/door_top.bmp')

r.scene = [
  Cube(V3(1, 3, -1), leaves),
  Cube(V3(0, 3, -2), leaves),
  Cube(V3(2, 3, -2), leaves),
  Cube(V3(1, 4, -2), leaves),
  Cube(V3(1, 1, -2), log),
  Cube(V3(1, 2, -2), log),
  Cube(V3(4, 1, -1), diamond),
  Cube(V3(5, 1, -1), diamond),
  Cube(V3(6, 1, -4), door_bottom),
  Cube(V3(7, 1, -4), door_bottom),
  Cube(V3(6, 2, -4), door_top),
  Cube(V3(7, 2, -4), door_top),
]
r.scene.extend(setCubes(V3(0, 0, 0), V3(4, 1, 10), grass))
r.scene.extend(setCubes(V3(4, 0, 0), V3(6, 1, 4), grass))
r.scene.extend(setCubes(V3(5, 3, -5), V3(4, 1, 4), planks))
r.scene.extend(setCubes(V3(4, 3, -4), V3(1, 1, 6), log))
r.scene.extend(setCubes(V3(9, 3, -4), V3(1, 1, 6), log))
r.scene.extend(setCubes(V3(5, 3, -4), V3(4, 1, 1), log))
r.scene.extend(setCubes(V3(5, 3, -9), V3(4, 1, 1), log))
r.scene.extend(setCubes(V3(4, 1, -4), V3(1, 2, 1), log))
r.scene.extend(setCubes(V3(5, 1, -4), V3(1, 2, 1), planks))
r.scene.extend(setCubes(V3(8, 1, -4), V3(1, 2, 1), planks))
r.scene.extend(setCubes(V3(9, 1, -4), V3(1, 2, 1), log))

r.envmap = Envmap('./textures/envmap.bmp')

r.render()
r.write('r.bmp')