from typing import List, Tuple
import os
from collections import defaultdict

from catflow_validate.format import get_formatter, BaseFormatter, TextFormatter


class SoilsDef:
    """Soil definition file representation"""
    def __init__(self, filename: str, encoding: str = 'utf-8', fmt: str = 'txt', base_href: str = None):
        self.encoding = encoding

        # path settings
        self.filename = filename
        self.path = os.path.abspath(self.filename)
        self.basename = os.path.basename(self.filename)
        self.relative_path = os.path.relpath(self.path, os.path.dirname(self.filename))
        
        # container to store the soils
        self.soils = []
        self.n_soils = 0

        # container for the errors
        self.errors = defaultdict(lambda: [])
        self._did_run = False

        # formatting settings
        self.fmt = get_formatter(fmt, TextFormatter)
        if base_href is None:
            self.base_href = self.relative_path
        else:
            self.base_href = base_href

        # read in the data
        self.__read()
    
    def __line_link(self, line: int) -> str:
        return self.fmt.link(f"[L. {line}]", os.path.join(self.base_href, f"{self.relative_path}#L{line}"))

    def __read(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"The soil definition file {self.filename} could not be found.")

        # load the file
        with open(self.filename, 'rb') as fs:
            txt = fs.read().decode(encoding=self.encoding)
            self.lines = txt.splitlines()
        
        # extract the checksum
        try:
            self.n_soils = int(self.lines[0].split()[0])
        except ValueError:
            self.errors[0].append(('ValueError', f"{self.__line_link(1)} The "))
        except IndexError:
            self.errors[0].append(('ParseError', f"{self.__line_link(1)} The soil definition file is missing the checksum."))
        
        # create the soil definitions
        # TODO: This assumes that each soil is defined in exactly 6 rows
        self.soils = [SoilDef(self.lines, i + 1, self.fmt, self.base_href) for i in range(self.n_soils)]

        # update the errors
        for soil in self.soils:
            for l, errs in soil.errors.items():
                self.errors[l].extend(errs)

    @property
    def n_errors(self) -> int:
        return len([True for v in self.errors.values() for e in v if e[0].lower() != 'warning'])
    
    @property
    def n_warnings(self) -> int:
        return len([True for v in self.errors.values() for e in v if e[0].lower() == 'warning'])
    
    def valid(self, warnings_as_errors: bool = True) -> bool:
        return self.n_errors == 0 and (not warnings_as_errors or self.n_warnings == 0)



class SoilDef:
    """
    Definition for a single soil type
    """
    def __init__(self, lines: List[str], id_number: int, fmt: BaseFormatter, href: str = './'):
        self.id_number = id_number
        self._all_lines = lines
        self.fmt = fmt
        self.href = href

        # container for the errors
        self.errors = defaultdict(lambda: [])

        # check each line
        self.startline = None
        self.endline = None
        for i, line in enumerate(self._all_lines):
            if line.startswith(str(self.id_number)):
                # check if the preceding line is the first one, or the last of another soil
                if i == 1 or (i > 0 and self._all_lines[i - 1].startswith(' ')):
                    # this is a new soil
                    self.startline = i
                    self.endline = i + 6
                    break
                else:
                    continue

        # extract the lines
        if self.startline is None or self.endline is None:
            self.errors[-1].append(('ParseError', f"The soil definition {id_number} is not found."))
        else:
            self.lines = self._all_lines[self.startline:self.endline]

            # validate the file
            self.validate()

    def __line_link(self, line: int) -> str:
        return self.fmt.link(f"[L. {self.startline + line}]", f"{self.href}#L{self.startline + line}")

    def validate(self):
        """Validate """
        # get the name
        name = ' '.join(self.lines[0].split()[1:])
        # check line 2
        # TODO: 14 floats? 
        if len(self.lines[1].split()) != 14:
            self.errors[self.startline + 1].append(('ValueError', f"{self.__line_link(2)} line {self.startline + 2} of SOIL '{name}' has {len(self.lines[1].split())} values, but 14 were expected."))
        
        # line 3
        # TODO: 9 floats?
        if len(self.lines[2].split()) != 9:
            self.errors[self.startline + 2].append(('ValueError', f"{self.__line_link(3)} line {self.startline + 3} of SOIL '{name}' has {len(self.lines[2].split())} values, but 9 were expected."))

        # line 4,5,6
        # TODO 3x3 matrix with 1 whitespace of indention?
        for i in (3,4,5):
            if len(self.lines[i].split()) != 3:
                self.errors[self.startline + i].append(('ValueError', f"{self.__line_link(i + 1)} line {self.startline + i + 1} of SOIL '{name}' has {len(self.lines[i].split())} values, but 3 were expected."))
            
            if not self.lines[i].startswith(' '):
                self.errors[self.startline + i].append(('Warning', f"{self.__line_link(i + 1)} line {self.startline + i + 1} of SOIL '{name}' is not correctly indended and might cause problems."))

    @property
    def flat_errors(self) -> List[Tuple[str, str]]:
        err_list = []
        for errs in self.errors.values():
            err_list.extend(errs)
        return err_list

    @property
    def n_errors(self) -> int:
        return len([True for v in self.errors.values() for e in v if e[0].lower() != 'warning'])
    
    @property
    def n_warnings(self) -> int:
        return len([True for v in self.errors.values() for e in v if e[0].lower() == 'warning'])
    
    def valid(self, warnings_as_errors: bool = True) -> bool:
        return self.n_errors == 0 and (not warnings_as_errors or self.n_warnings == 0)
