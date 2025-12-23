from os import environ
import requests
import zipfile
from io import BytesIO
import web_browser


VERSION = '3.6'
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


def zip_repository():
  buffer = BytesIO()
  with zipfile.ZipFile(buffer, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for file in Path('.').glob('**/*.py'):
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
  r = requests.get('https://api.github.com/repos/jbzdarkid/3D-Models-automaton/releases/latest', timeout=60)

  latest_release = r.json()['name']
  if latest_release.split('.') == VERSION.split('.'):
    raise ValueError('Please bump the version in make_release.py, then push, then run this script, and finally generate a github release')

  z = zip_repository()
  with open('3D-Models-automation.zip', 'wb') as f:
    f.write(z)

  changelog = f'https://github.com/jbzdarkid/3D-Models-automaton/compare/{latest_release}...master'
  web_browser.open(f'https://github.com/jbzdarkid/3D-Models-automaton/releases/new?tag={VERSION}&title={VERSION}&body=Please summarize the commits from {changelog}')