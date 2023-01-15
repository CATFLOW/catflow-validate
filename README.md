# catflow-validate

This Python package contains classes to validate input files for the CATFLOW hydrological model.
The package can be used in other Python software, as a standalone CLI script or it can be 
pulled into a input files repository and can be run as a unittest.

## Install

### PyPI

```bash
pip install catflow_validate
```

## Use

Catflow-validate can be used as a python library or a command line interface. 

```
Usage: catlidate landuse [OPTIONS]

Options:
  -f, --filename TEXT  Filename for the landuse class definition file.
  -r, --recursive      Validate all referenced landuse class parameter files
                       recursively
  -v, --verbose        Print out verbose information on errors and warnings.
  -e, --extended       Print an extended report.
  --help               Show this message and exit.
```