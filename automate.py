"""
The base automation file. Coordinates between HLMV and image processing.
Rotates and captures pictures of a 3d model.
Load up your model in HLMV, then run this script.
"""

import ctypes
import requests
from datetime import datetime
from hashlib import md5
from importlib import import_module
from os import path, remove
from time import sleep
from urllib.parse import quote

from PIL import ImageFile
from PIL.ImageGrab import grab
from win32con import SW_MAXIMIZE
from win32gui import (EnumWindows, GetWindowRect, GetWindowText,
  SetForegroundWindow, ShowWindow)

from imageprocessor import ImageProcessor
from HLMVModel import HLMVModel
Wiki = import_module('TFWiki-scripts.wikitools.wiki').Wiki
Page = import_module('TFWiki-scripts.wikitools.page').Page

VERSION = '3.3'
def check_for_updates():
  try:
    r = requests.get('https://api.github.com/repos/jbzdarkid/3D-Models-automaton/releases/latest', timeout=10)
    latest_release = r.json()['name']

    if latest_release.split('.') > VERSION.split('.'):
      print(f'A new version of the automation scripts are available. You are running {VERSION} but the latest release is {latest_release}.')
      print('Please download the latest version from https://github.com/jbzdarkid/3D-Models-automaton/releases/latest')
      sleep(10)

  except:
    pass


if __name__ == '__main__':
  ctypes.windll.shcore.SetProcessDpiAwareness(2) # Set python itself to be DPI-aware so that we can compute boundaries correctly.
  number_of_images = 24 # Y rotations
  vertical_rotations = 1 # X rotations
  bounds_override = (0, 0, 0, 0) # Left, Top, Right, Bottom

  check_for_updates()

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
    window_title = GetWindowText(hwnd)
    if 'models' in window_title or "Jed's Half-Life Model Viewer" in window_title:
      global rect
      if not rect:
        SetForegroundWindow(hwnd)
        ShowWindow(hwnd, SW_MAXIMIZE)
        rect = GetWindowRect(hwnd)
  rect = None
  EnumWindows(enum_callback, None)
  if not rect:
    print("Couldn't find HLMV, is it open with a model loaded?")
    exit()
  else:
    print("Found HLMV window boundaries:", rect)

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

  if sum(bounds_override) > 0:
    cropping = bounds_override
  else:
    cropping = ip.find_minimum_bounds(white_images[0], black_images[0])
  print("Computed HLMV viewport bounds (minimum cropping):", cropping)

  print('Blending...' + ' '*(len(white_images) - 12) + '|')
  for (white_image, black_image) in zip(white_images, black_images):
    print('#', end='', flush=True)
    white_image = white_image.crop(cropping)
    black_image = black_image.crop(cropping)
    ip.blend(white_image, black_image)
  print('')

  # This is fast enough to not need a progress bar.
  full_image, full_offset_map = ip.stitch()

  output_file = 'temp.jpg'
  if path.exists(output_file):
    remove(output_file)
  # Ensure there is enough allocated space to save the image as progressive
  ImageFile.MAXBLOCK = full_image.height * full_image.width * 8
  full_image.convert('RGB').save(output_file, 'JPEG', quality=100, progressive=True, optimize=True)
  title = input('Upload file name: ') + ' 3D.jpg'

  try:
    username = input('Wiki username: ')
    user_agent = input('Custom user agent: ').strip()
    wiki = Wiki('https://wiki.teamfortress.com/w/api.php', user_agent)
    for i in range(3):
      if wiki.login(username):
        break

    page = Page(wiki, 'File:' + title)
    with open(output_file, 'rb') as file:
      r = page.upload(file)
    if r:
      raise ValueError('Failed to upload %s: %s' % (file, r))
  except:
    import traceback
    traceback.print_exc()

    print('Upload failed, image & description saved to temp.jpeg & temp.txt')

  # Generate the description after uploading so that the timestamp is correct.
  title = title.replace(' ', '_')
  hash = md5(title.encode('utf-8')).hexdigest()
  url = 'https://wiki.teamfortress.com/w/images/%s/%s/%s' % (hash[:1], hash[:2], quote(title))
  category = '3D model images' if not title.startswith('User_') else 'User images'
  description = '''{{#switch: {{{1|}}}
| url = <nowiki>%s?%s</nowiki>
| map = \n%s
| height = %d
| startframe = 16
}}<noinclude>{{3D viewer}}[[Category:%s]]
{{Externally linked}}''' % (
    url,
    datetime.utcnow().timestamp(),
    full_offset_map,
    ip.target_dimension,
    category
    )

  output_text = 'temp.txt'
  if path.exists(output_text):
    remove(output_text)
  with open(output_text, 'w') as file:
    file.write(description)

  page.edit(description, summary='Automatic update using 3D-Models-automation', bot=False)
