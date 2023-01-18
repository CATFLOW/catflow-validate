import os
import glob

import click

from catflow_validate.landuse import LanduseClassDef
from catflow_validate.report import Report


@click.group()
def cli():
    pass


@click.command()
@click.option('--filename', '-f', default='./landuseclass.def', help='Filename for the landuse class definition file.')
@click.option('--recursive', '-r', is_flag=True, help="Validate all referenced landuse class parameter files recursively")
@click.option('--verbose', '-v', default=False, is_flag=True, help="Print out verbose information on errors and warnings.")
@click.option('--extended', '-e', default=False, is_flag=True, help="Print an extended report.")
def landuse(filename: str, recursive: bool = False, verbose: bool = False, extended: bool = False) -> int:
    if not os.path.exists(filename):
        click.echo("The landuse class definition file could not be found.")
        return 1
    
    # load the file
    l = LanduseClassDef(filename, recursive=recursive)

    # validate
    valid = l.validate()

    if not verbose:
        if valid:
            click.secho('valid', fg='green')
        else:
            click.secho('invalid', fg='red')
        return 0

    # create the report
    report = Report(landuse=l)
    report.landuse_summary()

    if extended:
        click.echo('')
    report.landuse_details(extended=extended)


@click.command()
@click.option('--input-folder', '-i', default='./', help="CATFLOW input data root folder")
@click.option('--landuse-filename', '-L', default='landuseclass.def', help="Name of the landuse-class definition file")
@click.option('--fmt', default='txt', type=click.Choice(['txt', 'md'], case_sensitive=False), help="Output format of the report")
def report(input_folder: str = './', landuse_filename: str = 'landuseclass.def', fmt: str = 'txt'):
    # get all files recursively
    filenames = glob.glob(os.path.join(input_folder, '**', '*'), recursive=True)

    # filter for the landuse file
    try:
        filename = next(filter(lambda s: s.endswith(landuse_filename), filenames))
        landuse = LanduseClassDef(filename=filename, basepath=input_folder, recursive=True)
        landuse.validate()
    except Exception:
        landuse = None

    # finally build the report
    report = Report(landuse=landuse, fmt=fmt)
    report()


# add the commands
cli.add_command(landuse)
cli.add_command(report)


if __name__ == '__main__':
    cli()
