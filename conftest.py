def pytest_addoption(parser):
    parser.addoption("--input-folder", "-I", action="store", help="CATFLOW input folder location")
    parser.addoption("--suppress-warnings", action="store_true", default=False, help="Ignore warnings. Otherwise warnings are treated like errors.")