import os
import glob
import click

from catflow_validate.landuse import LanduseClassDef
from catflow_validate.report import Report
from catflow_validate.testing.conftest import input_folder, omit_warnings


def test_landuse(input_folder, omit_warnings):
    # get all files in the input folder
    files = glob.glob(os.path.join(input_folder, '**', 'landuseclass.def'), recursive=True)

    # make sure there is a file
    assert len(files) > 0

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
