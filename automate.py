"""
The base automation file. Coordinates between HLMV and image processing.
Rotates and captures pictures of a 3d model.
Load up your model in HLMV, then run this script.
"""

from __future__ import print_function, absolute_import
from time import sleep

from PIL.ImageGrab import grab
from win32con import SW_MAXIMIZE
from win32gui import (EnumWindows, GetWindowRect, GetWindowText,
  SetForegroundWindow, ShowWindow)

from imageprocessor import ImageProcessor
from HLMVModel import HLMVModel

if __name__ == '__main__':
  number_of_images = 24 # Y rotations
  vertical_rotations = 1 # X rotations
  # Initial parameters. Mostly, you won't need to set these.
  model = HLMVModel({
    'rotation': None,
    'translation': None,
    'rotation_offset': 7,
    'vertical_offset': None,
    })
  ip = ImageProcessor(number_of_images, vertical_rotations)

  def enum_callback(hwnd, _):
    """
    Focus and maximise HLMV
    then compute the cropping boundary based on its resulting size
    """
    if GetWindowText(hwnd)[:7] == 'models\\':
      SetForegroundWindow(hwnd)
      ShowWindow(hwnd, SW_MAXIMIZE)
      rect = GetWindowRect(hwnd)
      global crop_boundary
      crop_boundary = (
        rect[0] + 10, # Left edge <-> image left
        rect[1] + 51, # Top edge <-> image top
        rect[2] - 10, # Left edge <-> image right
        rect[3] - 250 # Top edge <-> image bottom
      )
  crop_boundary = None
  EnumWindows(enum_callback, [])
  if not crop_boundary:
    print("Couldn't find HLMV, is it open with a model loaded?")
    exit()
  else:
    print("Auto-computed crop boundary:", crop_boundary)

  white_images = []
  model.set_background('white')
  # Loops in this order to get the images in the right order.
  for y_rot in range(0, 360, 360//number_of_images):
    for x_rot in range(-15*vertical_rotations, 15*vertical_rotations+1, 15):
      model.rotate(x_rot, y_rot)
      sleep(0.02) # Wait for redraw
      white_images.append(grab().crop(crop_boundary))

  black_images = []
  model.set_background('black')
  for y_rot in range(0, 360, 360//number_of_images):
    for x_rot in range(-15*vertical_rotations, 15*vertical_rotations+1, 15):
      model.rotate(x_rot, y_rot)
      sleep(0.02) # Wait for redraw
      black_images.append(grab().crop(crop_boundary))
  model.rotate(0, 0) # Reset back to starting rotation for user

  print('Blending...' + ' '*(len(white_images) - 12) + '|')
  for (white_image, black_image) in zip(white_images, black_images):
    print('#', end='')
    ip.blend(white_image, black_image)
  print('')
  ip.stitch_and_upload()
