from typing import List
import os
import requests
import hashlib


class DepositionFile:
    def __init__(self, f: dict) -> None:
        self.checksum: str = f['checksum']
        self.filename: str = f['filename']
        self.filesize: int = f['filesize']
        self.id: str = f['id']
        self.links = f['links']

def upload_to_zenodo(*, folder: str, deposition_id: str, sandbox: bool):
    env_name = 'ZENODO_SANDBOX_ACCESS_TOKEN' if sandbox else 'ZENODO_ACCESS_TOKEN'
    try:
        access_token = os.environ[env_name]
    except:
        raise Exception(f'Environment variable not set: {env_name}')
    zenodo_base_url = 'https://sandbox.zenodo.org' if sandbox else 'https://zenodo.org'
    deposition = _http_get_json(
        f'{zenodo_base_url}/api/deposit/depositions/{deposition_id}',
        params={'access_token': access_token}
    )
    bucket_url = deposition["links"]["bucket"]
    deposition_files = [DepositionFile(f) for f in deposition['files']]
    filenames_in_deposition = set()
    for f in deposition_files:
        to_delete = False
        if not os.path.exists(f'{folder}/{f.filename}'):
            to_delete = True
        elif not _file_matches(f'{folder}/{f.filename}', filesize=f.filesize, checksum=f.checksum):
            to_delete = True
        if to_delete:
            print(f'Deleting from deposition: {f.filename}')
            _http_delete(
                f'{zenodo_base_url}/api/deposit/depositions/{deposition_id}/files/{f.filename}',
                params={'access_token': access_token}
            )
        else:
            filenames_in_deposition.add(f.filename)
    filenames = _get_all_filenames_in_dir(folder)
    for filename in filenames:
        if filename in filenames_in_deposition:
            print(f'Already in deposition: {filename}')
        else:
            print(f'Uploading {filename}')
            with open(f'{folder}/{filename}', 'rb') as ff:
                _http_put(
                    f'{bucket_url}/{filename}',
                    params={'access_token': access_token},
                    data=ff
                )
    print(f'{zenodo_base_url}/deposit/{deposition_id}')

def _http_get_json(url: str, *, params):
    resp = requests.get(
        url,
        params=params
    )
    if resp.status_code != 200:
        raise Exception(f'Error getting: {url} ({resp.status_code})')
    return resp.json()

def _http_delete(url: str, *, params):
    resp = requests.delete(url, params=params)
    if resp.status_code != 204:
        raise Exception(f'Error deleting: {url} ({resp.status_code})')

def _http_put(url: str, *, params, data):
    resp = requests.put(url, params=params, data=data)
    if resp.status_code != 200:
        raise Exception(f'Error uploading: {url} ({resp.status_code})')

def _file_matches(path: str, *, filesize: int, checksum: str):
    if os.path.getsize(path) != filesize:
        return False
    if os.path.getsize(path) > 1024 * 10:
        print(f'Computing md5 checksum of {path}')
    md5 = _compute_md5_of_file(path)
    if md5 != checksum:
        return False
    return True

def _compute_md5_of_file(path: str):
    with open(path, 'rb') as f:
        data = f.read()
        md5 = hashlib.md5(data).hexdigest()
        return md5

def _get_all_filenames_in_dir(path: str):
    ret: List[str] = []
    for f in os.listdir(path):
        pp = f'{path}/{f}'
        if os.path.isfile(pp):
            ret.append(f)
    for f in os.listdir(path):
        pp = f'{path}/{f}'
        if os.path.isdir(pp):
            for b in _get_all_filenames_in_dir(pp):
                ret.append(f'{f}/{b}')
    return ret