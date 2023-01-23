import os
import subprocess

from json2args import get_parameter


# parse the parameters
kwargs = get_parameter()

# get the toolname
toolname = os.environ.get('TOOL_RUN', 'catlidate').lower()

# checkout the tool
if toolname == 'catlidate':
    fmt = kwargs.get('format', 'md')
    inp = kwargs.get('input_folder', '/in/')
    subprocess.run(f"catlidate report --input-folder {inp} --fmt {fmt}>> /out/Report.{fmt}", shell=True)

else:
    raise AttributeError(f"The tool '{toolname}' is not available.\n")
