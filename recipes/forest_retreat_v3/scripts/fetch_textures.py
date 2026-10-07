"""Download the exact CC0 material maps used by the forest retreat."""
import concurrent.futures
import hashlib
import json
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parent.parent
ASSETS = ('bark_brown_02', 'forest_ground_04', 'wood_planks', 'rock_boulder_dry')


def download(asset):
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0'
    response = session.get('https://api.polyhaven.com/files/' + asset, timeout=30)
    response.raise_for_status()
    info = response.json()
    records = []
    for channel in ('Diffuse', 'Rough', 'Displacement'):
        item = info[channel]['2k']['jpg']
        target = OUT / 'assets' / 'textures' / item['url'].rsplit('/', 1)[-1]
        if not target.exists():
            result = session.get(item['url'], timeout=90)
            result.raise_for_status()
            target.write_bytes(result.content)
        data = target.read_bytes()
        if hashlib.md5(data).hexdigest() != item['md5']:
            raise RuntimeError('Asset checksum mismatch: ' + str(target))
        records.append(dict(asset=asset, channel=channel, file=str(target.relative_to(OUT)),
                            url=item['url'], license='CC0-1.0',
                            source='https://polyhaven.com/a/' + asset,
                            sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
    return records


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        records = [record for result in executor.map(download, ASSETS) for record in result]
    (OUT / 'assets' / 'sources.json').write_text(json.dumps(records, indent=2))
    print('VERIFIED_CC0_MAPS', len(records), flush=True)
