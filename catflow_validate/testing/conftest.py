import pytest

def pytest_addoption(parser):
    parser.addoption("--input-folder", "-I", action="store", help="CATFLOW input folder location")
    parser.addoption("--suppress-warnings", '-W', action="store_true", default=False, help="Ignore warnings. Otherwise warnings are treated like errors.")


# def pytest_generate_tests(metafunc):
#     input_folder = metafunc.config.getoption('input_folder', './')
#     omit_warnings = metafunc.config.getoption('suppress_warnings', False)
    
#     # run the tests
#     metafunc.parametrize(["input_folder", "omit_warnings"], [[input_folder], [omit_warnings]])

@pytest.fixture
def input_folder(request):
    return request.config.getoption('input_folder', './')

@pytest.fixture
def omit_warnings(request):
    return request.config.getoption('omit_warnings', False)