"""
The base automation file. Coordinates between HLMV and image processing.
Recolors and captures pictures of a 3d model.
Load up your model in HLMV, then run this script.
"""

from os import path, remove
import sys
from numpy import array

from PIL import ImageFile, Image

from importlib import import_module
Wiki = import_module('TFWiki-scripts.wikitools.wiki').Wiki
Page = import_module('TFWiki-scripts.wikitools.page').Page

IMAGE_TITLES = [
  ("0 - Unpainted RED.tga", "%s RED.png"),
  ("1 - Unpainted BLU.tga", "%s BLU.png"),
  ("2 - (E6E6E6) - An Extraordinary Abundance of Tinge.tga", "Painted %s E6E6E6.png"),
  ("3 - (D8BED8) - Color No 216-190-216.tga", "Painted %s D8BED8.png"),
  ("4 - (C5AF91) - Peculiarly Drab Tincture.tga", "Painted %s C5AF91.png"),
  ("5 - (7E7E7E) - Aged Moustache Grey.tga", "Painted %s 7E7E7E.png"),
  ("6 - (141414) - A Distinctive Lack of Hue.tga", "Painted %s 141414.png"),
  ("7 - (2D2D24) - After Eight.tga", "Painted %s 2D2D24.png"),
  ("8 - (694D3A) - Radigan Conagher Brown.tga", "Painted %s 694D3A.png"),
  ("9 - (7C6C57) - Ye Olde Rustic Colour.tga", "Painted %s 7C6C57.png"),
  ("10 - (A57545) - Muskelmannbraun.tga", "Painted %s A57545.png"),
  ("11 - (CF7336) - Mann Co Orange.tga", "Painted %s CF7336.png"),
  ("12 - (E7B53B) - Australium Gold.tga", "Painted %s E7B53B.png"),
  ("13 - (F0E68C) - The Color of a Gentlemann Business Pants.tga", "Painted %s F0E68C.png"),
  ("14 - (E9967A) - Dark Salmon Injustice.tga", "Painted %s E9967A.png"),
  ("15 - (FF69B4) - Pink as Hell.tga", "Painted %s FF69B4.png"),
  ("16 - (7D4071) - A Deep Commitment to Purple.tga", "Painted %s 7D4071.png"),
  ("17 - (51384A) - Noble Hatter's Violet.tga", "Painted %s 51384A.png"),
  ("18 - (2F4F4F) - A Color Similar to Slate.tga", "Painted %s 2F4F4F.png"),
  ("19 - (424F3B) - Zepheniah Greed.tga", "Painted %s 424F3B.png"),
  ("20 - (808000) - Drably Olive.tga", "Painted %s 808000.png"),
  ("21 - (729E42) - Indubitably Green.tga", "Painted %s 729E42.png"),
  ("22 - (32CD32) - The Bitter Taste of Defeat and Lime.tga", "Painted %s 32CD32.png"),
  ("23 - (BCDDB3) - A Mann's Mint.tga", "Painted %s BCDDB3.png"),
  ("24 - (A89A8C) - Waterlogged Lab Coat - RED.tga", "Painted %s A89A8C.png"),
  ("25 - (839FA3) - Waterlogged Lab Coat - BLU.tga", "Painted %s 839FA3.png"),
  ("26 - (3B1F23) - Balaclavas Are Forever - RED.tga", "Painted %s 3B1F23.png"),
  ("27 - (18233D) - Balaclavas Are Forever - BLU.tga", "Painted %s 18233D.png"),
  ("28 - (B8383B) - Team Spirit - RED.tga", "Painted %s B8383B.png"),
  ("29 - (5885A2) - Team Spirit - BLU.tga", "Painted %s 5885A2.png"),
  ("30 - (483838) - Operator's Overalls - RED.tga", "Painted %s 483838.png"),
  ("31 - (384248) - Operator's Overalls - BLU.tga", "Painted %s 384248.png"),
  ("32 - (803020) - The Value of Teamwork - RED.tga", "Painted %s 803020.png"),
  ("33 - (256D8D) - The Value of Teamwork - BLU.tga", "Painted %s 256D8D.png"),
  ("34 - (654740) - An Air of Debonair - RED.tga", "Painted %s 654740.png"),
  ("35 - (28394D) - An Air of Debonair - BLU.tga", "Painted %s 28394D.png"),
  ("36 - (C36C2D) - Cream Spirit - RED.tga", "Painted %s C36C2D.png"),
  ("37 - (B88035) - Cream Spirit - BLU.tga", "Painted %s B88035.png"),
]

if __name__ == '__main__':
  if len(sys.argv) > 1:
    folder = sys.argv[1]
  else:
    folder = input('Please provide the folder where the images were saved: ')
  
  if not path.exists(folder):
    print(f'ERROR: Folder {folder} does not exist.')
    sys.exit(0)

  images = [Image.open(folder / image[0]) for image in IMAGE_TITLES]

  # Extracted and adapted from imageprocessor.py
  # This will get folded back in if we take screenshots internally.
  cropping = {'left': [], 'top': [], 'right': [], 'bottom': []}
  for image in images:
    # This needs to be dtype=int to prevent an overflow when adding
    # Calculate crop lines by looking for all-white && all-black pixels, i.e. places where the luma is zero.
    # np.any() will return 'True' for any rows which contain nonzero integers (because zero is Falsy).
    # Then, we use nonzero() to get the only indices which are 'True', which are the rows with content.
    # (nonzero returns a tuple for some reason, so we also have to [0] it.)
    blended_arr = array(image, dtype=int)
    horizontal = blended_arr[:, :, 3].any(axis=0).nonzero()[0]
    vertical = blended_arr[:, :, 3].any(axis=1).nonzero()[0]

    cropping['left'].append(horizontal[0])
    cropping['top'].append(vertical[0])
    cropping['right'].append(horizontal[-1])
    cropping['bottom'].append(vertical[-1])

  min_cropping = (
    min(cropping['left']),
    min(cropping['top']),
    max(cropping['right']),
    max(cropping['bottom'])
  )
  print("Computed HLMV viewport bounds (minimum cropping):", min_cropping)
  
  images = [image.crop(min_cropping) for image in images]

  cosmetic = input('Cosmetic file name: ')
  description = '''== Summary ==
== Licensing ==
{{ScreenshotTF2}}
[[Category:Painted item images]]
'''

  output_file = 'temp.jpg'
  if path.exists(output_file):
    remove(output_file)
  # Ensure there is enough allocated space to save the image as progressive
  ImageFile.MAXBLOCK = image.height * image.width * 8

  try:
    wiki = Wiki('https://wiki.teamfortress.com/w/api.php')
    username = input('Wiki username: ')
    for i in range(3):
      if wiki.login(username):
        break

    for i, image in enumerate(images):
      title = IMAGE_TITLES[i][1] % cosmetic
      image.convert('RGB').save(output_file, 'PNG', quality=100, progressive=True, optimize=True)
      
      page = Page(wiki, title)
      with open(output_file, 'rb') as file:
        r = page.upload(file, description)
      if r:
        print(f'WARNING: Failed to upload {title}: {r}')
  except:
    import traceback
    print('Upload failed!')
    traceback.print_exc()
