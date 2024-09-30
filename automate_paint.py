"""
The base automation file. Coordinates between HLMV and image processing.
Recolors and captures pictures of a 3d model.
Load up your model in HLMV, then run this script.
"""

import sys
from numpy import array
from pathlib import Path

from PIL import ImageFile, Image

from importlib import import_module
Wiki = import_module('TFWiki-scripts.wikitools.wiki').Wiki
Page = import_module('TFWiki-scripts.wikitools.page').Page

FILENAME_TO_WIKI_PAGE = {
#  "0 - Unpainted RED.tga":                                        "Painted {name} UNPAINTED{style}.png",
  "0 - Unpainted RED.tga":                                        "RED {name}{style}.png",
  "1 - Unpainted BLU.tga":                                        "BLU {name}{style}.png",
  "2 - (E6E6E6) - An Extraordinary Abundance of Tinge.tga":       "Painted {name} E6E6E6{style}.png",
  "3 - (D8BED8) - Color No 216-190-216.tga":                      "Painted {name} D8BED8{style}.png",
  "4 - (C5AF91) - Peculiarly Drab Tincture.tga":                  "Painted {name} C5AF91{style}.png",
  "5 - (7E7E7E) - Aged Moustache Grey.tga":                       "Painted {name} 7E7E7E{style}.png",
  "6 - (141414) - A Distinctive Lack of Hue.tga":                 "Painted {name} 141414{style}.png",
  "7 - (2D2D24) - After Eight.tga":                               "Painted {name} 2D2D24{style}.png",
  "8 - (694D3A) - Radigan Conagher Brown.tga":                    "Painted {name} 694D3A{style}.png",
  "9 - (7C6C57) - Ye Olde Rustic Colour.tga":                     "Painted {name} 7C6C57{style}.png",
  "10 - (A57545) - Muskelmannbraun.tga":                          "Painted {name} A57545{style}.png",
  "11 - (CF7336) - Mann Co Orange.tga":                           "Painted {name} CF7336{style}.png",
  "12 - (E7B53B) - Australium Gold.tga":                          "Painted {name} E7B53B{style}.png",
  "13 - (F0E68C) - The Color of a Gentlemann Business Pants.tga": "Painted {name} F0E68C{style}.png",
  "14 - (E9967A) - Dark Salmon Injustice.tga":                    "Painted {name} E9967A{style}.png",
  "15 - (FF69B4) - Pink as Hell.tga":                             "Painted {name} FF69B4{style}.png",
  "16 - (7D4071) - A Deep Commitment to Purple.tga":              "Painted {name} 7D4071{style}.png",
  "17 - (51384A) - Noble Hatter's Violet.tga":                    "Painted {name} 51384A{style}.png",
  "18 - (2F4F4F) - A Color Similar to Slate.tga":                 "Painted {name} 2F4F4F{style}.png",
  "19 - (424F3B) - Zepheniah Greed.tga":                          "Painted {name} 424F3B{style}.png",
  "20 - (808000) - Drably Olive.tga":                             "Painted {name} 808000{style}.png",
  "21 - (729E42) - Indubitably Green.tga":                        "Painted {name} 729E42{style}.png",
  "22 - (32CD32) - The Bitter Taste of Defeat and Lime.tga":      "Painted {name} 32CD32{style}.png",
  "23 - (BCDDB3) - A Mann's Mint.tga":                            "Painted {name} BCDDB3{style}.png",
  "24 - (A89A8C) - Waterlogged Lab Coat - RED.tga":               "Painted {name} A89A8C{style}.png",
  "25 - (839FA3) - Waterlogged Lab Coat - BLU.tga":               "Painted {name} 839FA3{style}.png",
  "26 - (3B1F23) - Balaclavas Are Forever - RED.tga":             "Painted {name} 3B1F23{style}.png",
  "27 - (18233D) - Balaclavas Are Forever - BLU.tga":             "Painted {name} 18233D{style}.png",
  "28 - (B8383B) - Team Spirit - RED.tga":                        "Painted {name} B8383B{style}.png",
  "29 - (5885A2) - Team Spirit - BLU.tga":                        "Painted {name} 5885A2{style}.png",
  "30 - (483838) - Operator's Overalls - RED.tga":                "Painted {name} 483838{style}.png",
  "31 - (384248) - Operator's Overalls - BLU.tga":                "Painted {name} 384248{style}.png",
  "32 - (803020) - The Value of Teamwork - RED.tga":              "Painted {name} 803020{style}.png",
  "33 - (256D8D) - The Value of Teamwork - BLU.tga":              "Painted {name} 256D8D{style}.png",
  "34 - (654740) - An Air of Debonair - RED.tga":                 "Painted {name} 654740{style}.png",
  "35 - (28394D) - An Air of Debonair - BLU.tga":                 "Painted {name} 28394D{style}.png",
  "36 - (C36C2D) - Cream Spirit - RED.tga":                       "Painted {name} C36C2D{style}.png",
  "37 - (B88035) - Cream Spirit - BLU.tga":                       "Painted {name} B88035{style}.png",
#  "0.png":                                                        "Painted {name} UNPAINTED{style}.png",
  "0.png":                                                        "RED {name}{style}.png",
  "1.png":                                                        "BLU {name}{style}.png",
  "2.png":                                                        "Painted {name} E6E6E6{style}.png",
  "3.png":                                                        "Painted {name} D8BED8{style}.png",
  "4.png":                                                        "Painted {name} C5AF91{style}.png",
  "5.png":                                                        "Painted {name} 7E7E7E{style}.png",
  "6.png":                                                        "Painted {name} 141414{style}.png",
  "7.png":                                                        "Painted {name} 2D2D24{style}.png",
  "8.png":                                                        "Painted {name} 694D3A{style}.png",
  "9.png":                                                        "Painted {name} 7C6C57{style}.png",
  "10.png":                                                       "Painted {name} A57545{style}.png",
  "11.png":                                                       "Painted {name} CF7336{style}.png",
  "12.png":                                                       "Painted {name} E7B53B{style}.png",
  "13.png":                                                       "Painted {name} F0E68C{style}.png",
  "14.png":                                                       "Painted {name} E9967A{style}.png",
  "15.png":                                                       "Painted {name} FF69B4{style}.png",
  "16.png":                                                       "Painted {name} 7D4071{style}.png",
  "17.png":                                                       "Painted {name} 51384A{style}.png",
  "18.png":                                                       "Painted {name} 2F4F4F{style}.png",
  "19.png":                                                       "Painted {name} 424F3B{style}.png",
  "20.png":                                                       "Painted {name} 808000{style}.png",
  "21.png":                                                       "Painted {name} 729E42{style}.png",
  "22.png":                                                       "Painted {name} 32CD32{style}.png",
  "23.png":                                                       "Painted {name} BCDDB3{style}.png",
  "24.png":                                                       "Painted {name} A89A8C{style}.png",
  "25.png":                                                       "Painted {name} 839FA3{style}.png",
  "26.png":                                                       "Painted {name} 3B1F23{style}.png",
  "27.png":                                                       "Painted {name} 18233D{style}.png",
  "28.png":                                                       "Painted {name} B8383B{style}.png",
  "29.png":                                                       "Painted {name} 5885A2{style}.png",
  "30.png":                                                       "Painted {name} 483838{style}.png",
  "31.png":                                                       "Painted {name} 384248{style}.png",
  "32.png":                                                       "Painted {name} 803020{style}.png",
  "33.png":                                                       "Painted {name} 256D8D{style}.png",
  "34.png":                                                       "Painted {name} 654740{style}.png",
  "35.png":                                                       "Painted {name} 28394D{style}.png",
  "36.png":                                                       "Painted {name} C36C2D{style}.png",
  "37.png":                                                       "Painted {name} B88035{style}.png",
  "38.png":                                                       "Painted {name} E6E6E6 BLU{style}.png",
  "39.png":                                                       "Painted {name} D8BED8 BLU{style}.png",
  "40.png":                                                       "Painted {name} C5AF91 BLU{style}.png",
  "41.png":                                                       "Painted {name} 7E7E7E BLU{style}.png",
  "42.png":                                                       "Painted {name} 141414 BLU{style}.png",
  "43.png":                                                       "Painted {name} 2D2D24 BLU{style}.png",
  "44.png":                                                       "Painted {name} 694D3A BLU{style}.png",
  "45.png":                                                       "Painted {name} 7C6C57 BLU{style}.png",
  "46.png":                                                       "Painted {name} A57545 BLU{style}.png",
  "47.png":                                                       "Painted {name} CF7336 BLU{style}.png",
  "48.png":                                                       "Painted {name} E7B53B BLU{style}.png",
  "49.png":                                                       "Painted {name} F0E68C BLU{style}.png",
  "50.png":                                                       "Painted {name} E9967A BLU{style}.png",
  "51.png":                                                       "Painted {name} FF69B4 BLU{style}.png",
  "52.png":                                                       "Painted {name} 7D4071 BLU{style}.png",
  "53.png":                                                       "Painted {name} 51384A BLU{style}.png",
  "54.png":                                                       "Painted {name} 2F4F4F BLU{style}.png",
  "55.png":                                                       "Painted {name} 424F3B BLU{style}.png",
  "56.png":                                                       "Painted {name} 808000 BLU{style}.png",
  "57.png":                                                       "Painted {name} 729E42 BLU{style}.png",
  "58.png":                                                       "Painted {name} 32CD32 BLU{style}.png",
  "59.png":                                                       "Painted {name} BCDDB3 BLU{style}.png",
}

if __name__ == '__main__':
  if len(sys.argv) > 1:
    folder = sys.argv[1]
  else:
    folder = input('Please provide the folder where the images were saved: ')
  folder = Path(folder)
  print(f'Using folder: {folder}')
  if not folder.exists():
    print(f'ERROR: Folder {folder} does not exist.')
    sys.exit(0)

  images = {}

  # First, scan for matching files in the target directory
  for file in folder.glob('*.*'):
    if file.name in FILENAME_TO_WIKI_PAGE:
      wiki_title = FILENAME_TO_WIKI_PAGE[file.name]
      images[wiki_title] = Image.open(file)

  print(f'Loaded {len(images)} images, computing cropping')

  # Extracted and adapted from imageprocessor.py
  # This will get folded back in if and when we take screenshots internally.
  cropping = (2 ** 31, 2 ** 31, -2 ** 31, -2 ** 31) # Left, Top, Right, Bottom
  for image in images.values():
    # This needs to be dtype=int to prevent an overflow when adding
    # Calculate crop lines by looking for all-white && all-black pixels, i.e. places where the luma is zero.
    # np.any() will return 'True' for any rows which contain nonzero integers (because zero is Falsy).
    # Then, we use nonzero() to get the only indices which are 'True', which are the rows with content.
    # (nonzero returns a tuple for some reason, so we also have to [0] it.)
    blended_arr = array(image, dtype=int)
    horizontal = blended_arr[:, :, 3].any(axis=0).nonzero()[0]
    vertical = blended_arr[:, :, 3].any(axis=1).nonzero()[0]

    cropping = (
      min(cropping[0], horizontal[0]),
      min(cropping[1], vertical[0]),
      max(cropping[2], horizontal[-1]),
      max(cropping[3], vertical[-1])
    )

  for (title, image) in images.items():
    images[title] = image.crop(cropping)

  print('Cropped images with cropping:', cropping)

  cosmetic = input('Cosmetic file name: ')
  style = input('Style name (press enter if no style): ')
  if style:
    style = ' ' + style # We need a leading space in the filename

  description = '''== Summary ==
{{Model info
%s
}}
== Licensing ==
{{ScreenshotTF2}}
[[Category:Painted item images]]
'''

  # Ensure there is enough allocated space to save images as progressive
  ImageFile.MAXBLOCK = image.height * image.width * 8

  try:
    wiki = Wiki('https://wiki.teamfortress.com/w/api.php')
    username = input('Wiki username: ')
    for i in range(3):
      if wiki.login(username):
        break

    for (title, image) in images.items():
      model_info_template = f'| cosmetic = {cosmetic}'
      if style:
        model_info_template += f'\n| style ={style}'
      if title.startswith('Painted'):
        model_info_template += f'\n| paint = {title[15:21]}'
      description_with_template = description % model_info_template

      title = title.format(name=cosmetic, style=style)
      page = Page(wiki, title)

      output_file = Path('temp.png')
      image.convert('RGBA').save(output_file, 'PNG', quality=100, progressive=True, optimize=True)
      with output_file.open('rb') as file:
        print(file, description_with_template)
        r = page.upload(file, description_with_template)
      if r:
        print(f'WARNING: Failed to upload {page.title}: {r}')
  except:
    import traceback
    print('Upload failed!')
    traceback.print_exc()
