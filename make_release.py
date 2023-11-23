from os import environ
import requests
import zipfile
from io import BytesIO

def make_request(method, path, *args, **kwargs):
  url = f'https://api.github.com/repos/{environ["GITHUB_REPOSITORY"]}/{path}'
  kwargs['headers'] = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'Bearer ' + environ['GITHUB_TOKEN'],
  }
  r = requests.request(method, url, *args, **kwargs)
  if not r.ok:
    print(r.status_code, r.text)
  r.raise_for_status()
  return r.json()


def zip_repository():
  buffer = BytesIO()
  with zipfile.ZipFile(buffer, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write('automate.py')
    z.write('HLMVModel.py')
    z.write('imageprocessor.py')

    z.write('TFWiki-scripts/wikitools/wiki.py')
    z.write('TFWiki-scripts/wikitools/page.py')

    z.write('3DModels_BlackFirePlusBlackBackground/materials/effects/tiledfire/fireLayeredSlowTiled512.vtf')
    z.write('3DModels_BlackFirePlusBlackBackground/materials/skybox/sky_wasteland02bk.vtf')
    z.write('mem.exe')

    z.write('requirements.txt')
    z.write('TFWiki-scripts/requirements.txt')
  
  return buffer.getvalue()


def make_release():
  releases = make_request('GET', 'releases')
  latest_tag = releases[0]['tag_name']
  
  tag_parts = latest_tag.split('.')
  tag_parts[-1] = int(tag_parts[-1]) + 1
  new_tag = '.'.join(tag_parts)
  return make_request('POST', 'releases', json={'tag_name': new_tag})
  
  
def upload_release_asset(release, asset):
  upload_url = latest_release['upload_url'].replace('{?name,label}', '') # idk what this suffix is
  
  r = make_request(upload_url, files=asset)
  print(r.status_code, r.text)
  
  
if __name__ == '__main__':
  z = zip_repository()
  with open('out.zip', 'wb') as f:
    f.write(z)
  