import struct

class V3(object):
  def __init__(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z
  def __str__(self):
    return '%.1f, %.1f, %.1f'%(self.x, self.y, self.z)

class V2(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y

def sum(v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
  return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v0, v1):
  return V3(
    v0.y * v1.z - v0.z * v1.y,
    v0.z * v1.x - v0.x * v1.z,
    v0.x * v1.y - v0.y * v1.x,
  )

def length(v0):
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
  v0length = length(v0)
  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def char(c):
  return struct.pack('=c', c.encode('ascii'))

def word(w):
  return struct.pack('=h', w)

def dword(d):
  return struct.pack('=l', d)

def ccolor(v):
  return max(0, min(255, int(v)))

class color(object):
  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r, g, b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other
    return color(r, g, b)
  
  
  def toBytes(self):
    r = ccolor(self.r)
    g = ccolor(self.g)
    b = ccolor(self.b)
    return bytes([b, g, r])


def writebmp(filename, width, height, pixels):
  f = open(filename, 'bw')

  f.write(char('B'))
  f.write(char('M'))
  f.write(dword(54 + width * height * 3))
  f.write(dword(0))
  f.write(dword(54))

  f.write(dword(40))
  f.write(dword(width))
  f.write(dword(height))
  f.write(word(1))
  f.write(word(24))
  f.write(dword(0))
  f.write(dword(width * height * 3))
  f.write(dword(0))
  f.write(dword(0))
  f.write(dword(0))
  f.write(dword(0))
  for y in range(height):
    for x in range(width):
      f.write(pixels[y][x].toBytes())
    for _ in range(width % 4):
      f.write(struct.pack('=x'))
  f.close()

def reflect(I, N):
  TurnLight = mul(I, -1)
  return norm(sub(TurnLight, mul(N, 2 * dot(N, TurnLight))))

def refract(I, N, refractive_index):
  cosi = -max(-1, min(1, dot(I, N)))
  etai = 1
  etat = refractive_index

  if cosi < 0:
    cosi = -cosi
    etai, etat = etat, etai
    N = mul(N, -1)
  
  eta = etai / etat
  k = 1 - eta**2 * (1 - cosi**2)
  if k < 0: return V3(1, 0, 0)
  cost = k**(1/2)

  return norm(sum(mul(I, eta), mul(N, eta * cosi - cost)))

class Texture(object):
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
    #print(pixel_size)
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

  def get_color(self, tx, ty):
    x = int(tx * self.width)
    y = int(ty * self.height)
    if x >= self.width: x = self.width - 1
    if y >= self.height: y = self.height - 1

    return self.pixels[y][x]

class Material(object):
  def __init__(self, diffuse, albedo, spec, refractive_index = 0, texture=None, top_texture=None):
    self.diffuse = diffuse
    self.albedo = albedo
    self.spec = spec
    self.refractive_index = refractive_index
    self.texture = Texture(texture) if texture else None
    self.top_texture = Texture(top_texture) if top_texture else None

class Intersect(object):
  def __init__(self, distance, normal, point):
    self.distance = distance
    self.normal = normal
    self.point = point

class Light(object):
  def __init__(self, position, intensity, color):
    self.position = position
    self.intensity = intensity
    self.color = color
