from math import sin, cos, radians
from subprocess import Popen, PIPE
from struct import pack, unpack

mem_offsets = {}
def mem(*args):
  """
  Communicate with the C memory management utility via subprocess.Popen
  Takes in a series of arguments as parameters for mem.exe
  Returns parsed response, throws on any failure from mem.exe
  """
  params = ['mem.exe']
  for arg in args:
    if isinstance(arg, bytes):
      params.append(bytes.hex(arg))
    elif isinstance(arg, str):
      params.append(arg)
    else:
      raise ValueError('Unknown argument type: ' + type(arg))

  proc = Popen(params, stdout=PIPE, stderr=PIPE, universal_newlines=True)
  stdout, stderr = proc.communicate()
  if stderr:
    raise Exception(stderr)
  elif args[0] == 'sigscan':
    return [bytes.fromhex(line) for line in stdout.strip().split('\n')]
  elif args[0] == 'read':
    return bytes.fromhex(stdout.strip())

class HLMVModel(object):
  def __init__(self, initial):
    """
    Iniitial model setup. Enable normal maps, set the background to white,
    and load the current rotation and translation from memory.
    If initial values are specified, rot and trans will be set instead.
    """

    # To avoid having to recompile mem.exe every time HLMV updates,
    # I have switched the hard-coded offsets to instead use "signature scans".
    # These are hex-encoded assembly bytes which preceed the usage of these
    # particular HLMV variables.
    # mem.exe will search for these bytes and return the assembly (also in hex)
    # and we can then decode that assembly back into the offset of the variable.
    sigscans = mem('sigscan',
      '81CA00010000803D', # normals
      '50F30F2CC0F30F1005', # color
      '8B4328A80274', # rotation and position
      '558BEC81ECE8010000', # background
    )

    self.mem_offsets = {}

    # Normal mapping
    self.mem_offsets['nm'] = str(unpack('<i', sigscans[0][8:12])[0] - 0x410000)
    # Background color
    self.mem_offsets['color'] = str(unpack('<i', sigscans[1][9:13])[0] - 0x410000)

    object_ref = str(unpack('<i', sigscans[2][29:33])[0] - 0x410000)
    object_base = unpack('<i', mem('read', '4', object_ref))[0] - 0x410000

    # Absolute rotation
    self.mem_offsets['rot'] = str(object_base + 0x08)
    self.mem_offsets['trans'] = str(object_base + 0x14)

    # Enable background
    self.mem_offsets['bg'] = str(unpack('<i', sigscans[3][11:15])[0] - 0x410000)

    # for k, v in self.mem_offsets.items():
    #   print(k, hex(int(v)))

    mem('write', self.mem_offsets['nm'], pack('b', 1))
    mem('write', self.mem_offsets['color'], pack('ffff', 1.0, 1.0, 1.0, 1.0))
    if initial['rotation']:
      self.rotation = initial['rotation']
      mem('write', self.mem_offsets['rot'], pack('fff', self.rotation))
    else: # Load from current state
      self.rotation = unpack('fff', mem('read', '12', self.mem_offsets['rot']))
    if initial['translation']:
      self.translation = initial['translation']
      mem('write', self.mem_offsets['trans'], pack('fff', self.translation))
    else:
      self.translation = unpack('fff', mem('read', '12', self.mem_offsets['trans']))
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
    Set the HLMV background to a given value.
    """
    mem('write', self.mem_offsets['bg'], pack('b', value*1))

  def rotate(self, x, y):
    """
    Rotate the model to coordinates x, y from its initial rotation.
    X rotation is around the vertical axis, aka yaw
    Y rotation is around the horizontal axis, aka pitch

    Note that HLMV uses degrees while python uses radians.
    """

    mem('write', self.mem_offsets['rot'], pack('fff',
      self.rotation[0] + x,
      self.rotation[1] + y,
      self.rotation[2]
    ))

    x = radians(x)
    y = radians(y)

    xy_shift = sin(x)*sin(y)*self.vert_offset
    mem('write', self.mem_offsets['trans'], pack('fff',
      self.translation[0] + cos(y)*self.rot_offset + xy_shift,
      self.translation[1] + sin(y)*self.rot_offset + xy_shift,
      self.translation[2] - sin(x)*self.rot_offset
    ))
