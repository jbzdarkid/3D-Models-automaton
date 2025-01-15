from math import sin, cos, radians
from subprocess import Popen, PIPE
from struct import pack, unpack

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
    return [bytes.fromhex(line) for line in stdout.split(' ')]
  elif args[0] == 'read':
    return bytes.fromhex(stdout.strip())

class HLMVModel(object):
  def __init__(self, initial = None):
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
    sigscans = mem('sigscan', # this closing paren is because vim is an idiot )
      # Shared between HLMV and HLMV++ x86
      '50F30F2CC0F30F1005', # color
      '558BEC81ECE8010000', # background

      # HLMV
      '81CA00010000803D', # normals
      '8B4328A80274', # position and rotation

      # HLMV++ x86
      '81CA0001000025FFFEFFFF', # normals
      'EB2FA802742B', # position and rotation

      # HLMV++ x64
      '0FBAEA080FBAF008', # normals
      '55488DA8F8FDFFFF', # background
      'F3440F2CC1F3440F2CC8', # color
      'EB32A802742E', # position and rotation

      # Jed's HLMV v1.36
      'D95C240C8BF1', # color
      'D9542404D9EE', # position and rotation
    )

    self.mem_offsets = {}

    base_addr = unpack('>Q', sigscans.pop(0))[0]

    if sigscans[5]:
      print('Detected HLMV')

      # Background color
      self.mem_offsets['color'] = str(unpack('<i', sigscans[1][9:13])[0] - base_addr)

      # Enable background
      self.mem_offsets['bg'] = str(unpack('<i', sigscans[3][11:15])[0] - base_addr)

      # Normal mapping
      self.mem_offsets['nm'] = str(unpack('<i', sigscans[5][8:12])[0] - base_addr)

      # Absolute rotation and translation
      object_ref = str(unpack('<i', sigscans[7][29:33])[0] - base_addr)
      object_base = unpack('<i', mem('read', '4', object_ref))[0] - base_addr
      self.mem_offsets['rot'] = str(object_base + 0x08)
      self.mem_offsets['trans'] = str(object_base + 0x14)
      self.mem_offsets['skin'] = str(object_base + 0x24)

    elif sigscans[9]:
      print('Detected HLMV++ x86')

      # Background color
      self.mem_offsets['color'] = str(unpack('<i', sigscans[1][9:13])[0] - base_addr)

      # Enable background
      self.mem_offsets['bg'] = str(unpack('<i', sigscans[3][11:15])[0] - base_addr)

      # Normal mapping
      self.mem_offsets['nm'] = str(unpack('<i', sigscans[9][13:17])[0] - base_addr)

      # Absolute rotation and translation
      object_ref = str(unpack('<i', sigscans[11][29:33])[0] - base_addr)
      object_base = unpack('<i', mem('read', '4', object_ref))[0] - base_addr
      self.mem_offsets['rot'] = str(object_base + 0x08)
      self.mem_offsets['trans'] = str(object_base + 0x14)

    elif sigscans[13]:
      print('Detected HLMV++ x64')

      # Normal mapping
      normals = unpack('>Q', sigscans[12])[0] + unpack('<i', sigscans[13][10:14])[0] + 15
      self.mem_offsets['nm'] = str(normals - base_addr)

      # Enable background
      background = unpack('>Q', sigscans[14])[0] + unpack('<i', sigscans[15][17:21])[0] + 22
      self.mem_offsets['bg'] = str(background - base_addr)

      # Background color
      color = unpack('>Q', sigscans[16])[0] + unpack('<i', sigscans[17][14:18])[0] + 18
      self.mem_offsets['color'] = str(color - base_addr)

      # Object rotation, translation, and skin
      object_ref = unpack('>Q', sigscans[18])[0] + unpack('<i', sigscans[19][32:36])[0] + 36
      object_base = unpack('<Q', mem('read', '8', str(object_ref - base_addr)))[0] - base_addr
      self.mem_offsets['rot'] = str(object_base + 0x10)
      self.mem_offsets['trans'] = str(object_base + 0x1C)
      self.mem_offsets['skin'] = str(object_base + 0x2C)

    elif sigscans[20]:
      print('Detected Jed\'s HLMV')

      # Background color
      self.mem_offsets['color'] = str(unpack('<i', sigscans[21][8:12])[0] - base_addr - 8)

      # Absolute rotation and translation
      trans = unpack('<i', sigscans[23][8:12])[0] - base_addr
      self.mem_offsets['trans'] = str(trans)
      self.mem_offsets['rot'] = str(trans - 12)

    else:
      print('\n'.join((f'{i} {scan}' for i, scan in enumerate(sigscans))))
      raise ValueError('Unable to determine HLMV/HLMV++ version, please recompute sigscans')

    if 'nm' in self.mem_offsets:
      mem('write', pack('b', 1), self.mem_offsets['nm'])

    if not initial:
      initial = {}

    mem('write', pack('ffff', 1.0, 1.0, 1.0, 1.0), self.mem_offsets['color'])
    if initial.get('rotation', None):
      self.rotation = initial['rotation']
      mem('write', pack('fff', self.rotation), self.mem_offsets['rot'])
    else: # Load from current state
      self.rotation = unpack('fff', mem('read', '12', self.mem_offsets['rot']))
    if initial.get('translation', None):
      self.translation = initial['translation']
      mem('write', pack('fff', self.translation), self.mem_offsets['trans'])
    else:
      self.translation = unpack('fff', mem('read', '12', self.mem_offsets['trans']))
    if initial.get('rotation_offset', None):
      self.rot_offset = initial['rotation_offset']
    else:
      self.rot_offset = 0
    if initial.get('vertical_offset', None):
      self.vert_offset = initial['vertical_offset']
    else:
      self.vert_offset = 0

  def set_background(self, value):
    """
    Enable or disable the HLMV background. False -> 0 -> white, True -> 1 -> black.
    """
    if 'bg' in self.mem_offsets:
      mem('write', pack('b', value*1), self.mem_offsets['bg'])
    elif 'color' in self.mem_offsets:
      if value:
        mem('write', pack('ffff', 0.0, 0.0, 0.0, 1.0), self.mem_offsets['color'])
      else:
        mem('write', pack('ffff', 1.0, 1.0, 1.0, 1.0), self.mem_offsets['color'])

  def set_skin(self, value):
    """
    Change a model's skin (e.g. from RED to BLU).
    I have no idea what this does if the model has only one skin.
    """
    mem('write', pack('<i', value), self.mem_offsets['skin'])

  def rotate(self, x, y):
    """
    Rotate the model to coordinates x, y from its initial rotation.
    X rotation is around the vertical axis, aka yaw
    Y rotation is around the horizontal axis, aka pitch

    Note that HLMV uses degrees while python uses radians.
    """

    mem('write', pack('fff',
      self.rotation[0] + x,
      self.rotation[1] + y,
      self.rotation[2]
    ), self.mem_offsets['rot'])

    x = radians(x)
    y = radians(y)

    xy_shift = sin(x)*sin(y)*self.vert_offset
    mem('write', pack('fff',
      self.translation[0] + cos(y)*self.rot_offset + xy_shift,
      self.translation[1] + sin(y)*self.rot_offset + xy_shift,
      self.translation[2] - sin(x)*self.rot_offset
    ), self.mem_offsets['trans'])
