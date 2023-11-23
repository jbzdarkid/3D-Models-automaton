from os import environ
import requests
import zipfile
from io import BytesIO

def zip_repository():
  buffer = BytesIO()
  with zipfile.ZipFile(buffer, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write('automate.py')
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

  
if __name__ == '__main__':
  z = zip_repository()
  with open('3D-Models-automaton.zip', 'wb') as f:
    f.write(z)
  