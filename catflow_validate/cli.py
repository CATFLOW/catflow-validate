import os

import click

from catflow_validate.landuse import LanduseClassDef


@click.group()
def cli():
    pass


@click.command()
@click.option('--filename', '-f', default='./landuseclass.def', help='Filename for the landuse class definition file.')
@click.option('--recursive', '-r', help="Validate all referenced landuse class parameter files recursively")
def landuse(filename: str, recursive: bool = False) -> int:
    if not os.path.exists(filename):
        click.echo("The landuse class definition file could not be found.")
        return 1
    
    # load the file
    l = LanduseClassDef(filename)

    # validate
    valid = l.validate()

    if valid:
        click.echo(f"Landuse class definion is valid")
        return 0
    else:
        click.echo(l.errors)
        return 1


# add the commands
cli.add_command(landuse)


if __name__ == '__main__':
    cli()
