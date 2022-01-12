from math import sin, cos, radians
from subprocess import Popen, PIPE

def mem(*params):
  """
  Communicate with the C memory management utility via subprocess.Popen
  Takes in a series of arguments as parameters for mem.exe
  Returns parsed response, raises all exceptions
  """
  params = ['mem.exe'] + [str(param) for param in params]
  proc = Popen(params, stdout=PIPE, stderr=PIPE, universal_newlines=True)
  stdout, stderr = proc.communicate()
  if stderr:
    raise Exception(stderr)
  if stdout:
    return [float(o) for o in stdout.split(' ')]

class HLMVModel(object):
  def __init__(self, initial):
    """
    Iniitial model setup. Enable normal maps, set the background to white,
    and load the current rotation and translation from memory.
    If initial values are specified, rot and trans will be set instead.
    """
    mem('nm', 0) # Disabled normal maps because I am getting black/purple
    # mem('color', '1.0', '1.0', '1.0', '1.0')
    if initial['rotation']:
      self.rotation = initial['rotation']
      mem('rot', *self.rotation)
    else: # Load from current state
      self.rotation = mem('rot')
    if initial['translation']:
      self.translation = initial['translation']
      mem('trans', *self.translation)
    else:
      self.translation = mem('trans')
    if initial['rotation_offset']:
      self.rot_offset = initial['rotation_offset']
    else:
      self.rot_offset = 0
    if initial['vertical_offset']:
      self.vert_offset = initial['vertical_offset']
    else:
      self.vert_offset = 0

  def set_background(self, value):
    """
    Set the HLMV background color to a given value.
    """
    if value == 'white':
      mem('color', 1.0, 1.0, 1.0, 1.0)
    elif value == 'black':
      mem('color', 0.0, 0.0, 0.0, 1.0)

  def rotate(self, x, y):
    """
    Rotate the model to coordinates x, y from its initial rotation.
    X rotation is around the vertical axis, aka yaw
    Y rotation is around the horizontal axis, aka pitch

    Note that HLMV uses degrees while python uses radians.
    """

    mem('rot',
        self.rotation[0] + x,
        self.rotation[1] + y,
        self.rotation[2]
       )

    x = radians(x)
    y = radians(y)

    xy_shift = sin(x)*sin(y)*self.vert_offset
    mem('trans',
        self.translation[0] + cos(y)*self.rot_offset + xy_shift,
        self.translation[1] + sin(y)*self.rot_offset + xy_shift,
        self.translation[2] - sin(x)*self.rot_offset
       )
