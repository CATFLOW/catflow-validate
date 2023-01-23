import sys
import contextlib

import click
from click import style, echo

from catflow_validate import __version__
from catflow_validate.format import get_formatter, TextFormatter
from catflow_validate.landuse import LanduseClassDef
from catflow_validate.soil import SoilsDef

ERROR_COLORS = dict(
    warning='yellow',
    duplicateerror='bright_magenta',
    parseerror='red',
    typeerror='magenta',
    valueerror='magenta'
)

class Report:
    def __init__(self, landuse: LanduseClassDef = None, soil: SoilsDef = None, output_file: str = None, fmt: str = 'txt'):
        self.landuse = landuse
        self.soil = soil
        self.output_file = output_file
        self.fmt = get_formatter(fmt, TextFormatter)

    def __run_with_echo(self):
        # header
        echo(self.fmt.heading('CATFLOW input file validation report', level=1))
        echo(f"Catlidate version: {__version__}")
        echo('')

        # overview
        lines = self.landuse_summary()
        lines.extend(self.soil_summary())
        self.echo_summary(lines)
        echo('')

        # details
        self.landuse_details()
        echo(' ')
        self.soil_details()

    def echo_summary(self, lines: list):
 # create the header
        header = ['Object', 'checked', 'errors', 'warnings']
        message = self.fmt.tabular(lines, header)
        echo(message)

    def landuse_summary(self):
        """Print single line summary"""
        # collect the summary lines
        lines = []
        
        if self.landuse is None:
            lines.append(['Landuse classes', 'not checked', 'NA', 'NA'])
        else:
            msg = [
                style('Landuse classes  ', fg='green' if self.landuse.valid() else 'red'),
                style('valid  ' if self.landuse.valid() else 'invalid', fg='green' if self.landuse.valid() else 'red'),
                style(self.landuse.n_errors, fg='' if self.landuse.n_errors == 0 else 'red'),
                style(self.landuse.n_warnings, fg='' if self.landuse.n_warnings == 0 else 'yellow'),
            ]
            lines.append(msg)

            # append information about all landuse parameter files
            for cl, lp in self.landuse.parameters.items():
                valid = lp.n_errors + lp.n_warnings == 0
                
                # format the name
                name = self.landuse.data[cl][1]
                name = f"{name[:20] if len(name) > 20 else name[:17]}{'...' if len(name) > 20 else ''}"
                if len(name) < 20:
                    name = name.ljust(20)
                
                # build the line
                msg = [
                    style(name, fg='green' if valid else 'red'),
                    style('valid  ' if valid else 'invalid', fg='green' if valid else 'red'),
                    style(lp.n_errors, fg='red' if lp.n_errors > 0 else ''),
                    style(lp.n_warnings, fg='yellow' if lp.n_warnings > 0 else '')
                ]
                lines.append(msg)
            
            return lines
    
    def landuse_details(self, extended: bool = True):
        # check if there are invalid landuse classes
        n_inval = len([1 for w in self.landuse.errors.values() if len(w) > 0])
        
        # print extended header
        if extended:
            echo(self.fmt.heading('Landuse-class definitions', 2))
            echo('')
            echo(f"PATH:             {self.landuse.path}")
            echo(f"NAME:             {self.landuse.basename}")
            echo(f"Total classes:    {len(self.landuse.data)}")
            click.secho(f"Invalid classes:  {n_inval}", fg='red' if n_inval > 0 else '')
            echo('')
        # without errors, don't give details about errors
        if n_inval == 0:
            return
        
        # there are errors, so print them
        echo(self.fmt.heading('Landuse Error Details', level=3))
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

    def soil_summary(self):
        """Print single line summary""" 
        # collect the summary lines
        lines = []

        # check if a soil files was added to the report
        if self.soil is None:
            lines.append(['SOIL classes', 'not checked', 'NA', 'NA'])
        else:
            msg = [
                style('SOIL classes', fg='green' if self.soil.valid() else 'red'),
                style('valid  ' if self.soil.valid() else 'invalid', fg='green' if self.soil.valid() else 'red'),
                style(self.soil.n_errors, fg='' if self.soil.n_errors == 0 else 'red'),
                style(self.soil.n_warnings, fg='' if self.soil.n_warnings == 0 else 'yellow')
            ]
            lines.append(msg)
        
        return lines


    def soil_details(self, extended: bool = True):
        # print an extended header
        if extended:
            echo(self.fmt.heading('SOIL class definitions', 2))
            echo('')
            echo(f"PATH:           {self.soil.path}")
            echo(f"NAME:           {self.soil.basename}")
            echo(f"Total soils:    {self.soil.n_soils}")
            inval_cls = sum([1 for s in self.soil.soils if not s.valid()])
            click.secho(f"Invalid soils:  {inval_cls}", fg='red' if inval_cls > 0 else '')
        
        # check if there are errors at all
        if self.soil.valid():
            return
        
        # otherwise there are errors
        echo(self.fmt.heading('Soil Error Details'))
        
        # check if there are overall errors
        for l in (-1, 1):
            for cl, warn in self.soil.errors.get(l, []):
                click.secho(f"+ {warn}", fg='' if False else ERROR_COLORS.get(cl.lower(), 'blue'))
        
        # append all soils
        for s in self.soil.soils:
            if s.valid():
                continue
            click.secho(f"+ SOIL: {s.lines[0].split()[-1]}", fg='red' if s.n_errors > 0 else 'yellow')
            for ty, warn in s.flat_errors:
                click.secho(f"  - {warn}", fg='' if False else ERROR_COLORS.get(ty.lower(), 'blue'))
        
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
        soil = self.soil is not None and self.soil.n_errors == 0 and (warnings_as_errors and self.soil.n_warnings == 0)

        return landuse and soil

    def __call__(self):
        self.run()

    def __str__(self):
        return self.__call__()