from typing import List, Tuple, Dict
import os
from collections import defaultdict

from catflow_validate.format import get_formatter, TextFormatter

CLASSDEF_DATA = List[Tuple[int, str, str]]


class LanduseClassDef:
    """
    Representation of a CATFLOW landuse class definition fileset
    """
    def __init__(self, filename: str, basepath: str = None, recursive: bool = False, encoding: str = 'latin1', fmt: str = 'txt', base_href: str = None):        
        self.encoding = encoding
        
        # read the file
        self.data, self.errors = self.__read(filename)

        # path settings
        self.filename = filename
        self.path = os.path.abspath(os.path.dirname(self.filename))
        self.basename = os.path.basename(self.filename)
        if basepath is None:
            self.catflow_basepath = os.path.abspath(os.path.join(self.path, '../../'))
        else:
            self.catflow_basepath = os.path.abspath(basepath)
        self.relative_path = os.path.relpath(self.path, self.catflow_basepath)

        # recursive
        self.recursive = recursive
        self.parameters: Dict[int, LanduseParameter] = {}

        self._did_run = False

        # formatting settings
        self.fmt = get_formatter(fmt, TextFormatter)
        if base_href is None:
            self.base_href = self.catflow_basepath
        else:
            self.base_href = base_href
        
    @classmethod
    def open(cls, filename: str) -> 'LanduseClassDef':
        return LanduseClassDef(filename)
    
    def __read(self, filename: str) -> Tuple[CLASSDEF_DATA, Dict[int, Tuple[str, str]]]:
        """Open a CATFLOW laduse class definition file"""
        if not os.path.exists(filename):
            raise FileNotFoundError("The specified file could not be found.")
        
        # load the file
        with open(filename, 'rb') as fs:
            txt = fs.read().decode(encoding=self.encoding)
        
        # create the container for the expected information
        ids, names, paths = [], [], []
        errors = defaultdict(lambda: [])

        # parse all
        for i, line in enumerate(txt.splitlines()):
            try:
                chunks = line.split()
                ids.append(int(chunks[0]))
                names.append(' '.join([str(c) for c in chunks[1:-1]]))
                paths.append(chunks[-1])
            except Exception as e:
                errors[i].append(('ParseError', str(e)))
            
        return list(zip(ids, names, paths)), errors

    def __line_link(self, line: int, path: str) -> str:
        return self.fmt.link(f"[L. {line}]", os.path.join(self.base_href, f"{path}#L{line}"))

    def validate(self, warnings_as_errors = False) -> bool:
        # check the class definiton file
        for i, (id, name, path) in enumerate(self.data):
            # check datatype
            if not isinstance(id, int):
                self.errors[i].append(('TypeError', f"{self.__line_link(i + 1, self.relative_path)} line {i + 1} does not contain an integer landuse class definion ID."))
            
            # check if the referenced parameter file
            par_path = os.path.join(self.catflow_basepath, path)
            if not os.path.exists(par_path):
                self.errors[i].append(('ValueError', f"{self.__line_link(i + 1, self.relative_path)} line {i + 1} references {par_path}, which does not exist."))
            elif self.recursive:
                par = LanduseParameter(par_path, encoding=self.encoding, relative_path=path)
                par_valid = par.validate()
                self.parameters[i] = par

                # check if the parameter file was not valid
                if not par_valid:
                    link = self.fmt.link(par.basename, os.path.join(self.base_href, path))
                    self.errors[i].append(('Warning', f"{self.__line_link(i + 1, self.relative_path)} The reference landuse parameter file {link} is not valid."))

            # check duplicates
            id_idx = [d[0] for d in self.data].index(id)
            if id_idx != i:
                self.errors[i].append(('DuplicateError', f"{self.__line_link(i + 1, self.relative_path)} Duplicate landuse class ID. Line {i + 1} is a duplicate of line {id_idx + 1}"))
            
            name_idx = [d[1] for d in self.data].index(name)
            if name_idx != i:
                self.errors[i].append(('Warning', f"{self.__line_link(i + 1, self.relative_path)} Duplicate landuse class NAME. Line {i + 1} is a duplicate of line {name_idx + 1}"))
        
        # set the run flag
        self._did_run = True

        # Check if file is valid
        if len(self.errors) == 0:
            return True
        
        if warnings_as_errors:
            return False
        else:
            warnings = [e[0].lower() == 'warning' for v in self.errors.values() for e in v]
            return all(warnings)
    
    @property
    def n_errors(self) -> int:
        if not self._did_run:
            self.validate()
        return len([True for v in self.errors.values() for e in v if e[0].lower() != 'warning'])

    @property
    def n_warnings(self) -> int:
        if not self._did_run:
            self.validate()
        return len([True for v in self.errors.values() for e in v if e[0].lower() == 'warning'])

    def valid(self, warnings_as_errors: bool = True) -> bool:
        return self.n_errors == 0 and (not warnings_as_errors or self.n_warnings == 0)

class LanduseParameter:
    def __init__(self, filename: str, relative_path: str = None, encoding: str = 'latin1', fmt: str = 'txt', base_href: str = None):
        self.encoding = encoding
        self.filename = filename
        self.basename = os.path.basename(filename)
        self.relative_path = os.path.dirname(self.filename) if relative_path is None else relative_path
        self.errors = defaultdict(lambda: [])
        
        # TODO: ask back to Jan: are these really hardcoded into CATFLOW?
        # also: is the order fixed?
        self.VALID_HEADER_NAMES = ['KST', 'MAK', 'BFI', 'BBG', 'TWU', 'PFH', 'PALB', 'RSTMIN', 'WP_BFW', 'F_BFW']
        self.lines = []

        # formatting settings
        self.fmt = get_formatter(fmt, TextFormatter)
        if base_href is None:
            self.base_href = self.relative_path
        else:
            self.base_href = base_href

        self.__read()

    def __read(self):
        # read in
        with open(self.filename, 'rb') as fs:
            lines = fs.read().decode(encoding=self.encoding).splitlines()
        
        # parse the header:
        try:
            h_chunks = lines[0].split()
            self.n_cols = int(h_chunks[0])
            self.header_names = []
            for c  in h_chunks[1:]:
                if c.startswith('%'):
                    break
                self.header_names.append(str(c))

        except Exception as e:
            self.errors[0].append('ParseError', f"{self.__line_link(1)} {str(e)}")

        # parse the file
        for i, line in enumerate(lines[1:], start=1):
            # remove comments
            try:
                chunks = []
                for c in line.split():
                    if c.startswith('%'):
                        break
                    chunks.append(float(c))
                self.lines.append(chunks)
            except Exception as e:
                self.errors[i].append(('ParseError', f"{self.__line_link(i + 1)} {str(e)}"))

    def __line_link(self, line: int) -> str:
        return self.fmt.link(f"[L. {line}]", os.path.join(self.base_href, f"{self.relative_path}#L{line}"))

    def validate(self) -> bool:
        """Validate the parameter file"""
        # check the number of columns
        if self.n_cols != len(self.header_names):
            self.errors[0].append(('ParseError', f"{self.__line_link(1)} {self.basename} defines {self.n_cols} landuse attribute columns, but {len(self.header_names)} are found."))
        
        # check the header names
        for name in self.header_names:
            if name not in self.VALID_HEADER_NAMES:
                self.errors[0].append(('ValueError', f"{self.__line_link(1)} The landuse attribute '{name}' is not a valid name."))
        
        # check the multiplicator line and first date:
        if int(self.lines[0][0]) != 0:
            self.errors[1].append(('ValueError', f"{self.__line_link(2)} The multiplicator line is missing."))
        if int(self.lines[1][0]) != 1:
            self.errors[1].append(('ValueError', f"{self.__line_link(2)} The date ranges have to start with 1. Jan, DOY := 1."))
        
        # check the lines
        for i, line in enumerate(self.lines[1:], start=2):
            # check the day of the year
            if line[0] < 0 or line[0] > 366:
                self.errors[i].append(('ValueError', f"{self.__line_link(i + 1)} line {i + 1} contains an invalid day of the year. (1. <= DOY <= 366.)"))
            
            # DOY has to be increasing
            if int(line[0]) <= int(self.lines[i - 2][0]):
                self.errors[i].append(('ValueError', f"{self.__line_link(i + 1)} line {i + 1} contains a non-increasing day of the year."))
            
            # check all others
            # TODO: The only constrain I am aware of is that these numbers have to be positive
            for j, c in enumerate(line[1:], start=1):
                if float(c) < 0:
                    self.errors[i].append(('ValueError', f"{self.__line_link(i + 1)} line {i + 1} column {j + 1} contains a negative parameter"))
        
        return len(self.errors.keys()) == 0     

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

