import struct
from lib import *
from math import atan2, pi, acos

class Envmap(object):
  def __init__(self, path):
    self.path = path
    self.read()
  
  def read(self):
    image = open(self.path, 'rb')
    image.seek(10)
    header_size = struct.unpack('=l', image.read(4))[0]
    image.seek(18)

    self.width = struct.unpack('=l', image.read(4))[0]
    self.height = struct.unpack('=l', image.read(4))[0]
    self.pixels = []
    image.seek(28)
    pixel_size = struct.unpack('=h', image.read(2))[0]
    image.seek(header_size)
    for y in range(self.height):
      self.pixels.append([])
      for _ in range(self.width):
        b = ord(image.read(1))
        g = ord(image.read(1))
        r = ord(image.read(1))
        if pixel_size == 32: image.read(1)
        self.pixels[y].append(color(r, g, b))
    image.close()

  def get_color(self, direction):
    direction = norm(direction)
    x = int((atan2(direction.z, direction.x) / (2 * pi) + 0.5) * self.width)
    y = int(acos(-direction.y) / pi * self.height)
    return self.pixels[y][x]
