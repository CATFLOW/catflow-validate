import os
import glob

import click

from catflow_validate.landuse import LanduseClassDef
from catflow_validate.soil import SoilsDef
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
    lines = report.landuse_summary()
    report.echo_summary(lines)

    if extended:
        click.echo('')
    report.landuse_details(extended=extended)


@click.command()
@click.option('--filename', '-f', default='./l*_soils.def', help='Filename for the SOIL definition file.')
@click.option('--verbose', '-v', default=False, is_flag=True, help="Print out verbose information on errors and warnings.")
@click.option('--extended', '-e', default=False, is_flag=True, help="Print an extended report.")
@click.option('--omit-warnings', '-w', default=False, is_flag=True, help="If set, Warnings are ignored.")
def soil(filename: str, verbose: bool = False, extended: bool = False, omit_warnings: bool = False) -> int:
    if not os.path.exists(filename):
        click.echo("The soil definition file could not be found")
        return 1
    
    # load the file
    s = SoilsDef(filename, encoding='latin1')

    # single word return
    if not verbose:
        if s.valid(warnings_as_errors=not omit_warnings):
            click.secho('valid', fg='green')
        else:
            click.secho('invalid', fg='red')
        return 0

    # use the report
    report = Report(soil=s)
    lines = report.soil_summary()
    report.echo_summary(lines)

    if extended:
        click.echo('')
        report.soil_details(extended=extended)


@click.command()
@click.option('--input-folder', '-i', default='./', help="CATFLOW input data root folder")
@click.option('--landuse-filename', '-L', default='landuseclass.def', help="Name of the landuse-class definition file")
@click.option('--soil-filename', '-S', default="*_soils.def", help="Name of the soil class definition file")
@click.option('--fmt', default='txt', type=click.Choice(['txt', 'md'], case_sensitive=False), help="Output format of the report")
@click.option('--base-href', type=str, help="Base href path for hyperlinks in the report.")
@click.option('--encoding', default="latin1", help="File encoding. Defaults to 'latin1'")
def report(input_folder: str = './', landuse_filename: str = 'landuseclass.def', soil_filename: str = '*_soils.def', fmt: str = 'txt', base_href=None, encoding: str = 'latin1'):
    # get all files recursively
    filenames = glob.glob(os.path.join(input_folder, '**', '*'), recursive=True)

    # filter for the landuse file
    #try:
    filename = next(filter(lambda s: s.endswith(landuse_filename), filenames))
    landuse = LanduseClassDef(filename=filename, basepath=input_folder, recursive=True, encoding=encoding, fmt=fmt, base_href=base_href)
    landuse.validate()
    #except Exception:
    #    print('GOT WRONG')
    #    landuse = None

    # try to find the soil file
    soilnames = glob.glob(os.path.join(input_folder, '**', soil_filename), recursive=True)
    if len(soilnames) > 1:
        click.secho("FOUND MORE THAN ONE SOIL DEFINITION FILE. THIS IS NOT YET SUPPORTED.")
        return
    if len(soilnames) == 0:
        soil = None
    else:
        soil = SoilsDef(filename=soilnames[0], encoding=encoding, fmt=fmt, base_href=base_href)

    # finally build the report
    report = Report(landuse=landuse, soil=soil, fmt=fmt)
    report()


# add the commands
cli.add_command(landuse)
cli.add_command(soil)
cli.add_command(report)


if __name__ == '__main__':
    cli()
