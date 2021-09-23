#!/usr/bin/env python3

import pytest


@pytest.mark.incremental
class TestPrerequisities:

    def test_import_sh(self):
        '''Import sh package'''
        try:
            import sh
        except ModuleNotFoundError:
            pytest.fail(msg="Package 'sh' is not installed")

    def test_mkdir_is_available(self):
        '''Is mkdir available'''
        try:
            from sh import mkdir
        except ImportError:
            pytest.fail(msg="mkdir command is not available")

    def test_mkdir_is_executable(self):
        '''Is mkdir executable'''
        from sh import mkdir
        try:
            mkdir('--version')
        except:
            pytest.fail(msg="mkdir command is not executable")


