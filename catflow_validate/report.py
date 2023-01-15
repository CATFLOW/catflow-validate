import sys
import contextlib

import click

from catflow_validate.landuse import LanduseClassDef

ERROR_COLORS = dict(
    warning='yellow',
    duplicateerror='bright_magenta',
    parseerror='red',
    typeerror='magenta',
    valueerror='magenta'
)

class Report:
    def __init__(self, landuse: LanduseClassDef = None, output_file: str = None):
        self.landuse = landuse
        self.output_file = output_file

    def __run_with_echo(self):
        # header
        click.echo("|--------------------------------------|")
        click.echo("| CATFLOW input file validation report |")
        click.echo("|--------------------------------------|")

        # overview
        self.landuse_summary()

        # details
        self.landuse_details()
    
    def landuse_summary(self):
        """Print single line summary"""
        if self.landuse is None:
            click.echo("Landuse classes: not checked.")
        else:
            msg = [
                click.style('Landuse classes: invalid', fg='red') if self.landuse.n_errors + self.landuse.n_warnings > 0 else click.style('Landuse classes: valid', fg='green'),
                '\t\t', 
                click.style(f'errors: {self.landuse.n_errors}', fg='red') if self.landuse.n_errors > 0 else 'errors: 0',
                '\t ',
                click.style(f'warnings: {self.landuse.n_warnings}', fg='yellow') if self.landuse.n_warnings > 0 else 'warnings: 0'
            ]
            click.echo(''.join(msg))
    
    def landuse_details(self, extended: bool = True):
        # check if there are invalid landuse classes
        n_inval = len([1 for w in self.landuse.errors.values() if len(w) > 0])
        
        # print extended header
        if extended:
            click.echo("Landuse-class definitions")
            click.echo("-------------------------")
            click.echo(f"PATH: {self.landuse.path}")
            click.echo(f"NAME: {self.landuse.basename}")
            click.echo(f"Total classes:    {len(self.landuse.data)}")
            click.secho(f"Invalid classes:  {n_inval}", fg='red' if n_inval > 0 else '')

        # without errors, don't give details about errors
        if n_inval == 0:
            return
        
        # there are errors, so print them
        for cl, warn in self.landuse.errors.items():
            if extended:
                click.echo('')
            n_err = len([1 for _ in warn if _[0].lower() != 'warning'])
            n_wrn = len([1 for _ in warn if _[0].lower() == 'warning'])
            name = self.landuse.data[cl][1]
            if n_err + n_wrn == 0:
                click.secho(f"{'+ ' if extended else ''}ClASS {name}: valid", fg='green')
            else:
                click.echo(click.style(f"{'+ ' if extended else ''}CLASS {name[:20]}: invalid\t\t\t", fg='red') + 
                    click.style(f"errors: {n_err}", fg='red' if n_err > 0 else '') + '\t ' +
                    click.style(f"warnings: {n_wrn}", fg='yellow' if n_wrn > 0 else ''))
            
            # add the actual errors
            if extended:
                for ty, msg in warn:
                    # TODO: the if is there, to supress color. Not yet sure if this is too colorful
                    click.secho(f"  - {msg}", fg= '' if False else ERROR_COLORS.get(ty.lower(), 'blue'))
        
    def run(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                with contextlib.redirect_stderr(sys.stdout):
                    with contextlib.redirect_stdout(f):
                        self.__run_with_echo()
        else:
            self.__run_with_echo()
    
    def __run__(self):
        self.run()

    def __str__(self):
        return self.__run__()