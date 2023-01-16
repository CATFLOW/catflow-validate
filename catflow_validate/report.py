import sys
import contextlib

import click
from click import style, echo

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
        echo("|--------------------------------------|")
        echo("| CATFLOW input file validation report |")
        echo("|--------------------------------------|")

        # overview
        self.landuse_summary()

        # details
        self.landuse_details()
    
    def landuse_summary(self):
        """Print single line summary"""
        if self.landuse is None:
            echo("Landuse classes: not checked.")
        else:
            msg = [
                style('Landuse classes: invalid', fg='red') if self.landuse.n_errors + self.landuse.n_warnings > 0 else style('Landuse classes: valid', fg='green'),
                '\t\t', 
                style(f'errors: {self.landuse.n_errors}', fg='red') if self.landuse.n_errors > 0 else 'errors: 0',
                '\t ',
                style(f'warnings: {self.landuse.n_warnings}', fg='yellow') if self.landuse.n_warnings > 0 else 'warnings: 0'
            ]
            echo(''.join(msg))

            # append information about all landuse parameter files
            for cl, lp in self.landuse.parameters.items():
                valid = lp.n_errors + lp.n_warnings == 0
                msg = f"CLASS {self.landuse.data[cl][1][:30]}:\t{'valid' if valid else 'invalid'}"
                echo(
                    style(msg, fg='green' if valid else 'red') + '\t\t' +
                    style(f"errors: {lp.n_errors}", fg='red' if lp.n_errors > 0 else '') + '\t ' +
                    style(f"warnings: {lp.n_warnings}", fg='yellow' if lp.n_warnings > 0 else '')
                )
    
    def landuse_details(self, extended: bool = True):
        # check if there are invalid landuse classes
        n_inval = len([1 for w in self.landuse.errors.values() if len(w) > 0])
        
        # print extended header
        if extended:
            echo("Landuse-class definitions")
            echo("-------------------------")
            echo(f"PATH: {self.landuse.path}")
            echo(f"NAME: {self.landuse.basename}")
            echo(f"Total classes:    {len(self.landuse.data)}")
            click.secho(f"Invalid classes:  {n_inval}", fg='red' if n_inval > 0 else '')

        # without errors, don't give details about errors
        if n_inval == 0:
            return
        
        # there are errors, so print them
        for cl, warn in self.landuse.errors.items():
            # get the params if any
            par = self.landuse.parameters.get(cl)
            
            # start printing
            if extended:
                echo('')
            n_err = len([1 for _ in warn if _[0].lower() != 'warning']) + 0 if par is None else par.n_errors 
            n_wrn = len([1 for _ in warn if _[0].lower() == 'warning']) + 0 if par is None else par.n_warnings
            name = self.landuse.data[cl][1]
            ID = self.landuse.data[cl][0]
            if n_err + n_wrn == 0:
                click.secho(f"{'+ ' if extended else ''}ClASS {ID} {name}: valid", fg='green')
            else:
                echo(style(f"{'+ ' if extended else ''}CLASS {ID} {name[:20]}: invalid\t\t\t", fg='red') + 
                    style(f"errors: {n_err}", fg='red' if n_err > 0 else '') + '\t ' +
                    style(f"warnings: {n_wrn}", fg='yellow' if n_wrn > 0 else ''))
            
            # add the actual errors
            if extended:
                for ty, msg in warn:
                    # TODO: the if is there, to supress color. Not yet sure if this is too colorful
                    click.secho(f"  - {msg}", fg= '' if False else ERROR_COLORS.get(ty.lower(), 'blue'))
                
                # add the warnings of the landuse file
                if par is not None:
                    click.echo(f'  PARAMETER FILE ({par.basename}):')
                    for ty, msg in par.flat_errors:
                        click.secho(f"  - {msg}", fg= '' if False else ERROR_COLORS.get(ty.lower(), 'blue'))
        
    def run(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                with contextlib.redirect_stderr(sys.stdout):
                    with contextlib.redirect_stdout(f):
                        self.__run_with_echo()
        else:
            self.__run_with_echo()

    def valid(self, warnings_as_errors: bool = True):
        """Get through all child test suites and return their state"""
        # landuse
        landuse = self.landuse is not None and self.landuse.n_errors == 0 and (warnings_as_errors and self.landuse.n_warnings == 0)

        return landuse

    def __call__(self):
        self.run()

    def __str__(self):
        return self.__call__()