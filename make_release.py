"""
Packages the repo, and uploads it to github to make a new release.
Also holds the source-of-truth VERSION so that other files can check if we're on the latest version.
"""
from io import BytesIO
from os import environ
from pathlib import Path
from time import sleep
import zipfile
import requests


VERSION = '3.8'


def make_request(method, path, *args, **kwargs):
  """
  Open a network request using requests.
  Defaults to calling the github APIs for this repo, but can be overridden.
  Sources the GITHUB_TOKEN from the environ (for CI) but can also run without.
  """
  if path.startswith('https:'):
    url = path
  else:
    url = f'https://api.github.com/repos/jbzdarkid/3D-Models-automaton/{path}'
  if 'headers' not in kwargs:
    kwargs['headers'] = {}
  kwargs['headers']['Accept'] = 'application/vnd.github.v3+json'
  if 'GITHUB_TOKEN' in environ:
    kwargs['headers']['Authorization'] = 'Bearer ' + environ['GITHUB_TOKEN']
  r = requests.request(method, url, *args, timeout=10, **kwargs)
  if not r.ok:
    print(r.status_code, r.text)
  r.raise_for_status()
  return r.json()

def check_for_updates():
  """
  Check to see if this copy of the script is the latest, by checking the public github releases.
  """
  try:
    latest_release = make_request('GET', 'releases/latest')['name']
    if latest_release.split('.') > VERSION.split('.'):
      print('A new version of the automation scripts are available.')
      print(f'You are running {VERSION} but the latest release is {latest_release}.')
      print('Please download the latest version from https://github.com/jbzdarkid/3D-Models-automaton/releases/latest')
      sleep(1)

  except:
    pass

def is_relative_to(file, path):
  """
  Small helper to wrap the (not very helpful) python pathlib behavior
  """
  try:
    file.relative_to(path)
    return True
  except:
    return False


def zip_repository():
  """
  Assemble a zip file with all the important files in this repo, for publishing.
  """
  buffer = BytesIO()
  with zipfile.ZipFile(buffer, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for file in Path('.').glob('**/*.py'):
      if is_relative_to(file, 'venv'):
        continue # Don't include my virtual environment
      if is_relative_to(file, 'mem'):
        continue # Don't include any of the source code for mem.exe
      if is_relative_to(file, 'TFWiki-scripts/reports'):
        continue # We only need TFWiki-scripts for the wikitools

      print(f'- {file}')
      z.write(file)

    z.write('mem.exe')
    z.write('README.md')

    z.write('requirements.txt')
    z.write('TFWiki-scripts/requirements.txt')

    z.write('3DModels_BlackFirePlusBlackBackground/HLMV - Cubemap Fix.vpk')
    z.write('3DModels_BlackFirePlusBlackBackground/HLMV - Fire Overlay Fix.vpk')
    z.write('3DModels_BlackFirePlusBlackBackground/HLMV - Skybox Background - Black.vpk')

    z.write('MVScripts/AUTO-PaintedVariants-Part1.mvscript')
    z.write('MVScripts/AUTO-PaintedVariants-Part2.mvscript')

  return buffer.getvalue()


if __name__ == '__main__':
  print('Fetching latest release')
  current_release = make_request('GET', 'releases/latest')['name']
  if current_release.split('.') <= VERSION.split('.'):
    raise ValueError(f'The version in make_release.py {VERSION} is not greater than the latest released version {current_release}')

  print('Zipping repository')
  zip_buffer = zip_repository()
  # with open('3D-Models-automation.zip', 'wb') as f:
  #   f.write(zip_buffer)
  # print('Done')

  body = f'Please summarize the commits from https://github.com/jbzdarkid/3D-Models-automaton/compare/v{current_release}...master'
  j = make_request('POST', 'releases', json={
    'tag_name': 'v' + VERSION,
    'name': VERSION,
    'body': body,
    'draft': True
  })

  release_id = j['id']
  upload_url = f'https://uploads.github.com/repos/jbzdarkid/3D-Models-automaton/releases/{release_id}/assets?name=3D-models-automation.zip'
  make_request('POST', upload_url, data=zip_buffer, headers={'Content-Type': 'application/binary'})
