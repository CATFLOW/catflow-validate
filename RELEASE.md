# CATFLOW validate

This Python package contains classes to validate input files for the CATFLOW hydrological model.
The package can be used in other Python software, as a standalone CLI script or it can be 
pulled into a input files repository and can be run as a unittest.

Install like:

```bash
pip install catflow_validate
```

Then use like:

```bash
catlidate landuse --filename path/to/landuseclass.def --recursive --extended --verbose
```