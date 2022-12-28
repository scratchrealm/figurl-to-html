import click
from .figurl_to_html import figurl_to_html


@click.command(help="Create static HTML folder for a figurl figure")
@click.argument('url')
@click.option('--output', help="The output folder")
def figurl_to_html_cli(url: str, output: str):
    figurl_to_html(url=url, output_dir=output)