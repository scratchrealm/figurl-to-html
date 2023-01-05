from typing import Union
import click
from .figurl_to_html import figurl_to_html
from .figurl_doc_to_html import figurl_doc_to_html
from .upload_to_zenodo import upload_to_zenodo as do_upload_to_zenodo
from .view_doc import view_doc as do_view_doc
from .generate_doc_bibliography import generate_doc_bibliography as do_generate_doc_bibliography


@click.group(help="Isa command-line client")
def cli():
    pass

@click.command(help="Create static HTML folder for a figurl figure")
@click.option('--input', required=True, help="The figurl URL for the figure")
@click.option('--output', required=True, help="The output folder")
def create_figure(input: str, output: str):
    figurl_to_html(url=input, output_dir=output)

@click.command(help="Create static HTML folder for a figurl document")
@click.option('--input', required=True, help='The .md document file')
@click.option('--output', required=True, help="The output folder")
def create_doc(input: str, output: str):
    figurl_doc_to_html(doc_fname=input, output_dir=output)

@click.command(help="Upload a figure or doc folder to Zenodo")
@click.option('--folder', required=True, help="The local folder to upload")
@click.option('--deposition-id', required=True, help="The ID of the Zenodo deposition")
@click.option('--sandbox', is_flag=True, default=False, help='Use sandbox Zenodo site')
def upload_to_zenodo(folder: str, deposition_id: str, sandbox: bool):
    do_upload_to_zenodo(folder=folder, deposition_id=deposition_id, sandbox=sandbox)

@click.command(help="View a figurl markdown document locally")
@click.argument('file')
@click.option('--port', default=8000, help="The local port to use")
@click.option('--allow-origin', default='https://doc.figurl.org', help="The URL of doc.figurl.org to allow")
def view_doc(file: str, port: int, allow_origin: str):
    do_view_doc(file_path=file, port=port, allow_origin=allow_origin)

@click.command(help="Generate doc bibliography")
@click.argument('file')
@click.option('--bibliography', required=True, help="Path to .bib file")
@click.option('--csl', help="Path to csl file")
def generate_doc_bibliography(file: str, bibliography: str, csl: Union[str, None]):
    do_generate_doc_bibliography(file_path=file, bibliography_path=bibliography, csl_path=csl)

cli.add_command(create_figure)
cli.add_command(create_doc)
cli.add_command(upload_to_zenodo)
cli.add_command(view_doc)
cli.add_command(generate_doc_bibliography)