from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('catflow_validate/__version__.py') as f:
        loc = dict()
        exec(f.read(), loc, loc)
        return loc['__version__']


def dependencies():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name="catflow_validate",
    version=version(),
    author="Mirko Mälicke",
    author_email="mirko.maelicke@kit.edu",
    descirption="Valdiation script tools for CATFLOW input files",
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=dependencies(),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'catlidate = catflow_validate.cli:cli'
        ]
    }
)
