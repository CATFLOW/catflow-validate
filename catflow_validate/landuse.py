from typing import List, Tuple, Dict
import os
from collections import defaultdict

CLASSDEF_DATA = List[Tuple[int, str, str]]
BASEPATH = '../..'


class LanduseClassDef:
    """
    Representation of a CATFLOW landuse class definition fileset
    """
    def __init__(self, filename: str, basepath: str = None):
        self.data, self.errors = self.__read(filename)
        self.filename = filename
        self.path = os.path.abspath(os.path.dirname(self.filename))
        self.basename = os.path.basename(self.filename)

        if basepath is None:
            basepath = BASEPATH
        self.catflow_basepath = os.path.abspath(os.path.join(self.path, basepath))
        
    @classmethod
    def open(cls, filename: str) -> 'LanduseClassDef':
        return LanduseClassDef(filename)
    
    def __read(self, filename: str) -> Tuple[CLASSDEF_DATA, Dict[int, Tuple[str, str]]]:
        """Open a CATFLOW laduse class definition file"""
        if not os.path.exists(filename):
            raise FileNotFoundError("The specified file could not be found.")
        
        # load the file
        with open(filename, 'r') as f:
            txt = f.read()
        
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

    def validate(self, warnings_as_errors = False) -> bool:
        # check the class definiton file
        for i, (id, name, path) in enumerate(self.data):
            # check datatype
            if not isinstance(id, int):
                self.errors[i].append(('TypeError', f"[L {i + 1}] line {i + 1} does not contain an integer landuse class definion ID."))
            
            # check if the referenced parameter file
            par_path = os.path.join(self.catflow_basepath, path)
            if not os.path.exists(par_path):
                self.errors[i].append(('ValueError', f"[L {i + 1}] line {i + 1} references {par_path}, which does not exist."))
            
            # check duplicates
            id_idx = [d[0] for d in self.data].index(id)
            if id_idx != i:
                self.errors[i].append(('DuplicateError', f"[L {i + 1}] Duplicate landuse class ID. line {i + 1} is a duplicate of line {id_idx}"))
            
            name_idx = [d[1] for d in self.data].index(name)
            if name_idx != i:
                self.errors[i].append(('Warning', f"[L {i + 1}] Duplicate landuse class NAME. line {i + 1} is a duplicate of line {id_idx}"))
        
        # Check if file is valid
        if len(self.errors) == 0:
            return True
        
        if warnings_as_errors:
            return False
        else:

            warnings = [e[0].lower() == 'warning' for v in self.errors.values() for e in v]
            return all(warnings)
            