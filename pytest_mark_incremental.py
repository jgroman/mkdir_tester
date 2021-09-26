#!/usr/bin/env python3
'''
pytest incremental testing setup plugin
'''

# Adopted from
# https://docs.pytest.org/en/latest/example/simple.html#incremental-testing-test-steps

import pytest
from typing import Dict, Tuple

# store history of failures per test class name and per index in parametrize
# (if parametrize used)
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed
            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test (if parametrize is used
            # in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test (if parametrize is used
            # in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the first test function to fail for
            # this class name and index
            test_name = _test_failed_incremental[cls_name].get(
                parametrize_index, None)
            # if name found, test has failed for the combination of class name & test name
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))


if __name__ == "__main__":
    print("""pytest_mark_incremental.py pytest plugin

This script should not be run directly but rather configured as pytest plugin
and loaded using following directive in conftest.py configuration file:

pytest_plugins = ("pytest_mark_incremental")

Also please remember to add custom 'incremental' marker definition to pytest.ini:

[pytest]
markers =
    incremental: Enables forced test skipping if previous step failed

    """)
