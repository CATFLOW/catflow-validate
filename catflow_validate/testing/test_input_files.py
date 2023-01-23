import pytest
import os
import glob
import click
import warnings

from catflow_validate.landuse import LanduseClassDef
from catflow_validate.soil import SoilsDef
from catflow_validate.report import Report


@pytest.fixture
def input_folder(request):
    return request.config.getoption('input_folder', './')


@pytest.fixture
def omit_warnings(request):
    return request.config.getoption('omit_warnings', False)


def test_landuse(input_folder, omit_warnings):
    # get all files in the input folder
    files = glob.glob(os.path.join(input_folder, '**', 'landuseclass.def'), recursive=True)

    # make sure there is a file
    if len(files) == 0:
        warnings.warn("The tested input folder does not contain a landuse class definition file")
        return True

    # get the filename and validate
    landuse = LanduseClassDef(filename=files[0], basepath=input_folder, recursive=True)
    landuse.validate()

    # print out the info
    click.echo('\n##### START REPORT --->\n')
    report = Report(landuse=landuse)
    report.landuse_summary()
    report.landuse_details()
    click.echo('\n##### END  REPORT  <---\n')

    # do the test
    assert landuse.n_errors == 0
    assert landuse.n_warnings == 0 or omit_warnings


def test_soil(input_folder, omit_warnings):
    # get all files in the input folder
    files = glob.glob(os.path.join(input_folder, '**', '*_soils.def'), recursive=True)

    # make sure there is a file
    if len(files) == 0:
        warnings.warn("The tested input folder does not contain a soil definition file")
        return True
    
    # get the file and validate it
    for i, filename in enumerate(files):
        soil = SoilsDef(filename=filename, encoding='latin1')

        # print out the info
         # print out the info
        click.echo(f'\n##### START REPORT SOIL #{i + 1}--->\n')
        report = Report(soil=soil)
        report.soil_summary()
        report.soil_details()
        click.echo('\n##### END  REPORT SOIL #{i + 1}  <---\n')

        # do the test
        assert soil.n_errors == 0
        assert soil.n_warnings == 0 or omit_warnings


