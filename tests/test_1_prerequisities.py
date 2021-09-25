#!/usr/bin/env python3

import os
import pytest


@pytest.mark.incremental
class TestPrerequisities:

    def test_import_packages(self):
        '''Import required packages'''
        try:
            import sh
        except ModuleNotFoundError:
            pytest.fail(msg="Required packages (sh) are not installed")

    def test_mkdir_is_available(self):
        '''Is mkdir available'''
        try:
            from sh import mkdir
        except ImportError:
            pytest.fail(msg="mkdir command is not available")

    def test_mkdir_is_executable(self):
        '''Is mkdir executable'''
        import sh

        assert os.access(sh.mkdir._path, os.X_OK), "mkdir command is not executable"
