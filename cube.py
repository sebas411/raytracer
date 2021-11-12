from lib import *

class Cube(object):
  def __init__(self, center, material, l=1):
    self.center = center
    self.material = material
    self.l = l
  
  def ray_intersect(self, origin, direction):
    B0 = self.center
    B1 = sum(self.center, V3(self.l, self.l, self.l))

    if direction.x == 0: direction.x = 0.0001
    if direction.y == 0: direction.y = 0.0001
    if direction.z == 0: direction.z = 0.0001

    if direction.x >= 0:
      t0x = (B0.x - origin.x) / direction.x 
      t1x = (B1.x - origin.x) / direction.x
      coefx = -1
    else:
      t1x = (B0.x - origin.x) / direction.x 
      t0x = (B1.x - origin.x) / direction.x
      coefx = 1

    
    if direction.y >= 0:
      t0y = (B0.y - origin.y) / direction.y 
      t1y = (B1.y - origin.y) / direction.y 
      coefy = -1
    else:
      t1y = (B0.y - origin.y) / direction.y 
      t0y = (B1.y - origin.y) / direction.y 
      coefy = 1

    if direction.z >= 0:
      t0z = (B0.z - origin.z) / direction.z 
      t1z = (B1.z - origin.z) / direction.z
      coefz = -1
    else:
      t1z = (B0.z - origin.z) / direction.z 
      t0z = (B1.z - origin.z) / direction.z 
      coefz = 1


    if t0x > t1y or t0y > t1x or t0x > t1z or t0z > t1x or t0z > t1y or t0y > t1z:
      return None

    maxt0 = max(t0x, t0y, t0z)

    if t0x < 0:
      t0x = t1x

    if t0y < 0:
      t0y = t1y

    if t0z < 0:
      t0z = t1z

    if maxt0 == t0x:
      normal = V3(coefx, 0, 0)
    elif maxt0 == t0y:
      normal = V3(0, coefy, 0)
    else:
      normal = V3(0, 0, coefz)

    t0 = maxt0


    hit = sum(origin, mul(direction, t0))

    if t0x < 0 or t0y < 0 or t0z < 0:
      return None

    return Intersect(
      distance=t0,
      normal=normal,
      point=hit
    )