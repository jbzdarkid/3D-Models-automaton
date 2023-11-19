from math import sin, cos, radians
from subprocess import Popen, PIPE

mem_offsets = {}
def mem(command, *args):
  """
  Communicate with the C memory management utility via subprocess.Popen
  Takes in a series of arguments as parameters for mem.exe
  Returns parsed response, raises all exceptions
  """
  if command == 'sigscan':
    params = ['mem.exe', 'sigscan', *args]
  elif not args:
    params = ['mem.exe', 'read', str(mem_offsets[command])]
  else:
    params = ['mem.exe', 'write', str(mem_offsets[command])]
    for arg in args:
      params.append(bytes.hex(int.to_bytes(arg, byteorder='little')))
    print(params)

  proc = Popen(params, stdout=PIPE, stderr=PIPE, universal_newlines=True)
  stdout, stderr = proc.communicate()
  if stderr:
    raise Exception(stderr)
  if stdout:
    if params[1] == 'read':
      return [float(o) for o in stdout.split(' ')]
    elif params[1] == 'sigscan':
      print(stdout)
      return [bytes.fromhex(line) for line in stdout.strip().split('\n')]

class HLMVModel(object):
  def __init__(self, initial):
    """
    Iniitial model setup. Enable normal maps, set the background to white,
    and load the current rotation and translation from memory.
    If initial values are specified, rot and trans will be set instead.
    """

    # TODO explain
    sigscans = mem('sigscan', '81CA00010000803D')

    mem_offsets['nm'] = int.from_bytes(sigscans[0][8:12], byteorder='little') - 0x410000

    print(mem_offsets)

    mem('nm', 1)

    # int32_t normals = *(int32_t*)&data[index + 8];
    exit()

    self.mem_offsets = {
      'rot': 0x23C4B0, # Absolute Rotation
      'trans': 0x23C4C0, # Absolute Translation
      'color': 0x23F1B4, # Background color
      'bg': 0x23F17C, # Enable Background
      'nm': 0x23F12F, # Normal Maps
    }
    """
  } else if (strcmp(argv[1], "spec") == 0) { // Specular
    offset = (LPVOID)(base_addr + 0x23F131);
  } else if (strcmp(argv[1], "ob") == 0) { // Overbrightening
    offset = (LPVOID)(base_addr + 0x23F1DE);
  } else if (strcmp(argv[1], "lrot") == 0) { // Light Rotation
    offset = (LPVOID)(base_addr + 0x23F148);    }
    """

    mem('nm', 1)
    mem('color', '1.0', '1.0', '1.0', '1.0')
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
    Set the HLMV background to a given value.
    """
    mem('bg', value*1)

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
