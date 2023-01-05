import os
from typing import List, Union
import kachery_cloud as kcl


def generate_doc_bibliography(*, file_path: str, bibliography_path: str, csl_path: Union[str, None]):
    with open(file_path, 'r') as f:
        txt = f.read()
    lines = txt.split('\n')
    bib_comment_text = '<!--bibliography-->' 
    if bib_comment_text in lines:
        ind = lines.index(bib_comment_text)
        body_lines = lines[:ind]
    else:
        print(f'WARNING: No "{bib_comment_text}" line found in file.')
        return

    bib_keys: List[str] = []
    for line in body_lines:
        a = _get_bib_keys(line)
        for b in a:
            if b not in bib_keys:
                bib_keys.append(b)
    
    bib_lines: List[str] = []
    for i, bib_key in enumerate(bib_keys):
        print(f'Generating bibliography item for {bib_key}')
        txt = _get_bib_item_text(key=bib_key, bibliography_path=bibliography_path, csl_path=csl_path)
        if txt:
            bib_lines.append(
                f'\\[@{bib_key}\\] {txt}'
            )
            if i < len(bib_keys) - 1:
                bib_lines.append('')
        else:
            print(f'WARNING: Unable to find {bib_key}')

    new_lines = body_lines + ['<!--bibliography-->', ''] + bib_lines
    new_txt = '\n'.join(new_lines)
    with open(file_path, 'w') as f:
        f.write(new_txt)

def _get_bib_keys(line: str):
    keys: List[str] = []
    def process_separated_part(x: str):
        if x.startswith('@'):
            keys.append(x[1:])
        return x
    def process_bracketed_part(x: str):
        _handleSeparatedParts(x, [',', ';'], process_separated_part)
        return x
    _handleBracketedParts(line, process_bracketed_part)
    return keys

def _handleBracketedParts(a: str, handler: callable) -> str:
    parts1: List[str] = a.split('[')
    parts2: List[str] = []
    for i, part1 in enumerate(parts1):
        if i > 0:
            jj = part1.find(']')
            if jj > 0:
                parts2.append(handler(part1[:jj]) + part1[jj:])
            else:
                parts2.append(part1)
        else:
            parts2.append(part1)
    return '['.join(parts2)

def _handleSeparatedParts(a: str, delimiters: List[str], handler: callable) -> str:
    for d in delimiters:
        b = a.split(d)
        if len(b) > 1:
            return d.join([_handleSeparatedParts(x, delimiters, handler) for x in b])
    if a.startswith(' '):
        return ' ' + handler(a[1:])
    else:
        return handler(a)

def _get_bib_item_text(*, key: str, bibliography_path: str, csl_path: Union[str, None]):
    # should we call this a hack? yes.
    with kcl.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/input.md', 'w') as f:
            f.write(f'''
{key}: [@{key}]

<!---->

''')
        opts = [
            f'--bibliography {bibliography_path}'
        ]
        if csl_path is not None:
            opts.append(
                f'--csl {csl_path}'
            )
        os.system(f'pandoc -t markdown_strict {" ".join(opts)} -o {tmpdir}/output.md {tmpdir}/input.md')

        with open(f'{tmpdir}/output.md', 'r') as f:
            a = f.read()
        lines = a.split('\n')
        ind = lines.index('<!---->')
        txt = '\n'.join(lines[ind + 1:]).strip()
        prefixes_to_remove = '\\[1\\] '
        for p in prefixes_to_remove:
            if txt.startswith(p):
                txt = txt[len(p):]
        return txt