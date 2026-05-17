import pytest
import s2mflow

def test_package_import():
    assert s2mflow is not None

@pytest.mark.xfail(reason="Deliberate failure to verify pytest assertion framework behavior.")
def test_expected_fail():
    assert False