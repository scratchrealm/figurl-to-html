import os
import json
import shutil
import yaml as YAML
from typing import List
from .figurl_to_html import _parse_figurl_url, _get_dependent_uris_recursive, _parse_sha1_uri, _download_view
import kachery_cloud as kcl
import requests

thisdir = os.path.dirname(os.path.realpath(__file__))

def figurl_doc_to_html(*,
    doc_fname: str,
    output_dir: str
):
    if os.path.exists(output_dir):
        print(f'File or folder already exists: {output_dir}')
    os.makedirs(f'{output_dir}/views')
    os.makedirs(f'{output_dir}/sha1')
    os.makedirs(f'{output_dir}/images')

    figurls: List[str] = _get_figurls_from_doc(doc_fname)
    images: List[dict] = _get_images_from_doc(doc_fname)
    view_uris: List[str] = []
    data_uris: List[str] = []
    for url in figurls:
        F = _parse_figurl_url(url)
        if F.v not in view_uris:
            view_uris.append(F.v)
        aa = _get_dependent_uris_recursive(uri=F.d)
        for uu in aa:
            if uu not in data_uris:
                data_uris.append(uu)
    for data_uri in data_uris:
        sha1 = _parse_sha1_uri(data_uri)
        dst_fname = f'{output_dir}/sha1/{sha1}'
        print(f'Writing {dst_fname}')
        kcl.load_file(data_uri, dest=dst_fname)
    for view_uri in view_uris:
        pp = _path_for_view_uri(view_uri)
        view_dir = f'{output_dir}/views/{pp}'
        os.makedirs(view_dir)
        _download_view(view_uri, output_dir=view_dir)
    for image in images:
        image_name: str = image['name']
        image_url: str = image['url']
        if '/' in image_name:
            dd = f'{output_dir}/images/{os.path.dirname(image_name)}'
            if not os.path.exists(dd):
                os.makedirs(dd)
        dest_path = f'{output_dir}/images/{image_name}'
        print(f'Downloading file to: {dest_path}')
        _download_file(image_url, dest=dest_path)
    
    pp = f'{output_dir}/index.md'
    print(f'Writing {pp}')
    shutil.copyfile(doc_fname, pp)

    print('Downloading doc-figurl')
    _download_view('gs://figurl/doc-figurl', output_dir=output_dir)

    print(f'Writing {output_dir}/figurl.json')
    figurl_json = {
        'figurlToHtml': True
    }
    with open(f'{output_dir}/figurl.json', 'w') as f:
        json.dump(figurl_json, f)

def _path_for_view_uri(uri: str):
    return uri.replace('://', '/')

def _get_figurls_from_doc(doc_fname: str):
    ret: List[str] = []
    with open(doc_fname, 'r') as f:
        txt = f.read()
    lines = txt.split('\n')
    for line in lines:
        if line.startswith('https://figurl.org/f'):
            figurl = line.strip()
            if figurl not in ret:
                ret.append(figurl)
    return ret

def _get_images_from_doc(doc_fname: str):
    ret: List[dict] = []
    with open(doc_fname, 'r') as f:
        txt = f.read()
    lines = txt.split('\n')
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith('!['):
            a = _get_comment_parameters(lines[i + 1:])
            if a is None:
                raise Exception(f'Comment parameters required after image at line {i + 1}')
            if 'name' not in a:
                raise Exception(f'Parameter "name" required after image at line {i + 1}')
            name: str = a['name']
            try:
                i1 = line.index('(')
                i2 = line.index(')')
            except:
                raise Exception(f'Unexpected format of image at line {i + 1}')
            url = line[i1 + 1:i2]
            ret.append({'name': name, 'url': url})
    return ret

def _get_comment_parameters(lines: List[str]):
    if (lines[0].strip() != '<!--'):
        return None
    yaml_lines: List[str] = []
    i = 1
    while (i < len(lines)):
        line = lines[i]
        if line.strip() == '-->':
            break
        yaml_lines.append(line)
        i += 1
    yaml = '\n'.join(yaml_lines)
    return YAML.safe_load(yaml)

def _download_file(url: str, *, dest: str):
    # see: https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # specifying chunk size is important, because the default apparently is 1
                # if the source is chunk-encoded, perhaps chunk_size should be None?
                if chunk: 
                    f.write(chunk)