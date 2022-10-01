"""
The base automation file. Coordinates between HLMV and image processing.
Rotates and captures pictures of a 3d model.
Load up your model in HLMV, then run this script.
"""

from time import sleep

from PIL.ImageGrab import grab
from win32con import SW_MAXIMIZE
from win32gui import (EnumWindows, GetWindowRect, GetWindowText,
  SetForegroundWindow, ShowWindow)
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2) # Set python itself to be DPI-aware so that we can compute boundaries correctly.

from imageprocessor import ImageProcessor
from HLMVModel import HLMVModel

if __name__ == '__main__':
  number_of_images = 24 # Y rotations
  vertical_rotations = 1 # X rotations
  # Initial parameters. Mostly, you won't need to set these.
  model = HLMVModel({
    'rotation': None,
    'translation': None,
    'rotation_offset': None,
    'vertical_offset': None
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
      global rect
      rect = GetWindowRect(hwnd)
  rect = None
  EnumWindows(enum_callback, [])
  if not rect:
    print("Couldn't find HLMV, is it open with a model loaded?")
    exit()
  else:
    print("Found HLMV, boundaries at:", rect)

  white_images = []
  model.set_background(False)
  # Loops in this order to get the images in the right order.
  for y_rot in range(0, 360, 360//number_of_images):
    for x_rot in range(-15*vertical_rotations, 15*vertical_rotations+1, 15):
      model.rotate(x_rot, y_rot)
      sleep(0.02) # Wait for redraw
      white_images.append(grab())

  black_images = []
  model.set_background(True)
  for y_rot in range(0, 360, 360//number_of_images):
    for x_rot in range(-15*vertical_rotations, 15*vertical_rotations+1, 15):
      model.rotate(x_rot, y_rot)
      sleep(0.02) # Wait for redraw
      black_images.append(grab())
  model.rotate(0, 0) # Reset back to starting rotation for user

  cropping = ip.find_minimum_bounds(white_images[0], black_images[0])
  print("Computed HLMV bounds (minimum cropping):", cropping)

  print('Blending...' + ' '*(len(white_images) - 12) + '|')
  for (white_image, black_image) in zip(white_images, black_images):
    print('#', end='', flush=True)
    white_image = white_image.crop(cropping)
    black_image = black_image.crop(cropping)
    ip.blend(white_image, black_image)
  print('')
  ip.stitch_and_upload()
