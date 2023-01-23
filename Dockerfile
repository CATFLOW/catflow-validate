FROM python:3.10

# install the toolbox tools
RUN pip install json2args

# Install the latest version from PyPI
RUN pip install catflow_validate

# create the tool input structure
RUN mkdir /in
RUN mkdir /out
RUN mkdir /src
COPY ./src /src

WORKDIR /src
CMD ["python", "run.py"]