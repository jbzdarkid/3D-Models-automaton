"""
The base automation file. Coordinates between HLMV and image processing.
Recolors and captures pictures of a 3d model.
Load up your model in HLMV, then run this script.
"""

import sys
from numpy import array
from pathlib import Path

from PIL import ImageFile, Image

from automate import check_for_updates

from importlib import import_module
Wiki = import_module('TFWiki-scripts.wikitools.wiki').Wiki
Page = import_module('TFWiki-scripts.wikitools.page').Page

FILENAME_TO_WIKI_PAGE = {
  "2.tga":                                          "Painted {name} E6E6E6{style}.png",
  "3.tga":                                          "Painted {name} D8BED8{style}.png",
  "4.tga":                                          "Painted {name} C5AF91{style}.png",
  "5.tga":                                          "Painted {name} 7E7E7E{style}.png",
  "6.tga":                                          "Painted {name} 141414{style}.png",
  "7.tga":                                          "Painted {name} 2D2D24{style}.png",
  "8.tga":                                          "Painted {name} 694D3A{style}.png",
  "9.tga":                                          "Painted {name} 7C6C57{style}.png",
  "10.tga":                                         "Painted {name} A57545{style}.png",
  "11.tga":                                         "Painted {name} CF7336{style}.png",
  "12.tga":                                         "Painted {name} E7B53B{style}.png",
  "13.tga":                                         "Painted {name} F0E68C{style}.png",
  "14.tga":                                         "Painted {name} E9967A{style}.png",
  "15.tga":                                         "Painted {name} FF69B4{style}.png",
  "16.tga":                                         "Painted {name} 7D4071{style}.png",
  "17.tga":                                         "Painted {name} 51384A{style}.png",
  "18.tga":                                         "Painted {name} 2F4F4F{style}.png",
  "19.tga":                                         "Painted {name} 424F3B{style}.png",
  "20.tga":                                         "Painted {name} 808000{style}.png",
  "21.tga":                                         "Painted {name} 729E42{style}.png",
  "22.tga":                                         "Painted {name} 32CD32{style}.png",
  "23.tga":                                         "Painted {name} BCDDB3{style}.png",
  "24.tga":                                         "Painted {name} A89A8C{style}.png",
  "25.tga":                                         "Painted {name} 839FA3{style}.png",
  "26.tga":                                         "Painted {name} 3B1F23{style}.png",
  "27.tga":                                         "Painted {name} 18233D{style}.png",
  "28.tga":                                         "Painted {name} B8383B{style}.png",
  "29.tga":                                         "Painted {name} 5885A2{style}.png",
  "30.tga":                                         "Painted {name} 483838{style}.png",
  "31.tga":                                         "Painted {name} 384248{style}.png",
  "32.tga":                                         "Painted {name} 803020{style}.png",
  "33.tga":                                         "Painted {name} 256D8D{style}.png",
  "34.tga":                                         "Painted {name} 654740{style}.png",
  "35.tga":                                         "Painted {name} 28394D{style}.png",
  "36.tga":                                         "Painted {name} C36C2D{style}.png",
  "37.tga":                                         "Painted {name} B88035{style}.png",
  "38.tga":                                         "Painted {name} E6E6E6{style} BLU.png",
  "39.tga":                                         "Painted {name} D8BED8{style} BLU.png",
  "40.tga":                                         "Painted {name} C5AF91{style} BLU.png",
  "41.tga":                                         "Painted {name} 7E7E7E{style} BLU.png",
  "42.tga":                                         "Painted {name} 141414{style} BLU.png",
  "43.tga":                                         "Painted {name} 2D2D24{style} BLU.png",
  "44.tga":                                         "Painted {name} 694D3A{style} BLU.png",
  "45.tga":                                         "Painted {name} 7C6C57{style} BLU.png",
  "46.tga":                                         "Painted {name} A57545{style} BLU.png",
  "47.tga":                                         "Painted {name} CF7336{style} BLU.png",
  "48.tga":                                         "Painted {name} E7B53B{style} BLU.png",
  "49.tga":                                         "Painted {name} F0E68C{style} BLU.png",
  "50.tga":                                         "Painted {name} E9967A{style} BLU.png",
  "51.tga":                                         "Painted {name} FF69B4{style} BLU.png",
  "52.tga":                                         "Painted {name} 7D4071{style} BLU.png",
  "53.tga":                                         "Painted {name} 51384A{style} BLU.png",
  "54.tga":                                         "Painted {name} 2F4F4F{style} BLU.png",
  "55.tga":                                         "Painted {name} 424F3B{style} BLU.png",
  "56.tga":                                         "Painted {name} 808000{style} BLU.png",
  "57.tga":                                         "Painted {name} 729E42{style} BLU.png",
  "58.tga":                                         "Painted {name} 32CD32{style} BLU.png",
  "59.tga":                                         "Painted {name} BCDDB3{style} BLU.png",
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
  "38.png":                                                       "Painted {name} E6E6E6{style} BLU.png",
  "39.png":                                                       "Painted {name} D8BED8{style} BLU.png",
  "40.png":                                                       "Painted {name} C5AF91{style} BLU.png",
  "41.png":                                                       "Painted {name} 7E7E7E{style} BLU.png",
  "42.png":                                                       "Painted {name} 141414{style} BLU.png",
  "43.png":                                                       "Painted {name} 2D2D24{style} BLU.png",
  "44.png":                                                       "Painted {name} 694D3A{style} BLU.png",
  "45.png":                                                       "Painted {name} 7C6C57{style} BLU.png",
  "46.png":                                                       "Painted {name} A57545{style} BLU.png",
  "47.png":                                                       "Painted {name} CF7336{style} BLU.png",
  "48.png":                                                       "Painted {name} E7B53B{style} BLU.png",
  "49.png":                                                       "Painted {name} F0E68C{style} BLU.png",
  "50.png":                                                       "Painted {name} E9967A{style} BLU.png",
  "51.png":                                                       "Painted {name} FF69B4{style} BLU.png",
  "52.png":                                                       "Painted {name} 7D4071{style} BLU.png",
  "53.png":                                                       "Painted {name} 51384A{style} BLU.png",
  "54.png":                                                       "Painted {name} 2F4F4F{style} BLU.png",
  "55.png":                                                       "Painted {name} 424F3B{style} BLU.png",
  "56.png":                                                       "Painted {name} 808000{style} BLU.png",
  "57.png":                                                       "Painted {name} 729E42{style} BLU.png",
  "58.png":                                                       "Painted {name} 32CD32{style} BLU.png",
  "59.png":                                                       "Painted {name} BCDDB3{style} BLU.png",
}

HEX_TO_PAINT_NAME = {
  "E6E6E6": "An Extraordinary Abundance of Tinge",
  "D8BED8": "Color No 216-190-216",
  "C5AF91": "Peculiarly Drab Tincture",
  "7E7E7E": "Aged Moustache Grey",
  "141414": "A Distinctive Lack of Hue",
  "2D2D24": "After Eight",
  "694D3A": "Radigan Conagher Brown",
  "7C6C57": "Ye Olde Rustic Colour",
  "A57545": "Muskelmannbraun",
  "CF7336": "Mann Co Orange",
  "E7B53B": "Australium Gold",
  "F0E68C": "The Color of a Gentlemann Business Pants",
  "E9967A": "Dark Salmon Injustice",
  "FF69B4": "Pink as Hell",
  "7D4071": "A Deep Commitment to Purple",
  "51384A": "Noble Hatter's Violet",
  "2F4F4F": "A Color Similar to Slate",
  "424F3B": "Zepheniah Greed",
  "808000": "Drably Olive",
  "729E42": "Indubitably Green",
  "32CD32": "The Bitter Taste of Defeat and Lime",
  "BCDDB3": "A Mann's Mint",
  "A89A8C": "Waterlogged Lab Coat",
  "839FA3": "Waterlogged Lab Coat",
  "3B1F23": "Balaclavas Are Forever",
  "18233D": "Balaclavas Are Forever",
  "B8383B": "Team Spirit",
  "5885A2": "Team Spirit",
  "483838": "Operator's Overalls",
  "384248": "Operator's Overalls",
  "803020": "The Value of Teamwork",
  "256D8D": "The Value of Teamwork",
  "654740": "An Air of Debonair",
  "28394D": "An Air of Debonair",
  "C36C2D": "Cream Spirit",
  "B88035": "Cream Spirit",
}

if __name__ == '__main__':
  check_for_updates()

  if len(sys.argv) > 1:
    folder = sys.argv[1]
  else:
    folder = input('Please provide the folder where the images were saved: ').strip('"')
  folder = Path(folder)
  print(f'Using folder: {folder}')
  if not folder.exists():
    print(f'ERROR: Folder {folder} does not exist.')
    sys.exit(0)

  # We use slightly different naming styles for unpainted images (i.e. default images) with and without team colors.
  team_color = input('Is the cosmetic team colored [y/n]?')
  if team_color.lower() in ['y', 'yes']:
    FILENAME_TO_WIKI_PAGE["0 - Unpainted RED.tga"] = "RED {name}{style}.png"
    FILENAME_TO_WIKI_PAGE["1 - Unpainted BLU.tga"] = "BLU {name}{style}.png"
    FILENAME_TO_WIKI_PAGE["0.png"] = "RED {name}{style}.png"
    FILENAME_TO_WIKI_PAGE["1.png"] = "BLU {name}{style}.png"
  elif team_color.lower() in ['n', 'no']:
    FILENAME_TO_WIKI_PAGE["0 - Unpainted RED.tga"] = "Painted {name} UNPAINTED{style}.png"
    FILENAME_TO_WIKI_PAGE["0.png"] = "Painted {name} UNPAINTED{style}.png"
  else:
    print(f'ERROR: Could not parse response: "{team_color}"')
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
'''

  # Ensure there is enough allocated space to save images as progressive
  ImageFile.MAXBLOCK = image.height * image.width * 8

  try:
    username = input('Wiki username: ')
    user_agent = input('Custom user agent: ').strip()
    wiki = Wiki('https://wiki.teamfortress.com/w/api.php', user_agent, use_cache=False)
    for i in range(3):
      if wiki.login(username):
        break

    for (title, image) in images.items():
      model_info_template = f'| cosmetic = {cosmetic}'
      if style:
        model_info_template += f'\n| style ={style}'
      if title.startswith('Painted'):
        hex_id = title[15:21]
        paint_name = HEX_TO_PAINT_NAME.get(hex_id, None)
        if paint_name:
          model_info_template += f'\n| paint = {paint_name}'

      description_with_template = description % model_info_template

      if title.startswith('Painted'):
        description_with_template += '[[Category:Painted item images]]\n'
      else:
        description_with_template += '[[Category:Item skin images]]\n'

      title = title.format(name=cosmetic, style=style)
      page = Page(wiki, 'File:' + title)

      output_file = Path('temp.png')
      image.convert('RGBA').save(output_file, 'PNG', quality=100, progressive=True, optimize=True)
      with output_file.open('rb') as file:
        print(file, description_with_template)
        r = page.upload(file, description_with_template)
        if r:
          print(f'WARNING: Failed to upload {page.title}: {r}')
        else:
          page.edit(description_with_template, 'Adding [[Template:Model info]] alongside new image')
  except:
    import traceback
    print('Upload failed!')
    traceback.print_exc()
