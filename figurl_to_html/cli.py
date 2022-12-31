import click
from .figurl_to_html import figurl_to_html
from .figurl_doc_to_html import figurl_doc_to_html
from .upload_to_zenodo import upload_to_zenodo as do_upload_to_zenodo

@click.group(help="Isa command-line client")
def cli():
    pass

@click.command(help="Create static HTML folder for a figurl figure")
@click.option('--input', help="The figurl URL for the figure")
@click.option('--output', help="The output folder")
def create_figure(input: str, output: str):
    figurl_to_html(url=input, output_dir=output)

@click.command(help="Create static HTML folder for a figurl document")
@click.option('--input', help='The .md document file')
@click.option('--output', help="The output folder")
def create_doc(input: str, output: str):
    figurl_doc_to_html(doc_fname=input, output_dir=output)

@click.command(help="Upload a figure or doc folder to Zenodo")
@click.option('--folder', help="The local folder to upload")
@click.option('--deposition-id', help="The ID of the Zenodo deposition")
@click.option('--sandbox', is_flag=True, default=False, help='Use sandbox Zenodo site')
def upload_to_zenodo(folder: str, deposition_id: str, sandbox: bool):
    do_upload_to_zenodo(folder=folder, deposition_id=deposition_id, sandbox=sandbox)

cli.add_command(create_figure)
cli.add_command(create_doc)
cli.add_command(upload_to_zenodo)