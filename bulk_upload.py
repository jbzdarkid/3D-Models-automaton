from pathlib import Path
from PIL import ImageFile, Image
from shutil import copy as copy_file

from importlib import import_module
Wiki = import_module('TFWiki-scripts.wikitools.wiki').Wiki
Page = import_module('TFWiki-scripts.wikitools.page').Page


# Search in this folder
image_folder = r'C:\Users\localhost\Downloads\tmp\tmp'
# For files named like this
image_filter = '*.png'

# Upload them using this description
description = '''
[[Category:Audio TF2]]
[[Category:Heavy whatever]]
'''

# Use this edit summary if we overwrite an existing file and need to update its description
edit_summary = 'Editing description after automatic upload from https://github.com/jbzdarkid/3D-Models-automaton'



#### Script starts ####
root_folder = Path(image_folder)
if not root_folder.exists():
  print(f'Root folder "{root_folder}" does not exist')
  exit(1)

# Create a new folder to put failed uploads
i = 1
while 1:
  failed_upload_folder = root_folder.parent / (root_folder.name + f' ({i})')
  if not failed_upload_folder.exists():
    break
  i += 1
failed_upload_folder.mkdir(exist_ok = False)

files = list(root_folder.glob(image_filter))
if len(files) == 0:
  print(f'No images found matching pattern "{image_filter}" in "{root_folder}"')
  exit(1)

try:
  wiki = Wiki('https://wiki.teamfortress.com/w/api.php')
except KeyError:
  print('Failed to connect to the wiki, please try again')
  exit(1)

username = input('Wiki username: ')
if not wiki.login(username):
  print('Failed to log in to the wiki')
  exit(1)

success_uploads = 0
failed_uploads = 0
for file in files:
  page = Page(wiki, 'File:' + file.name)
  with file.open('rb') as f:
    r = page.upload(f, description)
  if r:
    print(f'Failed to upload {page.title}: {r}')
    copy_file(file, failed_upload_dir)
    failed_uploads += 1
  else:
    success_uploads += 1

print(f'Successfully uploaded {success_uploads} out of {len(files)} file(s).')
if len(failed_uploads) > 0:
  print(f'Failed to upload {failed_uploads} file(s). They have been copied into "{failed_upload_folder}".')
