from os import environ
import requests
import zipfile
from io import BytesIO

from automate import VERSION

def zip_repository():
  buffer = BytesIO()
  with zipfile.ZipFile(buffer, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write('automate.py')
    z.write('automate_paint.py')
    z.write('HLMVModel.py')
    z.write('imageprocessor.py')
    z.write('mem.exe')

    z.write('TFWiki-scripts/wikitools/wiki.py')
    z.write('TFWiki-scripts/wikitools/page.py')

    z.write('3DModels_BlackFirePlusBlackBackground/HLMV - Cubemap Fix.vpk')
    z.write('3DModels_BlackFirePlusBlackBackground/HLMV - Fire Overlay Fix.vpk')
    z.write('3DModels_BlackFirePlusBlackBackground/HLMV - Skybox Background - Black.vpk')

    z.write('README.md')
    z.write('requirements.txt')
  
  return buffer.getvalue()


def check_version_number():
  r = requests.get('https://api.github.com/repos/jbzdarkid/3D-Models-automaton/releases/latest', timeout=60)
  
  latest_release = r.json()['name']
  if latest_release.split('.') == VERSION.split('.'):
    raise ValueError('Please bump the version in automate.py, then push, then run this script, and finally generate a github release')

  
if __name__ == '__main__':
  check_version_number()

  z = zip_repository()
  with open('3D-Models-automation.zip', 'wb') as f:
    f.write(z)
  