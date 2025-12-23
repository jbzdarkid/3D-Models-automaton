from pathlib import Path
from PIL import ImageFile, Image
from shutil import copy as copy_file

from importlib import import_module
Wiki = import_module('TFWiki-scripts.wikitools.wiki').Wiki
Page = import_module('TFWiki-scripts.wikitools.page').Page

from make_release import check_for_updates

# Checks to see if there's a newer version of this script.
check_for_updates()

# Search in this folder
image_folder = r'C:\Users\localhost\Downloads\tmp\tmp'
# For files named like this
image_filter = '*.png'

# Upload them using this description
description = '''
[[Category:Audio TF2]]
[[Category:Heavy whatever]]
'''

# If we're overwriting an existing file, use this edit summary to update the description
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

username = input('Wiki username: ')
user_agent = input('Custom user agent: ').strip()

wiki = Wiki('https://wiki.teamfortress.com/w/api.php', user_agent, use_cache=False)
if not wiki.login(username):
  print('Failed to log in to the wiki')
  exit(1)

success_uploads = 0
failed_uploads = 0
for file in files:
  page = Page(wiki, 'File:' + file.name)
  with file.open('rb') as f:
    if not page.upload(f, description):
      print(f'Failed to upload {page.title}, adding to {failed_upload_folder}')
      copy_file(file, failed_upload_folder)
      failed_uploads += 1
    else:
      success_uploads += 1
      if not page.get_wiki_text() == description:
        page.edit(description, edit_summary)

print(f'Successfully uploaded {success_uploads} out of {len(files)} file(s).')
if failed_uploads > 0:
  print(f'Failed to upload {failed_uploads} file(s). They have been copied into "{failed_upload_folder}".')
