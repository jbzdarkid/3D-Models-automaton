from io import BytesIO
from os import environ
from pathlib import Path
import requests
import webbrowser
import zipfile


VERSION = '3.6'


def make_request(method, path, *args, **kwargs):
  url = f'https://api.github.com/repos/jbzdarkid/3D-Models-automaton/{path}'
  kwargs['headers'] = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'Bearer ' + environ.get('GITHUB_TOKEN', None),
  }
  r = requests.request(method, url, *args, **kwargs)
  if not r.ok:
    print(r.status_code, r.text)
  r.raise_for_status()
  return r.json()

def check_for_updates():
  try:
    latest_release = make_request('GET', 'releases/latest')['name']
    if latest_release.split('.') > VERSION.split('.'):
      print(f'A new version of the automation scripts are available. You are running {VERSION} but the latest release is {latest_release}.')
      print('Please download the latest version from https://github.com/jbzdarkid/3D-Models-automaton/releases/latest')
      sleep(10)

  except:
    pass

def is_relative_to(file, path):
  try:
    file.relative_to(path)
    return True
  except:
    return False


def zip_repository():
  buffer = BytesIO()
  with zipfile.ZipFile(buffer, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for file in Path('.').glob('**/*.py'):
      if is_relative_to(file, 'venv'):
        continue # Don't include my virtual environment
      elif is_relative_to(file, 'mem'):
        continue # Don't include any of the source code for mem.exe
      elif is_relative_to(file, 'TFWiki-scripts/reports'):
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


  return buffer.getvalue()


if __name__ == '__main__':
  print('Fetching latest release')
  latest_release = make_request('GET', 'releases/latest')['name']
  if latest_release.split('.') == VERSION.split('.'):
    raise ValueError('Please bump the version in make_release.py, then push, then run this script, and finally generate a github release')

  print('Zipping repository')
  z = zip_repository()
  with open('3D-Models-automation.zip', 'wb') as f:
    f.write(z)
  print('Done')

  body = f'Please summarize the commits from https://github.com/jbzdarkid/3D-Models-automaton/compare/v{latest_release}...master'
  j = make_request('POST', 'releases', json={
    'tag_name': VERSION,
    'name': 'v' + VERSION,
    'body': body,
    'draft': True
  })
  release_id = j['id']

  make_request('POST', f'releases/{release_id}/assets', data=z, headers={'Content-Type': 'application/binary'})
