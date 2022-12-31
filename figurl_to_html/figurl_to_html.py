import os
import shutil
import requests
import json
import time
from typing import List
from dataclasses import dataclass
import kachery_cloud as kcl

thisdir = os.path.dirname(os.path.realpath(__file__))

def figurl_to_html(*,
    url: str,
    output_dir: str
):
    F = _parse_figurl_url(url)
    if not F.d:
        raise Exception('No d parameter')
    if not F.v:
        raise Exception('No v parameter')
    if os.path.exists(output_dir):
        print(f'File or folder already exists: {output_dir}')
    os.makedirs(f'{output_dir}/sha1')
    os.makedirs(f'{output_dir}/view')

    _download_view(F.v, output_dir=output_dir + '/view')

    config_fname = f'{output_dir}/figurl.json'
    print(f'Writing {config_fname}')
    with open(config_fname, 'w') as f:
        json.dump({
            'd': F.d,
            'v': F.v,
            'label': F.label,
            'zone': F.zone,
            'url': url,
            'timestampCreated': time.time()
        }, f, indent=4)

    dependent_uris = _get_dependent_uris_recursive(uri=F.d)
    for uri in dependent_uris:
        if uri.startswith('sha1://'):
            sha1 = _parse_sha1_uri(uri)
            dst_fname = f'{output_dir}/sha1/{sha1}'
            print(f'Writing {dst_fname}')
            kcl.load_file(uri, dest=dst_fname)
        else:
            print(f'Depends on: {uri}')
    
    dstpath = f'{output_dir}/index.html'
    print(f'Writing {dstpath}')
    shutil.copyfile(f'{thisdir}/templates/figurl_to_html_index.html', dstpath)

def _get_dependent_uris_recursive(*, uri: str):
    ret: List[str] = []
    ret.append(uri)
    a = kcl.load_text(uri)
    try:
        b = json.loads(a)
    except:
        b = None
    if b is not None:
        x = _get_dependent_uris_from_obj_recursive(obj=b)
        for c in x:
            if not c in ret:
                ret.append(c)
    return ret

def _get_dependent_uris_from_obj_recursive(*, obj):
    ret: List[str] = []
    if isinstance(obj, str):
        if obj.startswith('sha1://') or obj.startswith('zenodo://') or obj.startswith('zenodo-sandbox://'):
            if not obj in ret:
                aa = _get_dependent_uris_recursive(uri=obj)
                for bb in aa:
                    if not bb in ret:
                        ret.append(bb)
    elif isinstance(obj, list) or isinstance(obj, tuple):
        for c in obj:
            a = _get_dependent_uris_from_obj_recursive(obj=c)
            for b in a:
                if not b in ret:
                    ret.append(b)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            a = _get_dependent_uris_from_obj_recursive(obj=v)
            for b in a:
                if not b in ret:
                    ret.append(b)
    else:
        pass
    return ret

@dataclass
class FigurlUrl:
    d: str
    v: str
    s: str
    label: str
    zone: str

def _parse_figurl_url(uri: str):
    ind = uri.index('?')
    q = uri[ind + 1:]
    a = q.split('&')
    query = {}
    for b in a:
        x = b.split('=')
        if len(x) == 2:
            query[x[0]] = x[1]
    return FigurlUrl(
        d=query.get('d', ''),
        v=query.get('v', ''),
        s=query.get('s', ''),
        label=query.get('label', ''),
        zone=query.get('zone', '')
    )

def _parse_sha1_uri(uri: str):
    a = uri.split('?')[0].split('/')
    sha1 = a[2]
    return sha1

def _http_get(url: str):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        raise Exception(f'Error getting {url}: {r.status_code}')

def _download_view(view_uri: str, *, output_dir: str):
    if view_uri.startswith('sha1://') or view_uri.startswith('zenodo://') or view_uri.startswith('zenodo-sandbox://'):
        view_fname = f'{output_dir}/index.html'
        print(f'Writing {view_fname}')
        kcl.load_file(view_uri, dest=view_fname)
    elif view_uri.startswith('gs://'):
        p = view_uri[len("gs://"):]
        url = f'https://storage.googleapis.com/{p}'
        index_html = _http_get(f'{url}/index.html')
        _write_file(f'{output_dir}/index.html', index_html)
        manifest_json = _http_get(f'{url}/manifest.json')
        _write_file(f'{output_dir}/manifest.json', manifest_json)
        asset_manifest_json = _http_get(f'{url}/asset-manifest.json')
        _write_file(f'{output_dir}/asset-manifest.json', asset_manifest_json)
        asset_manifest = json.loads(asset_manifest_json)
        for k, f in asset_manifest['files'].items():
            if f.startswith('/'):
                f = f[1:]
            url_src = f'{url}/{f}'
            pp_dst = f'{output_dir}/{f}'
            os.makedirs(os.path.dirname(pp_dst), exist_ok=True)
            txt = _http_get(url_src)
            _write_file(pp_dst, txt)

def _write_file(fname: str, content: str):
    print(f'Writing {fname}')
    with open(fname, 'w') as f:
        f.write(content)