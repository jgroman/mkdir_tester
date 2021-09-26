#!/usr/bin/env python3

import os
import pytest


@pytest.mark.incremental
class TestPrerequisities:
    """
    Class for grouping tests for test suite prerequisities.
    """

    def test_import_packages(self):
        '''Selfcheck: Import required packages'''
        try:
            import sh
        except ModuleNotFoundError:
            pytest.fail(msg="Required package 'sh' is not installed")

    def test_mkdir_is_available(self):
        '''Selfcheck: mkdir is available'''
        try:
            from sh import mkdir
        except ImportError:
            pytest.fail(msg="mkdir command is not available")

    def test_mkdir_is_executable(self):
        '''Selfcheck: mkdir is executable'''
        import sh

        assert os.access(sh.mkdir._path, os.X_OK), "mkdir command is not executable"
